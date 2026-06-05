# app/admin_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .decorators import super_admin_required
from .models import User, Project, ContactMessage
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
        'total_projects': Project.query.count(),
        'total_messages': ContactMessage.query.count(),
        'unread_messages': ContactMessage.query.filter_by(is_read=False).count(),
        'visible_projects': Project.query.filter_by(is_visible=True).count(),
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
    print("=== تابع add_user فراخوانی شد ===")  # برای دیباگ
    
    if request.method == 'POST':
        print("متد POST دریافت شد")
        
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        usertype = request.form.get('usertype')
        
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Phone: {phone}")
        print(f"Usertype: {usertype}")
        
        # اعتبارسنجی
        if not username or not email or not phone or not password:
            flash('تمامی فیلدها الزامی هستند!', 'danger')
            print("خطا: فیلدهای الزامی پر نشده")
            return redirect(url_for('admin.add_user'))
        
        # بررسی تکراری نبودن
        if User.query.filter_by(username=username).first():
            flash('نام کاربری تکراری است!', 'danger')
            print("خطا: نام کاربری تکراری")
            return redirect(url_for('admin.add_user'))
        
        if User.query.filter_by(email=email).first():
            flash('ایمیل تکراری است!', 'danger')
            print("خطا: ایمیل تکراری")
            return redirect(url_for('admin.add_user'))
        
        try:
            # ایجاد کاربر جدید
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
            
            print(f"کاربر {username} با موفقیت اضافه شد!")
            flash('کاربر با موفقیت اضافه شد!', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            db.session.rollback()
            print(f"خطا در ذخیره: {e}")
            flash(f'خطا در ذخیره کاربر: {str(e)}', 'danger')
            return redirect(url_for('admin.add_user'))
    
    # درخواست GET
    print("نمایش فرم افزودن کاربر")
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

@admin_bp.route('/projects')
@login_required
@super_admin_required
def manage_projects():
    """مدیریت پروژه‌ها"""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=projects)
@admin_bp.route('/project/add', methods=['GET', 'POST'])
@login_required
@super_admin_required
def add_project():
    if request.method == 'POST':
        try:
            # دریافت اطلاعات فرم
            employer_name = request.form.get('employer_name')
            title = request.form.get('title')
            address = request.form.get('address')
            project_type = request.form.get('project_type')
            is_visible = 'is_visible' in request.form
            
            # پردازش تصویر
            image_filename = 'default_project.jpg'  # تصویر پیش‌فرض
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file and file.filename and allowed_file(file.filename):
                    # ایمن سازی نام فایل
                    filename = secure_filename(file.filename)
                    # اضافه کردن timestamp به نام فایل برای یکتا شدن
                    import time
                    name_parts = filename.rsplit('.', 1)
                    unique_filename = f"{name_parts[0]}_{int(time.time())}.{name_parts[1]}"
                    
                    # اطمینان از وجود پوشه
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    # ذخیره فایل
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    image_filename = unique_filename
                    print(f"✅ تصویر ذخیره شد: {image_filename}")
            
            # ایجاد پروژه جدید
            project = Project(
                employer_name=employer_name,
                title=title,
                address=address,
                project_type=project_type,
                is_visible=is_visible,
                image_file=image_filename,
                created_by=current_user.id
            )
            
            db.session.add(project)
            db.session.commit()
            
            flash('پروژه با موفقیت اضافه شد!', 'success')
            return redirect(url_for('admin.manage_projects'))
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطا: {e}")
            flash(f'خطا در افزودن پروژه: {str(e)}', 'danger')
            return redirect(url_for('admin.add_project'))
    
    return render_template('admin/add_project.html')

@admin_bp.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        try:
            # به‌روزرسانی اطلاعات
            project.employer_name = request.form.get('employer_name')
            project.title = request.form.get('title')
            project.address = request.form.get('address')
            project.project_type = request.form.get('project_type')
            project.is_visible = 'is_visible' in request.form
            
            # پردازش تصویر جدید (اگر آپلود شده باشد)
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file and file.filename and allowed_file(file.filename):
                    # حذف تصویر قدیمی (اگر وجود داشته باشد و تصویر پیش‌فرض نباشد)
                    if project.image_file and project.image_file != 'default_project.jpg':
                        old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], project.image_file)
                        # بررسی وجود فایل قبل از حذف
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                            print(f"🗑️ تصویر قدیمی حذف شد: {project.image_file}")
                        else:
                            print(f"⚠️ فایل تصویر قدیمی وجود ندارد: {project.image_file}")
                    
                    # ذخیره تصویر جدید
                    filename = secure_filename(file.filename)
                    import time
                    name_parts = filename.rsplit('.', 1)
                    unique_filename = f"{name_parts[0]}_{int(time.time())}.{name_parts[1]}"
                    
                    # اطمینان از وجود پوشه
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    project.image_file = unique_filename
                    print(f"✅ تصویر جدید ذخیره شد: {unique_filename}")
            
            db.session.commit()
            flash('پروژه با موفقیت به‌روزرسانی شد!', 'success')
            return redirect(url_for('admin.manage_projects'))
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطا: {e}")
            flash(f'خطا در به‌روزرسانی: {str(e)}', 'danger')
            return redirect(url_for('admin.edit_project', project_id=project.id))
    
    return render_template('admin/edit_project.html', project=project)

@admin_bp.route('/project/toggle/<int:project_id>')
@login_required
@super_admin_required
def toggle_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.is_visible = not project.is_visible
    db.session.commit()
    
    status = 'نمایش داده شد' if project.is_visible else 'مخفی شد'
    flash(f'پروژه {project.title} {status}!', 'success')
    return redirect(url_for('admin.manage_projects'))

@admin_bp.route('/project/delete/<int:project_id>')
@login_required
@super_admin_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    
    flash('پروژه با موفقیت حذف شد!', 'success')
    return redirect(url_for('admin.manage_projects'))

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