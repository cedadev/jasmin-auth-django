from django.conf import settings as django_settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.shortcuts import redirect, render, resolve_url
from django.urls import reverse

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import OAuth2Error

from .settings import app_settings


def login(request):
    """
    Starts the OAuth 2.0 login flow.
    """
    # NOTE: Even if the user is already authenticated, they will be sent round the
    #       redirect loop and re-authenticated
    #       This allows for the case where a user has signed out of the identity provider
    #       in order to sign in using a different account
    # Store the next url in the session if given
    if REDIRECT_FIELD_NAME in request.GET:
        request.session[app_settings.NEXT_URL_SESSION_KEY] = request.GET[REDIRECT_FIELD_NAME]
    # Initialise the OAuth session
    provider = OAuth2Session(
        app_settings.CLIENT_ID,
        redirect_uri = request.build_absolute_uri(reverse('jasmin_auth:callback')),
        scope = ' '.join(app_settings.SCOPES),
    )
    # Get the redirect URL and state
    auth_url, state = provider.authorization_url(app_settings.AUTHORIZE_URL)
    # Store the state for later
    request.session[app_settings.STATE_SESSION_KEY] = state
    return redirect(auth_url)


def callback(request):
    """
    Handles the OAuth 2.0 callback.
    """
    # Initialise the OAuth session
    provider = OAuth2Session(
        app_settings.CLIENT_ID,
        redirect_uri = request.build_absolute_uri(reverse('jasmin_auth:callback')),
        scope = ' '.join(app_settings.SCOPES),
        state = request.session.pop(app_settings.STATE_SESSION_KEY, None),
    )
    try:
        token = provider.fetch_token(
            app_settings.ACCESS_TOKEN_URL,
            client_secret = app_settings.CLIENT_SECRET,
            authorization_response = request.build_absolute_uri(),
            verify = app_settings.VERIFY_SSL
        )
    except OAuth2Error as exc:
        # If there is an OAuth error, show the error page
        return render(request, 'jasmin_auth/oauth_error.html', {
            'error': exc.error,
            'error_description': app_settings.ERROR_MESSAGES.get(
                exc.error,
                exc.description or app_settings.DEFAULT_ERROR_MESSAGE
            )
        })
    else:
        # If a token is obtained successfully, retrieve the profile and create a local user
        profile = provider.get(app_settings.PROFILE_URL).json()
        # The function to create or update a user is a setting
        user = app_settings.CREATE_OR_UPDATE_USER_FUNC(profile)
        # Log the user in.
        # If the backend to use is specified in settings use that one (should be a dotted
        # class path to the backend). Otherwise just use whatever the default one is.
        if app_settings.LOGIN_BACKEND:
          auth_login(request, user, app_settings.LOGIN_BACKEND)
        else:
          auth_login(request, user)
        # Redirect to the specified URL
        next_url = request.session.pop(
            app_settings.NEXT_URL_SESSION_KEY,
            resolve_url(django_settings.LOGIN_REDIRECT_URL)
        )
        return redirect(next_url)
