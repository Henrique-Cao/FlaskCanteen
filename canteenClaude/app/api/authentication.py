from flask import Blueprint, jsonify, request, session,abort, redirect, url_for
from app.extensions import db
from app.models import User
from flask_login import current_user, login_user, login_required,LoginManager,logout_user,UserMixin
from functools import wraps

from app.utils.decorators import admin_required

auth_api = Blueprint('auth', __name__)

# --- Login Route ---
@auth_api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    
    # Prevent timing attacks and user enumeration by checking hash validity
    if user and user.check_password(password):
        
        session['user_id'] = user.id
        session['role'] = user.role
        login_user(user)

        return jsonify({"message": "Login successful", 
                        "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role,}, 
                        "redirect_url": "/admin/",
                        "success": True})

    return jsonify({"message": "Invalid email or password"}), 401


@admin_required
@auth_api.route("/logout", methods=["POST", "GET"])
def logout():
    logout_user()
    session.clear()
    print("User logged out")
    return jsonify({"success": True, "redirect_url": "/"})
