from django import apps
from django.contrib.admin import apps as admin_apps


class AppConfig(apps.AppConfig):
    """
    Configuration for the main app.
    """
    name = 'jasmin_auth'
    verbose_name = 'JASMIN Auth'
    default = True


class AdminConfig(admin_apps.AdminConfig):
    """
    Configuration for the custom admin site.
    """
    default_site = 'jasmin_auth.admin_site.AdminSite'
    default = False

    def ready(self):
        """
        When the application becomes ready, register the signal handlers.
        """
        super().ready()
        from . import handlers
