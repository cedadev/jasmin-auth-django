from settings_object.appsettings import (
    SettingsObject,
    Setting,
    ImportStringSetting,
    MergedDictSetting
)


class AppSettings(SettingsObject):
    """
    Settings for the ``jasmin_oauth_client`` application.
    """
    #: The authorize URL to use
    AUTHORIZE_URL = Setting(default = 'https://accounts.jasmin.ac.uk/oauth/authorize/')
    #: The token URL to use to obtain an access token
    ACCESS_TOKEN_URL = Setting(default = 'https://accounts.jasmin.ac.uk/oauth/token/')
    #: The URL to use to obtain profile information
    PROFILE_URL = Setting(default = 'https://accounts.jasmin.ac.uk/api/profile/')
    #: Indicates whether to perform verification of the SSL certificate
    #: This should be ``True`` in production
    VERIFY_SSL = Setting(default = True)
    #: The oauth client id
    CLIENT_ID = Setting()
    #: The oauth client secret
    CLIENT_SECRET = Setting()
    #: The scopes to ask for
    SCOPES = Setting(default = lambda s: (s.PROFILE_URL, ))
    #: The session key to use for storing the oauth state parameter
    STATE_SESSION_KEY = Setting(default = 'jasmin_auth_state')
    #: The session key to use for the login redirect url
    NEXT_URL_SESSION_KEY = Setting(default = 'jasmin_auth_next_url')
    #: Function that creates or updates a user from the profile result
    CREATE_OR_UPDATE_USER_FUNC = ImportStringSetting(
        default = 'jasmin_auth.helpers.create_or_update_user'
    )
    #: The key in the profile to use as the username
    #: Used by the default CREATE_OR_UPDATE_USER_FUNC
    PROFILE_USERNAME_KEY = Setting(default = 'username')
    #: A mapping of profile keys to user fields
    #: Used by the default CREATE_OR_UPDATE_USER_FUNC
    PROFILE_USER_MAPPING = Setting(default = dict(
        first_name = "first_name",
        last_name = "last_name",
        email = "email",
    ))
    #: The error message for each error code
    ERROR_MESSAGES = MergedDictSetting(defaults = dict(
        access_denied = 'You did not grant the required access.',
    ))
    #: The default error message if the code is not present
    DEFAULT_ERROR_MESSAGE = Setting(
        default = 'An error occurred during authentication - please try again.'
    )

    #: Session key to use for storing the impersonated user pk
    IMPERSONATE_SESSION_KEY = Setting(default = 'jasmin_auth_impersonate')
    #: Function that tests if impersonation is permitted for an impersonator/impersonatee pair
    IMPERSONATE_IS_PERMITTED_USER = ImportStringSetting(
        default = 'jasmin_auth.helpers.impersonation_permitted_user'
    )
    #: Function that tests if impersonation is permitted for a particular request
    IMPERSONATE_IS_PERMITTED_REQUEST = ImportStringSetting(
        default = 'jasmin_auth.helpers.impersonation_permitted_request'
    )
    #: Iterable of patterns for which impersonation is disabled
    IMPERSONATE_DISABLED_PATTERNS = Setting(default = ('^/admin', ))

    # The backend to use to log the user in as.
    # A class path e.g. django.contrib.auth.backends.ModelBackend
    LOGIN_BACKEND = Setting(default = '')


app_settings = AppSettings('JASMIN_AUTH')
