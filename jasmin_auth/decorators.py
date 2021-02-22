from functools import wraps


def no_impersonation(view):
    """
    Decorator that disables impersonation for the given view.
    """
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        # If the request is impersonated, reverse it
        impersonator = getattr(request, 'impersonator', None)
        if impersonator:
            # Store the impersonated user as impersonatee
            request.impersonatee = request.user
            request.user = impersonator
            request.impersonator = None
        return view(request, *args, **kwargs)
    return wrapper
