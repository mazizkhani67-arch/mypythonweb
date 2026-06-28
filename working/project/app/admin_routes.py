# app/admin_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from .decorators import super_admin_required
from .models import User, Content, ContactMessage, Project, ProjectChecklist, ProjectType
from .extensions import db, csrf
from werkzeug.security import generate_password_hash
from .admin_form import UserForm
from werkzeug.utils import secure_filename
from datetime import datetime
from .form import ProjectTypeForm, ProjectForm, ChecklistUpdateForm
import os

def allowed_file(filename):
    """بررسی فرمت مجاز فایل"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
csrf.exempt(admin_bp)

# ==================== داشبورد ====================
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

# ==================== مدیریت کاربران ====================
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
        
        if User.query.filter_by(username=username).first():
            flash('نام کاربری تکراری است!', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if User.query.filter_by(email=email).first():
            flash('ایمیل تکراری است!', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if User.query.filter_by(phone=phone).first():
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

# ==================== مدیریت محتوا ====================
@admin_bp.route('/content')
@login_required
@super_admin_required
def manage_contents():
    contents = Content.query.order_by(Content.created_at.desc()).all()
    return render_template('admin/contents.html', contents=contents)

@admin_bp.route('/content/add', methods=['GET', 'POST'])
@login_required
@super_admin_required
def add_content():
    if request.method == 'POST':
        try:
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
            
            image_filename = 'default_content.jpg'
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    import time
                    name_parts = filename.rsplit('.', 1)
                    unique_filename = f"{name_parts[0]}_{int(time.time())}.{name_parts[1]}"
                    
                    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads/content')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    file_path = os.path.join(upload_folder, unique_filename)
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
            content.employer_name = request.form.get('employer_name')
            content.title = request.form.get('title')
            content.address = request.form.get('address')
            content.content_type = request.form.get('content_type')
            content.short_description = request.form.get('short_description')
            content.full_content = request.form.get('full_content')
            content.video_url = request.form.get('video_url')
            content.tags = request.form.get('tags')
            content.is_visible = 'is_visible' in request.form
            
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file and file.filename and allowed_file(file.filename):
                    if content.image_file and content.image_file != 'default_content.jpg':
                        old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], content.image_file)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    
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
    flash(f'محتوا {content.title} {status}!', 'success')
    return redirect(url_for('admin.manage_contents'))

# ==================== مدیریت پیام‌ها ====================
@admin_bp.route('/messages')
@login_required
@super_admin_required
def manage_messages():
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

# ==================== مدیریت نوع پروژه ====================
@admin_bp.route('/project-types')
@login_required
@super_admin_required
def manage_project_types():
    main_types = ProjectType.query.filter_by(category='main').all()
    sub_types = ProjectType.query.filter_by(category='sub').all()
    return render_template('admin/project_types.html', main_types=main_types, sub_types=sub_types)

@admin_bp.route('/project-type/add', methods=['GET', 'POST'])
@login_required
@super_admin_required
def add_project_type():
    form = ProjectTypeForm()
    main_types = ProjectType.query.filter_by(category='main').all()
    form.parent_code.choices = [(0, 'دسته اصلی')] + [(t.code, t.name) for t in main_types]
    
    if form.validate_on_submit():
        project_type = ProjectType(
            code=form.code.data,
            name=form.name.data,
            category='main' if form.parent_code.data == 0 else 'sub',
            parent_code=form.parent_code.data if form.parent_code.data != 0 else None
        )
        db.session.add(project_type)
        db.session.commit()
        flash('نوع پروژه با موفقیت اضافه شد', 'success')
        return redirect(url_for('admin.manage_project_types'))
    
    return render_template('admin/add_project_type.html', form=form)

# ==================== مدیریت پروژه‌ها ====================
@admin_bp.route('/projects')
@login_required
def manage_projects():
    if current_user.is_super_admin:
        projects = Project.query.order_by(Project.created_at.desc()).all()
    elif current_user.usertype == 'admin':
        projects = Project.query.order_by(Project.created_at.desc()).all()
    else:
        projects = Project.query.filter_by(employer_id=current_user.id).order_by(Project.created_at.desc()).all()
    
    return render_template('admin/projects.html', projects=projects, current_user=current_user)

@admin_bp.route('/project/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if not current_user.is_super_admin and current_user.usertype != 'admin':
        flash('دسترسی غیرمجاز. فقط مدیران می‌توانند پروژه ایجاد کنند.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    form = ProjectForm()
    
    # پر کردن لیست نوع پروژه
    project_types = ProjectType.query.all()
    form.project_type_code.choices = [(t.code, f"{t.code} - {t.name}") for t in project_types]
    
    # پر کردن لیست کاربران
    users = User.query.filter(User.usertype.in_(['user', 'employer'])).all()
    form.employer_id.choices = [(0, 'ایجاد کاربر جدید')] + [(u.id, f"{u.username} - {u.email}") for u in users]
    
    if request.method == 'POST':
        # دریافت مستقیم داده‌ها
        employer_id = request.form.get('employer_id')
        is_new_user = (employer_id == '0')
        
        print(f"employer_id: {employer_id}")
        print(f"is_new_user: {is_new_user}")
        
        # اگر کاربر جدید است، اعتبارسنجی را انجام بده
        if is_new_user:
            new_username = request.form.get('new_employer_name')
            new_email = request.form.get('new_employer_email')
            new_phone = request.form.get('new_employer_phone')
            
            if not new_username or not new_email or not new_phone:
                flash('لطفاً تمام فیلدهای کاربر جدید را پر کنید!', 'danger')
                return redirect(url_for('admin.add_project'))
            
            # بررسی عدم تکراری بودن
            if User.query.filter_by(email=new_email).first():
                flash('این ایمیل قبلاً ثبت شده است!', 'danger')
                return redirect(url_for('admin.add_project'))
            
            if User.query.filter_by(username=new_username).first():
                flash('این نام کاربری قبلاً ثبت شده است!', 'danger')
                return redirect(url_for('admin.add_project'))
            
            # ایجاد کاربر جدید
            new_user = User(
                username=new_username,
                email=new_email,
                phone=new_phone,
                usertype='employer',
                is_super_admin=False
            )
            new_user.password = 'default123'
            db.session.add(new_user)
            db.session.commit()
            employer_id = new_user.id
            flash(f'کاربر جدید با نام {new_user.username} ایجاد شد', 'success')
        else:
            # اعتبارسنجی برای کاربر موجود
            if not employer_id or employer_id == '0':
                flash('لطفاً یک کارفرما انتخاب کنید!', 'danger')
                return redirect(url_for('admin.add_project'))
            
            employer_id = int(employer_id)
            user = User.query.get(employer_id)
            if user and user.usertype == 'user':
                user.usertype = 'employer'
                db.session.commit()
                flash(f'کاربر {user.username} به کارفرما تبدیل شد', 'info')
        
        # اعتبارسنجی عنوان پروژه
        title = request.form.get('title')
        if not title:
            flash('لطفاً عنوان پروژه را وارد کنید!', 'danger')
            return redirect(url_for('admin.add_project'))
        
        # اعتبارسنجی نوع پروژه
        project_type_code = request.form.get('project_type_code')
        if not project_type_code:
            flash('لطفاً نوع پروژه را انتخاب کنید!', 'danger')
            return redirect(url_for('admin.add_project'))
        
        try:
            # ایجاد کد پروژه
            year = datetime.now().strftime('%Y')
            month = datetime.now().strftime('%m')
            employer_code = str(employer_id).zfill(4)
            project_type_code_str = str(project_type_code).zfill(3)
            
            # ذخیره فایل‌ها
            cover_filename = None
            zip_filename = None
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads/projects')
            os.makedirs(upload_folder, exist_ok=True)
            
            cover_image = request.files.get('cover_image')
            if cover_image and cover_image.filename:
                cover_filename = secure_filename(f"cover_{year}{month}_{cover_image.filename}")
                cover_image.save(os.path.join(upload_folder, cover_filename))
            
            project_zip = request.files.get('project_zip')
            if project_zip and project_zip.filename:
                zip_filename = secure_filename(f"project_{year}{month}_{project_zip.filename}")
                project_zip.save(os.path.join(upload_folder, zip_filename))
            
            # ایجاد پروژه موقت
            project = Project(
                project_code='temp',
                title=title,
                project_type_code=int(project_type_code),
                employer_id=employer_id,
                location_lat=request.form.get('location_lat', type=float),
                location_lon=request.form.get('location_lon', type=float),
                address=request.form.get('address'),
                description=request.form.get('description'),
                cover_image=cover_filename,
                project_zip=zip_filename,
                progress_percent=0,
                created_by=current_user.id
            )
            
            db.session.add(project)
            db.session.flush()  # برای گرفتن ID
            
            # کد پروژه نهایی
            project_id_code = str(project.id).zfill(4)
            project_code = f"{year}{month}{employer_code}{project_type_code_str}{project_id_code}"
            project.project_code = project_code
            
            db.session.commit()
            
            # ایجاد چک لیست
            checklist = ProjectChecklist(project_id=project.id)
            db.session.add(checklist)
            db.session.commit()
            
            flash(f'پروژه با کد {project_code} با موفقیت ایجاد شد', 'success')
            return redirect(url_for('admin.manage_projects'))
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطا: {e}")
            flash(f'خطا در ایجاد پروژه: {str(e)}', 'danger')
            return redirect(url_for('admin.add_project'))
    
    return render_template('admin/add_project.html', form=form)
    

@admin_bp.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    
    if not current_user.is_super_admin and current_user.usertype != 'admin' and project.employer_id != current_user.id:
        flash('دسترسی غیرمجاز', 'danger')
        return redirect(url_for('admin.manage_projects'))
    
    return render_template('admin/project_detail.html', project=project)

@admin_bp.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if not current_user.is_super_admin and current_user.usertype != 'admin':
        flash('دسترسی غیرمجاز. فقط مدیران می‌توانند پروژه را ویرایش کنند.', 'danger')
        return redirect(url_for('admin.manage_projects'))
    
    form = ProjectForm(obj=project)
    
    project_types = ProjectType.query.all()
    form.project_type_code.choices = [(t.code, f"{t.code} - {t.name}") for t in project_types]
    
    users = User.query.filter(User.usertype.in_(['user', 'employer'])).all()
    form.employer_id.choices = [(u.id, f"{u.username} - {u.email}") for u in users]
    
    if form.validate_on_submit():
        project.title = form.title.data
        project.project_type_code = form.project_type_code.data
        project.employer_id = form.employer_id.data
        project.location_lat = form.location_lat.data
        project.location_lon = form.location_lon.data
        project.address = form.address.data
        project.description = form.description.data
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads/projects')
        os.makedirs(upload_folder, exist_ok=True)
        
        if form.cover_image.data:
            if project.cover_image:
                old_path = os.path.join(upload_folder, project.cover_image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            file = form.cover_image.data
            project.cover_image = secure_filename(f"cover_{project.project_code}_{file.filename}")
            file.save(os.path.join(upload_folder, project.cover_image))
        
        if form.project_zip.data:
            if project.project_zip:
                old_path = os.path.join(upload_folder, project.project_zip)
                if os.path.exists(old_path):
                    os.remove(old_path)
            file = form.project_zip.data
            project.project_zip = secure_filename(f"project_{project.project_code}_{file.filename}")
            file.save(os.path.join(upload_folder, project.project_zip))
        
        db.session.commit()
        flash('پروژه با موفقیت ویرایش شد', 'success')
        return redirect(url_for('admin.manage_projects'))
    
    return render_template('admin/edit_project.html', form=form, project=project)

@admin_bp.route('/project/<int:project_id>/delete')
@login_required
def delete_project(project_id):
    if not current_user.is_super_admin:
        flash('دسترسی غیرمجاز. فقط سوپر ادمین می‌تواند پروژه را حذف کند.', 'danger')
        return redirect(url_for('admin.manage_projects'))
    
    project = Project.query.get_or_404(project_id)
    project_code = project.project_code
    
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads/projects')
    
    if project.cover_image:
        cover_path = os.path.join(upload_folder, project.cover_image)
        if os.path.exists(cover_path):
            os.remove(cover_path)
    
    if project.project_zip:
        zip_path = os.path.join(upload_folder, project.project_zip)
        if os.path.exists(zip_path):
            os.remove(zip_path)
    
    db.session.delete(project)
    db.session.commit()
    
    flash(f'پروژه {project_code} با موفقیت حذف شد', 'success')
    return redirect(url_for('admin.manage_projects'))


@admin_bp.route('/project/<int:project_id>/progress', methods=['GET', 'POST'])
@login_required
def update_project_progress(project_id):
    project = Project.query.get_or_404(project_id)
    
    if not current_user.is_super_admin and current_user.usertype != 'admin' and project.employer_id != current_user.id:
        flash('دسترسی غیرمجاز', 'danger')
        return redirect(url_for('admin.manage_projects'))
    
    checklist = project.checklist
    form = ChecklistUpdateForm(obj=checklist)
    
    if form.validate_on_submit():
        # ====== به‌روزرسانی دستی فیلدها ======
        # فیلدهای چک لیست اصلی
        checklist.user_registered = form.user_registered.data
        checklist.project_registered = form.project_registered.data
        checklist.employer_confirmed = form.employer_confirmed.data
        checklist.album_completed = form.album_completed.data
        checklist.engineering_approved = form.engineering_approved.data
        checklist.settlement_done = form.settlement_done.data
        checklist.delivered_to_client = form.delivered_to_client.data
        
        # فیلدهای ارسال پیامک
        checklist.sms_user_registered = form.sms_user_registered.data if hasattr(form, 'sms_user_registered') else False
        checklist.sms_project_registered = form.sms_project_registered.data if hasattr(form, 'sms_project_registered') else False
        checklist.sms_employer_confirmed = form.sms_employer_confirmed.data if hasattr(form, 'sms_employer_confirmed') else False
        checklist.sms_album_completed = form.sms_album_completed.data if hasattr(form, 'sms_album_completed') else False
        checklist.sms_engineering_approved = form.sms_engineering_approved.data if hasattr(form, 'sms_engineering_approved') else False
        checklist.sms_settlement_done = form.sms_settlement_done.data if hasattr(form, 'sms_settlement_done') else False
        checklist.sms_delivered_to_client = form.sms_delivered_to_client.data if hasattr(form, 'sms_delivered_to_client') else False
        
        checklist.updated_at = datetime.utcnow()
        
        # محاسبه درصد پیشرفت
        items = [
            checklist.user_registered,
            checklist.project_registered,
            checklist.employer_confirmed,
            checklist.album_completed,
            checklist.engineering_approved,
            checklist.settlement_done,
            checklist.delivered_to_client
        ]
        progress = sum(1 for item in items if item) * 100 // 7
        project.progress_percent = progress
        
        db.session.commit()
        
        # ====== ارسال پیامک برای مراحل تیک خورده ======
        employer_phone = project.employer.phone
        
        if employer_phone:
            sms_fields = [
                ('sms_user_registered', 'ثبت کاربر به عنوان کارفرما', checklist.user_registered),
                ('sms_project_registered', 'ثبت پروژه', checklist.project_registered),
                ('sms_employer_confirmed', 'تایید کارفرما', checklist.employer_confirmed),
                ('sms_album_completed', 'اتمام آلبوم', checklist.album_completed),
                ('sms_engineering_approved', 'تایید نظام مهندسی', checklist.engineering_approved),
                ('sms_settlement_done', 'تسویه حساب', checklist.settlement_done),
                ('sms_delivered_to_client', 'تحویل به مشتری', checklist.delivered_to_client),
            ]
            
            for sms_field, step_name, is_checked in sms_fields:
                if is_checked and getattr(checklist, sms_field, False):
                    try:
                        from utils.sms import send_project_sms
                        
                        message = f"""
                        پروژه {project.project_code}
                        مرحله: {step_name}
                        پیشرفت کلی: {progress}%
                        """
                        
                        result = send_project_sms(
                            phone_number=employer_phone,
                            message=message,
                            project_code=project.project_code,
                            step_name=step_name
                        )
                        
                        if result.get('success'):
                            flash(f'✅ پیامک مرحله "{step_name}" ارسال شد', 'success')
                        else:
                            flash(f'⚠️ خطا در ارسال پیامک مرحله "{step_name}": {result.get("error", "نامشخص")}', 'danger')
                            
                    except Exception as e:
                        flash(f'⚠️ خطا در ارسال پیامک: {str(e)}', 'danger')
        else:
            flash('⚠️ شماره تلفن کارفرما ثبت نشده است!', 'warning')
        
        flash('✅ پیشرفت پروژه با موفقیت به‌روزرسانی شد', 'success')
        return redirect(url_for('admin.project_detail', project_id=project.id))
    
    # اگر فرم اعتبارسنجی نشد، خطاها را نمایش بده
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'خطا در فیلد {field}: {error}', 'danger')
    
    return render_template('admin/project_progress.html', project=project, form=form)


# app/admin_routes.py
# ... بخش‌های قبلی ...

# ==================== مدیریت پیامک ====================
@admin_bp.route('/sms')
@login_required
@super_admin_required
def sms_panel():
    """پنل مدیریت پیامک"""
    form = SMSForm()
    
    # پر کردن لیست پروژه‌ها
    projects = Project.query.all()
    form.project_id.choices = [(0, 'بدون پروژه')] + [(p.id, f"{p.project_code} - {p.title}") for p in projects]
    
    return render_template('admin/sms_panel.html', form=form)

@admin_bp.route('/sms/send', methods=['POST'])
@login_required
@super_admin_required
def send_sms():
    """ارسال پیامک با سرویس پترن"""
    form = SMSForm()
    
    # پر کردن لیست پروژه‌ها (برای بازگرداندن فرم در صورت خطا)
    projects = Project.query.all()
    form.project_id.choices = [(0, 'بدون پروژه')] + [(p.id, f"{p.project_code} - {p.title}") for p in projects]
    
    if form.validate_on_submit():
        recipient = form.recipient.data
        project_id = form.project_id.data
        custom_step = form.custom_step.data
        
        # دریافت اطلاعات پروژه
        project = None
        project_code = 'بدون پروژه'
        progress = 0
        step_name = custom_step or 'به‌روزرسانی'
        
        if project_id > 0:
            project = Project.query.get(project_id)
            if project:
                project_code = project.project_code
                progress = project.progress_percent or 0
                # اگر شماره تلفن از پروژه گرفته نشده، از فرم استفاده کن
                if not recipient:
                    recipient = project.employer.phone if project.employer else None
        
        if not recipient:
            flash('⚠️ شماره تلفن گیرنده وارد نشده است!', 'danger')
            return render_template('admin/sms_panel.html', form=form)
        
        try:
            from utils.sms import send_project_sms
            
            result = send_project_sms(
                phone_number=recipient,
                project_code=project_code,
                step_name=step_name,
                progress_percent=progress
            )
            
            if result.get('success'):
                flash(f'✅ پیامک با موفقیت ارسال شد (شناسه: {result.get("message_id", "نامشخص")})', 'success')
            else:
                flash(f'❌ خطا در ارسال پیامک: {result.get("error", "نامشخص")}', 'danger')
                
        except ImportError:
            flash('❌ ماژول ارسال پیامک یافت نشد!', 'danger')
        except Exception as e:
            flash(f'❌ خطا در ارسال پیامک: {str(e)}', 'danger')
        
        return redirect(url_for('admin.sms_panel'))
    
    # اگر فرم اعتبارسنجی نشد
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'خطا در فیلد {field}: {error}', 'danger')
    
    return render_template('admin/sms_panel.html', form=form)

@admin_bp.route('/sms/project/<int:project_id>')
@login_required
@super_admin_required
def sms_project_info(project_id):
    """دریافت اطلاعات پروژه برای ارسال پیامک"""
    project = Project.query.get_or_404(project_id)
    
    employer_phone = project.employer.phone if project.employer else None
    employer_name = project.employer.username if project.employer else None
    
    return jsonify({
        'success': True,
        'phone': employer_phone,
        'name': employer_name,
        'project_code': project.project_code,
        'title': project.title,
        'progress': project.progress_percent or 0
    })

@admin_bp.route('/sms/templates')
@login_required
@super_admin_required
def sms_templates():
    """دریافت الگوهای پیامک"""
    templates = {
        'progress': 'پروژه {0} با پیشرفت {1}% به‌روزرسانی شد. مرحله: {2}',
        'complete': 'پروژه {0} با موفقیت تکمیل شد. پیشرفت: {1}%',
        'approval': 'لطفاً نسبت به تایید پروژه {0} اقدام فرمایید. مرحله: {1}',
        'step': 'پروژه {0} به مرحله جدید رسید. مرحله: {1} - پیشرفت: {2}%'
    }
    return jsonify({'success': True, 'templates': templates})