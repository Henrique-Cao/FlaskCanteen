# app/utils/decorators.py
from functools import wraps
from flask import abort, redirect, url_for, request, jsonify
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check 1: Is someone logged in?
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({"success": False, "message": "Authentication required."}), 401
            # Must return here so unauthenticated requests never fall through
            return redirect(url_for("main.index"))

        # Check 2: Are they an admin?
        # Safe check in case role attribute is missing
        if getattr(current_user, "role", None) != "admin" and not getattr(current_user, "is_admin", False):
            if request.is_json:
                return jsonify({"success": False, "message": "Admin privileges required."}), 403
            abort(403)

        return f(*args, **kwargs)
    return decorated_function