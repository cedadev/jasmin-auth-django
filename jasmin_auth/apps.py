from django.contrib.admin import apps


class AdminConfig(apps.AdminConfig):
    """
    Custom admin configuration object.
    """
    default_site = 'jasmin_auth.admin_site.AdminSite'

    def ready(self):
        """
        When the application becomes ready, register the signal handlers.
        """
        super().ready()
        from . import handlers
