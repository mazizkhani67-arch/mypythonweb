# app/decorators.py
from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user

def super_admin_required(f):
    """فقط سوپر ادمین می‌تواند به صفحه دسترسی داشته باشد"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('لطفا ابتدا وارد شوید', 'warning')
            return redirect(url_for('main.login', next=request.url))  # اضافه کردن next
        if not current_user.is_super_admin:
            flash('دسترسی غیرمجاز! فقط سوپر ادمین می‌تواند وارد این صفحه شود.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """ادمین معمولی یا سوپر ادمین می‌توانند دسترسی داشته باشند"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('لطفا ابتدا وارد شوید', 'warning')
            return redirect(url_for('main.login', next=request.url))  # اضافه کردن next
        if not (current_user.usertype == "admin" or current_user.is_super_admin):
            flash('دسترسی غیرمجاز! فقط مدیران می‌توانند وارد این صفحه شوند.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """هر کاربر وارد شده‌ای (حتی عادی) می‌تواند دسترسی داشته باشد"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('لطفا ابتدا وارد شوید', 'warning')
            return redirect(url_for('main.login', next=request.url))  # اضافه کردن next
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """دکوراتور عمومی برای نقش‌های مختلف"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('لطفا ابتدا وارد شوید', 'warning')
                return redirect(url_for('main.login', next=request.url))
            
            # بررسی دسترسی بر اساس نقش
            if current_user.usertype not in allowed_roles and not current_user.is_super_admin:
                flash('دسترسی غیرمجاز!', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator