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
            impersonated_user = User.objects.get(pk = impersonated_pk)
        except ObjectDoesNotExist:
            # If the user does not exist, we are done
            return self.get_response(request)
        # If the user is permitted to impersonate the requested user, modify the request
        # If not, leave it as it is
        if app_settings.IMPERSONATE_IS_PERMITTED(request.user, impersonated_user):
            # If they are, modify the request to reflect the impersonation
            request.impersonator = request.user
            request.user = impersonated_user
        return self.get_response(request)
