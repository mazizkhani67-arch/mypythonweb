# app/admin_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .decorators import super_admin_required
from .models import User, Content, ContactMessage
from .extensions import db,csrf
from werkzeug.security import generate_password_hash
from .admin_form import UserForm
import os
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    """بررسی فرمت مجاز فایل"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
csrf.exempt(admin_bp)  # ← این خط را اضافه کنید

@admin_bp.route('/')
@login_required
@super_admin_required
def dashboard():
    """داشبورد اصلی مدیریت"""
    stats = {
        'total_users': User.query.count(),
        'total_contents': Content.query.count(),
        'total_messages': ContactMessage.query.count(),
        'unread_messages': ContactMessage.query.filter_by(is_read=False).count(),
        'visible_contents': Content.query.filter_by(is_visible=True).count(),
        'super_admins': User.query.filter_by(is_super_admin=True).count(),
    }
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users,
                         recent_messages=recent_messages)

@admin_bp.route('/users')
@login_required
@super_admin_required
def manage_users():
    """مدیریت کاربران"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/user/add', methods=['GET', 'POST'])
@login_required
@super_admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        usertype = request.form.get('usertype')
        
        # بررسی تکراری نبودن
        if User.query.filter_by(username=username).first():
            flash('نام کاربری تکراری است!', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if User.query.filter_by(email=email).first():
            flash('ایمیل تکراری است!', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if User.query.filter_by(phone=phone).first():  # اضافه کردن بررسی تلفن
            flash('شماره تلفن تکراری است!', 'danger')
            return redirect(url_for('admin.add_user'))
        
        new_user = User(
            username=username,
            email=email,
            phone=phone,
            usertype=usertype,
            is_super_admin=(usertype == 'super_admin')
        )
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()
        
        flash('کاربر با موفقیت اضافه شد!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/add_user.html')

@admin_bp.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.usertype = request.form.get('usertype')
        user.is_super_admin = (request.form.get('usertype') == 'super_admin')
        
        new_password = request.form.get('password')
        if new_password:
            user.password = new_password
        
        db.session.commit()
        flash('اطلاعات کاربر به‌روزرسانی شد!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/user/delete/<int:user_id>')
@login_required
@super_admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('نمی‌توانید خودتان را حذف کنید!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('کاربر با موفقیت حذف شد!', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/content')
@login_required
@super_admin_required
def manage_contents():
    #"""مدیریت محتوا"""
    contents = Content.query.order_by(Content.created_at.desc()).all()
    return render_template('admin/contents.html', contents=contents)
@admin_bp.route('/content/add', methods=['GET', 'POST'])
@login_required
@super_admin_required
def add_content():
    if request.method == 'POST':
        try:
            # دریافت اطلاعات فرم (بدون created_by)
            content = Content(
                employer_name=request.form.get('employer_name'),
                title=request.form.get('title'),
                address=request.form.get('address'),
                content_type=request.form.get('content_type'),
                short_description=request.form.get('short_description'),
                full_content=request.form.get('full_content'),
                video_url=request.form.get('video_url'),
                tags=request.form.get('tags'),
                is_visible='is_visible' in request.form
            )
            
            # پردازش تصویر
            image_filename = 'default_content.jpg'
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    import time
                    name_parts = filename.rsplit('.', 1)
                    unique_filename = f"{name_parts[0]}_{int(time.time())}.{name_parts[1]}"
                    
                    # اطمینان از وجود پوشه
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    image_filename = unique_filename
            
            content.image_file = image_filename
            db.session.add(content)
            db.session.commit()
            
            flash('محتوا با موفقیت اضافه شد!', 'success')
            return redirect(url_for('admin.manage_contents'))
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطا: {e}")
            flash(f'خطا در افزودن محتوا: {str(e)}', 'danger')
            return redirect(url_for('admin.add_content'))
    
    return render_template('admin/add_content.html')


@admin_bp.route('/content/edit/<int:content_id>', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_content(content_id):
    content = Content.query.get_or_404(content_id)
    
    if request.method == 'POST':
        try:
            # به‌روزرسانی اطلاعات (بدون created_by)
            content.source_name = request.form.get('source_name')
            content.title = request.form.get('title')
            content.address = request.form.get('address')
            content.content_type = request.form.get('content_type')
            content.short_description = request.form.get('short_description')
            content.full_content = request.form.get('full_content')
            content.video_url = request.form.get('video_url')
            content.tags = request.form.get('tags')
            content.is_visible = 'is_visible' in request.form
            
            # پردازش تصویر جدید (اگر آپلود شده باشد)
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file and file.filename and allowed_file(file.filename):
                    # حذف تصویر قدیمی
                    if content.image_file and content.image_file != 'default_Content.jpg':
                        old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], content.image_file)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    
                    # ذخیره تصویر جدید
                    filename = secure_filename(file.filename)
                    import time
                    name_parts = filename.rsplit('.', 1)
                    unique_filename = f"{name_parts[0]}_{int(time.time())}.{name_parts[1]}"
                    
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    content.image_file = unique_filename
            
            db.session.commit()
            flash('محتوا با موفقیت به‌روزرسانی شد!', 'success')
            return redirect(url_for('admin.manage_contents'))
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطا: {e}")
            flash(f'خطا در به‌روزرسانی: {str(e)}', 'danger')
            return redirect(url_for('admin.edit_content', content_id=content.id))
    
    return render_template('admin/edit_content.html', content=content)


@admin_bp.route('/content/delete/<int:content_id>')
@login_required
@super_admin_required
def delete_content(content_id):
    content = Content.query.get_or_404(content_id)
    
    # حذف فایل تصویر (اگر وجود داشته باشد)
    if content.image_file and content.image_file != 'default_content.jpg':
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], content.image_file)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(content)
    db.session.commit()
    
    flash('محتوا با موفقیت حذف شد!', 'success')
    return redirect(url_for('admin.manage_contents'))

@admin_bp.route('/content/toggle/<int:content_id>')
@login_required
@super_admin_required
def toggle_content(content_id):
    content = Content.query.get_or_404(content_id)
    content.is_visible = not content.is_visible
    db.session.commit()
    
    status = 'نمایش داده شد' if content.is_visible else 'مخفی شد'
    flash(f'پروژه {content.title} {status}!', 'success')
    return redirect(url_for('admin.manage_contents'))



@admin_bp.route('/messages')
@login_required
@super_admin_required
def manage_messages():
    """مدیریت پیام‌های تماس"""
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@admin_bp.route('/message/read/<int:message_id>')
@login_required
@super_admin_required
def mark_message_read(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    
    flash('پیام به عنوان خوانده شده علامت‌گذاری شد!', 'success')
    return redirect(url_for('admin.manage_messages'))

@admin_bp.route('/message/delete/<int:message_id>')
@login_required
@super_admin_required
def delete_message(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    
    flash('پیام با موفقیت حذف شد!', 'success')
    return redirect(url_for('admin.manage_messages'))