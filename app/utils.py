from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps

def role_required(*roles):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role.value not in roles:
                flash("You do not have permission to access this page.")
                return redirect(url_for("facility.list_facilities"))
            return func(*args, **kwargs)
        return decorated_view
    return wrapper
