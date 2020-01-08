from django.contrib.admin import apps


class AdminConfig(apps.AdminConfig):
    default_site = 'jasmin_auth_django_admin.admin.AdminSite'
