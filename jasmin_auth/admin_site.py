from functools import wraps

from django.conf import settings as django_settings
from django.contrib import admin, messages
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, resolve_url
from django.template.loader import render_to_string
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode, url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from .decorators import no_impersonation
from .settings import app_settings
from .signals import impersonation_started, impersonation_ended


class AdminSite(admin.AdminSite):
    enable_nav_sidebar = False

    @never_cache
    @method_decorator(no_impersonation)
    def login(self, request, extra_context = None):
        """
        Overrides login view to redirect to the standard login view.

        If the authenticated user is not authorised to view the admin then it will show a
        permission denied page.
        """
        # Work out where we will be redirecting users on successful login
        if REDIRECT_FIELD_NAME in request.GET:
            next_url = request.GET[REDIRECT_FIELD_NAME]
        else:
            next_url = reverse('admin:index', current_app = self.name)
        # If the user is already authenticated, redirect them where they want to go
        if request.method == 'GET' and self.has_permission(request):
            return redirect(next_url)
        # If the user is authenticated but doesn't have permission to access the admin, show an error
        if request.user.is_authenticated and not self.has_permission(request):
            context = {
                **self.each_context(request),
                'title': _('Permission denied'),
                'app_path': request.get_full_path(),
                'username': request.user.get_username(),
            }
            context.update(extra_context or {})
            return render(request, 'admin/permission_denied.html', context)
        # Redirect the user to the configured login url with the next URL as a query param
        login_url = resolve_url(django_settings.LOGIN_URL)
        params = urlencode({ REDIRECT_FIELD_NAME: next_url })
        return redirect(f'{login_url}?{params}')

    def get_urls(self):
        """
        Override get_urls to register our additional urls.
        """
        def wrap(view, cacheable = False):
            @wraps(view)
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            wrapper.admin_site = self
            return wrapper

        urls = super().get_urls()[::-1]
        # We need to insert our views before the catch all view
        return (
            urls[:-1] +
            [
                path('impersonate/<path:pk>/', wrap(self.impersonate), name = 'impersonate'),
                path('impersonate_end/', wrap(self.impersonate_end), name = 'impersonate_end'),
            ] +
            urls[-1:]
        )

    def admin_view(self, view, cacheable = False):
        """
        Override admin_view to unwind any active impersonation when inside the admin.
        """
        return no_impersonation(super().admin_view(view, cacheable))

    def redirect_to_referer(self, request):
        """
        Redirects the user back to where they come from, unless it is unsafe.
        """
        referer = request.META.get('HTTP_REFERER', '')
        referer_is_safe = url_has_allowed_host_and_scheme(
            url = referer,
            allowed_hosts = { request.get_host() },
            require_https = request.is_secure()
        )
        if referer_is_safe:
            next_url = resolve_url(referer)
        else:
            next_url = reverse('admin:index', current_app = self.name)
        return redirect(next_url)

    @never_cache
    def impersonate(self, request, pk, extra_context = None):
        """
        View to start impersonating a user.
        """
        # Try to find the user given by the pk
        User = get_user_model()
        try:
            impersonatee = User.objects.get(pk = pk)
        except ObjectDoesNotExist:
            # If the user does not exist, set a message
            messages.add_message(
                request,
                messages.WARNING,
                'User with ID "{}" doesn\'t exist.'.format(pk)
            )
        else:
            # Next, test if the authenticated user is allowed to impersonate the given user
            if app_settings.IMPERSONATE_IS_PERMITTED(request.user, impersonatee):
                # If the impersonation is allowed, set the session key
                # Get the previous setting of the key first as we only want to fire the
                # signal when the key changes
                previous_pk = request.session.get(app_settings.IMPERSONATE_SESSION_KEY)
                request.session[app_settings.IMPERSONATE_SESSION_KEY] = pk
                # Dispatch the signal to indicate that an impersonation has started
                if previous_pk != pk:
                    impersonation_started.send(
                        impersonatee.__class__,
                        impersonator = request.user,
                        impersonatee = impersonatee
                    )
            else:
                # If the impersonation is not allowed, set a message
                messages.add_message(
                    request,
                    messages.ERROR,
                    'You are not allowed to impersonate user "{}".'.format(impersonatee)
                )
        # Redirect the user back where they came from
        return self.redirect_to_referer(request)

    @never_cache
    def impersonate_end(self, request, extra_context = None):
        """
        View to end impersonating a user.
        """
        # Remove the key from the session
        if app_settings.IMPERSONATE_SESSION_KEY in request.session:
            del request.session[app_settings.IMPERSONATE_SESSION_KEY]
        # If there is an impersonation active on this request, dispatch the signal
        if request.impersonatee:
            impersonation_ended.send(
                request.user.__class__,
                impersonator = request.user,
                impersonatee = request.impersonatee
            )
        return self.redirect_to_referer(request)
