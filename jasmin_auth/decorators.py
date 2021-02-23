from functools import update_wrapper


def no_impersonation(view):
    """
    Decorator that disables impersonation for the given view.
    """
    # Just return a new function with the no_impersonation flag set
    def wrapper(*args, **kwargs):
        return view(*args, **kwargs)
    wrapper.no_impersonation = True
    return update_wrapper(wrapper, view)
