from django.contrib import admin
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.views.generic.base import TemplateView

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import OAuth2Error

from .settings import app_settings


class AdminSite(admin.AdminSite):
    def user_has_permission(self, user):
        return user.is_active and user.is_staff

    def has_permission(self, request):
        return self.user_has_permission(request.user)

    @never_cache
    def login(self, request, extra_context = None):
        # NOTE: Even if the user is already authenticated, they will be sent round the
        #       redirect loop and re-authenticated
        #       This allows for the case where a user has signed out of the JASMIN Accounts
        #       Portal in order to sign in as someone else
        # Work out where we will be redirecting users on successful login
        if REDIRECT_FIELD_NAME in request.GET:
            next_url = request.GET[REDIRECT_FIELD_NAME]
        elif app_settings.NEXT_URL_SESSION_KEY in request.session:
            next_url = request.session[app_settings.NEXT_URL_SESSION_KEY]
        else:
            next_url = reverse('admin:index', current_app = self.name)
        # Update the session to preserve the next URL throughout the login process
        request.session[app_settings.NEXT_URL_SESSION_KEY] = next_url
        # Start the template context
        context = dict(
            self.each_context(request),
            title = _('Log in'),
            login_url = reverse('admin:login', current_app = self.name)
        )
        # Initialise the OAuth session
        provider = OAuth2Session(
            app_settings.CLIENT_ID,
            redirect_uri = request.build_absolute_uri(context['login_url']),
            scope = ' '.join(app_settings.SCOPES),
            # Initialise the session with any previously saved state
            state = request.session.pop(app_settings.STATE_SESSION_KEY, None)
        )
        # If there is a state parameter, attempt to complete the login process
        if 'state' in request.GET:
            # Try to exchange the authorisation grant for a token
            try:
                token = provider.fetch_token(
                    app_settings.ACCESS_TOKEN_URL,
                    client_secret = app_settings.CLIENT_SECRET,
                    authorization_response = request.build_absolute_uri(),
                    verify = app_settings.VERIFY_SSL
                )
            except OAuth2Error as exc:
                # If there is an OAuth error, show the error page
                context.update(
                    error = exc.error,
                    error_description = app_settings.ERROR_MESSAGES.get(
                        exc.error,
                        exc.description or app_settings.DEFAULT_ERROR_MESSAGE
                    )
                )
                return render(request, 'admin/oauth_error.html', context)
            else:
                # After a successful remote authentication, we no longer need to keep the next URL in the session
                del request.session[app_settings.NEXT_URL_SESSION_KEY]
                # If a token is obtained successfully, retrieve the profile and create a local user
                profile = provider.get(app_settings.PROFILE_URL).json()
                username = profile.pop('username')
                User = get_user_model()
                try:
                    user = User.objects.get(username = username)
                    user.first_name = profile.get('first_name')
                    user.last_name = profile.get('last_name')
                    user.email = profile.get('email')
                    user.save()
                except ObjectDoesNotExist:
                    user = User.objects.create_user(
                        username,
                        first_name = profile.get('first_name'),
                        last_name = profile.get('last_name'),
                        email = profile.get('email')
                    )
                # If the user has permission to access the admin site, log them in
                if self.user_has_permission(user):
                    auth_login(request, user)
                    return redirect(next_url)
                # If not, show an error page
                else:
                    context.update(username = username)
                    return render(request, 'admin/permission_denied.html', context)
        # If there is no state parameter, kick off an authentication by redirecting
        else:
            auth_url, state = provider.authorization_url(app_settings.AUTHORIZE_URL)
            # Store the state for later
            request.session[app_settings.STATE_SESSION_KEY] = state
            return redirect(auth_url)
