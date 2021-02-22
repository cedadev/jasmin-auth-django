from django.apps import apps
from django.dispatch import receiver

from .signals import impersonation_started


# If the tsunami application is installed, register a handler that makes a tsunami
# event every time an impersonation is started
if apps.is_installed('tsunami'):
    from tsunami.models import Event


    @receiver(impersonation_started)
    def make_tsunami_event(sender, impersonator, impersonatee, **kwargs):
        """
        Make a tsunami event indicating that an impersonation was started.
        """
        # Get the opts for the user class
        Event.objects.create(
            event_type = 'jasmin_auth.user_impersonated',
            target = impersonatee,
            user = impersonator
        )
