# jasmin-auth-django-admin

This package provides authentication using JASMIN accounts for a Django Admin application.

## Installation

Install directly from GitHub using `pip`:

```sh
pip install git+https://github.com/cedadev/jasmin-auth-django-admin.git#egg=jasmin_auth_django_admin
```

## Usage

In order to use `jasmin-auth-django-admin`, you must have the client ID and secret for an OAuth2
application that is registered with the JASMIN Accounts Portal. The application must be permitted
to obtain tokens with the profile scope. To allow for transparent authentication, the application
should also have "Skip authorization" set - not doing this will result in the authorization page
being shown every time a user signs in.

To configure your admin to use JASMIN accounts for authentication, we need to modify the Django
settings:

```py
INSTALLED_APPS = [
    # REPLACE django.contrib.admin with these two lines
    'jasmin_auth_django_admin',
    'jasmin_auth_django_admin.apps.AdminConfig',
    # ...
]

# Configure the OAuth application
JASMIN_AUTH = {
    'CLIENT_ID': '<oauth client id>',
    'CLIENT_SECRET': '<oauth client secret>',
}
```

Upon restarting your application, your Django admin will be able to authenticate using JASMIN accounts.

## Security

The way the authentication is written, local user details for your application are only updated
when a user authenticates. However, because authentication is transparent we can set the sessions
to time out after a short period of inactivity. If their session has expired, the user will not see
anything that looks like logging in again - they will just be redirected to the JASMIN Accounts Portal
then redirected straight back as authenticated.

To set the sessions to time out after 10 minutes of inactivity, use the following settings:

```py
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 600
```
