import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.urls import resolve

from .settings import app_settings


def create_or_update_user(profile):
    """
    Creates or updates a user from the given profile using the
    mappings configured in the settings.
    """
    UserModel = get_user_model()
    # Extract the username from the profile - this should always be present
    username = profile[app_settings.PROFILE_USERNAME_KEY]
    # Map the other fields as specified in the settings
    user_fields = {
        user_field: profile.get(profile_key)
        for profile_key, user_field in app_settings.PROFILE_USER_MAPPING.items()
    }
    # Create or update the user
    # We don't use get_or_create because we want to use create_user in the case
    # where the user does not exist
    try:
        user = UserModel.objects.get(username = username)
        for field, value in user_fields.items():
            setattr(user, field, value)
        user.save()
    except ObjectDoesNotExist:
        user = UserModel.objects.create_user(username, **user_fields)
    return user


def impersonation_permitted_user(impersonator, impersonatee):
    """
    Tests if the impersonator is allowed to impersonate the impersonatee.
    """
    # No impersonation is permitted by non-staff
    if not impersonator.is_staff:
        return False
    # By default, superusers are allowed to impersonate any other user
    if impersonator.is_superuser:
        return True
    # Other staff can impersonate any non-staff user
    if not impersonatee.is_superuser and not impersonatee.is_staff:
        return True
    # No other impersonation is permitted
    return False


def impersonation_permitted_request(request):
    """
    Tests if impersonation is allowed for the given request.
    """
    # First, see if the request path matches any of the excluded paths
    for pattern in app_settings.IMPERSONATE_DISABLED_PATTERNS:
        if re.search(pattern, request.path_info) is not None:
            return False
    # Then check if the view has disabled impersonation using the decorator
    view_func, *notused = resolve(request.path_info, getattr(request, 'urlconf', None))
    return not getattr(view_func, 'no_impersonation', False)
