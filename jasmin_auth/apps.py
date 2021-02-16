from django.contrib.admin import apps


class AdminConfig(apps.AdminConfig):
    """
    Custom admin configuration object.
    """
    default_site = 'jasmin_auth.admin.AdminSite'
