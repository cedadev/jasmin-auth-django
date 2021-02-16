# jasmin-auth-django

This packages provides views for authenticating users for a Django application using JASMIN accounts.

It also patches the admin to use the same authentication views as the rest of the site.

## Installation

Install directly from GitHub using `pip`:

```sh
pip install git+https://github.com/cedadev/jasmin-auth-django.git#egg=jasmin_auth_django
```

## Usage

In order to use `jasmin-auth-django`, you must have the client ID and secret for an OAuth2
application that is registered with the JASMIN Accounts Portal. The application must be permitted
to obtain tokens with the profile scope. To allow for transparent authentication, the application
should also have "Skip authorization" set - not doing this will result in the authorization page
being shown every time a user authenticates with your service.

To configure your admin to use JASMIN accounts for authentication, you need to modify the Django
settings:

```py
INSTALLED_APPS = [
    # REPLACE django.contrib.admin with this line
    'jasmin_auth_django_admin.apps.AdminConfig',
    # ...
    # Add the jasmin_auth app
    'jasmin_auth',
]

# Configure the OAuth application details
JASMIN_AUTH = {
    'CLIENT_ID': '<oauth client id>',
    'CLIENT_SECRET': '<oauth client secret>',
}
```

Upon restarting your application, your Django admin will be able to authenticate using JASMIN accounts.

## Security

The way the authentication works means local user details for your application are only updated
when a user authenticates. However, because authentication is transparent we can set the sessions
to time out after a short period of inactivity. If their session has expired, the user will not see
anything that looks like logging in again - they will just be redirected to the JASMIN Accounts Portal
then redirected straight back as authenticated.

To set the sessions to time out after 10 minutes of inactivity, use the following settings:

```py
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 600
```
