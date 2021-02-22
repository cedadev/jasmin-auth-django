from django.dispatch import Signal


#: Signal that is dispatched when an impersonation is started
#: Receives the impersonator and the impersonatee as arguments
impersonation_started = Signal()

#: Signal that is dispatched when impersonation is explicitly ended
#: Receives the impersonator and the impersonatee as arguments
#: Note that, similar to the way that django.contrib.auth.user_logged_out is only
#: dispatched for an explicit logout, this signal is only dispatched when
#: impersonation is explicitly ended
#: It is NOT dispatched if impersonation ends as a result of some other action such as
#: the session expiring or the user logging out completely
impersonation_ended = Signal()
