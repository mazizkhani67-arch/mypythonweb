# app/decorators.py
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def super_admin_required(f):
    """فقط سوپر ادمین می‌تواند به صفحه دسترسی داشته باشد"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('لطفا ابتدا وارد شوید', 'warning')
            return redirect(url_for('main.login'))
        if not current_user.is_super_admin:
            flash('دسترسی غیرمجاز! فقط سوپر ادمین می‌تواند وارد این صفحه شود.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function