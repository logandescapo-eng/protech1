from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect


def user_type_required(user_type):
    """Role-based access control decorator (client / worker)."""

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.user_type != user_type:
                messages.error(request, 'You do not have permission to access this page.')
                if request.user.user_type == 'worker':
                    return redirect('worker_dashboard')
                return redirect('user_dashboard')
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
