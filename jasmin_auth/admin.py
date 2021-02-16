from django.conf import settings as django_settings
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect, render, resolve_url
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from .settings import app_settings


class AdminSite(admin.AdminSite):
    enable_nav_sidebar = False

    @never_cache
    def login(self, request, extra_context = None):
        if request.method == 'GET' and self.has_permission(request):
            # The user is already authenticated, so redirect to admin index
            index_path = reverse('admin:index', current_app = self.name)
            return redirect(index_path)

        # If the user is already authenticated but doesn't have permission, show an error
        if request.user.is_authenticated and not self.has_permission(request):
            context = {
                **self.each_context(request),
                'title': _('Permission denied'),
                'app_path': request.get_full_path(),
                'username': request.user.get_username(),
            }
            context.update(extra_context or {})
            return render(request, 'admin/permission_denied.html', context)

        # Work out where we will be redirecting users on successful login
        if REDIRECT_FIELD_NAME in request.GET:
            next_url = request.GET[REDIRECT_FIELD_NAME]
        else:
            next_url = reverse('admin:index', current_app = self.name)
        # Redirect the user to the configured login url with the next URL as a query param
        login_url = resolve_url(django_settings.LOGIN_URL)
        params = urlencode({ REDIRECT_FIELD_NAME: next_url })
        return redirect(f'{login_url}?{params}')
