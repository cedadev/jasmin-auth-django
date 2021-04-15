# jasmin-auth-django

This packages provides views for authenticating users for a Django site using JASMIN
accounts. This includes a custom admin site that allows the admin to use the same
authentication views as the rest of the site rather than specialised admin login views.

It also includes functionality to allow staff users to impersonate other users on the
site. The impersonation does not apply in the admin.

## Installation

Install directly from GitHub using `pip`:

```sh
pip install git+https://github.com/cedadev/jasmin-auth-django.git#egg=jasmin_auth_django
```

## Usage

In order to use `jasmin-auth-django`, you must have a client ID and secret for an OAuth2
application that is registered with the JASMIN Accounts Portal. The application must be permitted
to obtain tokens with the profile scope. To allow for transparent authentication, the application
should also have "Skip authorization" set - not doing this will result in the authorization page
being shown every time a user authenticates with your service.

To configure your site to use JASMIN accounts for authentication, you need to modify the Django
settings:

```py
# Add the jasmin_auth apps at the top of the installed apps
INSTALLED_APPS = [
    'jasmin_auth',
    # This REPLACES django.contrib.admin
    'jasmin_auth.apps.AdminConfig',
    # ... other apps ...
]

# To enable impersonation, you must install the impersonation middleware
# It should come after all authentication-related middleware
MIDDLEWARE = [
    # ... other middleware ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # ... other middleware ...
    'jasmin_auth.middleware.ImpersonateMiddleware',
]

# Configure the OAuth application details
JASMIN_AUTH = {
    'CLIENT_ID': '<oauth client id>',
    'CLIENT_SECRET': '<oauth client secret>',
}

# Set the login URL to use
LOGIN_URL = 'jasmin_auth:login'
```

Upon restarting your application, your Django site will be able to authenticate using JASMIN
accounts, and any user flagged as staff will be able to impersonate other users on the site.

## Session expiry

The way the authentication works means local user details for your application are only updated
when a user authenticates. As a result, it is recommended to force users to re-authenticate
each time they visit the site. If your OAuth2 application has the "Skip authorization" property
set, as mentioned above, this will be transparent to users:

```python
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```
