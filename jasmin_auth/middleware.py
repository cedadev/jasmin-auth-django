from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from .settings import app_settings


class ImpersonateMiddleware:
    """
    Middleware that allows a user with sufficient permissions to impersonate
    another user.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set default values for impersonator and impersonatee
        request.impersonator = None
        # Get the impersonated user pk from the session
        impersonated_pk = request.session.get(app_settings.IMPERSONATE_SESSION_KEY)
        # If the request is not impersonated, we are done
        if not impersonated_pk:
            return self.get_response(request)
        # If the user is not authenticated, we are done
        if not request.user or not request.user.is_authenticated:
            return self.get_response(request)
        # Next, try to get the user that is being impersonated
        User = get_user_model()
        try:
            impersonatee = User.objects.get(pk = impersonated_pk)
        except ObjectDoesNotExist:
            # If the user does not exist, remove the key from the session so we don't
            # try again next time
            del request.session[app_settings.IMPERSONATE_SESSION_KEY]
            # Then we are done
            return self.get_response(request)
        # If the user is not permitted to impersonate the requested user, we are done
        if not app_settings.IMPERSONATE_IS_PERMITTED_USER(request.user, impersonatee):
            return self.get_response(request)
        # If we get to here then the impersonation would be permitted, however impersonation
        # might be disabled for the specific request
        if app_settings.IMPERSONATE_IS_PERMITTED_REQUEST(request):
            # In the case where impersonation is permitted, update the user for the request
            request.impersonator = request.user
            request.user = impersonatee
        else:
            # In the case where impersonation is disabled for the request, we still
            # acknowledge that it could have happened by setting impersonatee
            request.impersonatee = impersonatee
        return self.get_response(request)
