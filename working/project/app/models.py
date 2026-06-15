# app/models.py
from .extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    usertype = db.Column(db.String(128), nullable=False, default='user')  # 'admin', 'user', 'super_admin'
     # اضافه کردن با default مقدار
    is_super_admin = db.Column(db.Boolean, default=False, nullable=False)
    # اصلاح متدهای password (کد شما اشتباه داشت)
    @property
    def password(self):
        """این متد فقط برای خطا دادن است - از خواندن رمز جلوگیری می‌کند"""
        raise AttributeError('رمز عبور قابل خواندن نیست')
    
    @password.setter
    def password(self, password):
        """تنظیم رمز عبور به صورت هش شده"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """بررسی صحت رمز عبور"""
        return check_password_hash(self.password_hash, password)
    
    # متد کمکی برای بررسی نقش‌ها
    def is_admin(self):
        return self.usertype == 'admin' or self.is_super_admin
    
    def is_regular_user(self):
        return self.usertype == 'user' and not self.is_super_admin
    
    def __repr__(self):
        return f'<User {self.username}>'


# app/models.py
from datetime import datetime


class Content(db.Model):
    __tablename__ = 'contents'  # نام نهایی جدول
    
    id = db.Column(db.Integer, primary_key=True)
    employer_name = db.Column(db.String(100), nullable=False)  # نام کارفرما/منبع
    title = db.Column(db.String(150), nullable=False)          # عنوان مطلب
    address = db.Column(db.Text, nullable=True)                # آدرس/مکان
    image_file = db.Column(db.String(100), nullable=True, default='default_content.jpg')
    content_type = db.Column(db.String(50), nullable=False)    # نوع محتوا
    is_visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # فیلدهای محتوای غنی
    short_description = db.Column(db.Text, nullable=True)
    full_content = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(200), nullable=True)
    gallery_images = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(200), nullable=True)
    
    def __repr__(self):
        return f"Content('{self.title}')"
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Message from {self.name}>'
    

class UTMCoordinate(db.Model):
    __tablename__ = 'utm_coordinates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    easting = db.Column(db.Float, nullable=False)  # مختصات شرقی
    northing = db.Column(db.Float, nullable=False)  # مختصات شمالی
    zone = db.Column(db.Integer, nullable=False)  # ناحیه UTM
    hemisphere = db.Column(db.String(1), default='N')  # N یا S
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    latitude = db.Column(db.Float, nullable=True)   # اضافه شده
    longitude = db.Column(db.Float, nullable=True)  # اضافه شده
    # رابطه با کاربر
    user = db.relationship('User', backref='utm_coordinates')
    
    def __repr__(self):
        return f'<UTM {self.easting}, {self.northing} Zone {self.zone}>'
    
    # app/models.py - اضافه کردن مدل‌های جدید

class ProjectType(db.Model):
    """مدل نوع پروژه با کدهای دسته‌بندی"""
    __tablename__ = 'project_types'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, unique=True, nullable=False)  # کد عددی (100, 101, ...)
    name = db.Column(db.String(100), nullable=False)
    parent_code = db.Column(db.Integer, db.ForeignKey('project_types.code'), nullable=True)
    category = db.Column(db.String(50), nullable=False)  # 'main' یا 'sub'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # رابطه برای زیردسته‌ها
    children = db.relationship('ProjectType', backref=db.backref('parent', remote_side=[code]))
    
    def __repr__(self):
        return f"<ProjectType {self.code}: {self.name}>"

# app/models.py - اضافه کردن فیلد title به مدل Project

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)  # اضافه شود
    project_type_code = db.Column(db.Integer, db.ForeignKey('project_types.code'), nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location_lat = db.Column(db.Float, nullable=True)
    location_lon = db.Column(db.Float, nullable=True)
    address = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(200), nullable=True)
    project_zip = db.Column(db.String(200), nullable=True)
    progress_percent = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # روابط
    project_type = db.relationship('ProjectType', foreign_keys=[project_type_code])
    employer = db.relationship('User', foreign_keys=[employer_id], backref='projects_as_employer')
    creator = db.relationship('User', foreign_keys=[created_by], backref='projects_created')

class ProjectChecklist(db.Model):
    """چک لیست پیشرفت پروژه"""
    __tablename__ = 'project_checklists'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_registered = db.Column(db.Boolean, default=False)  # 1- ثبت کاربر به عنوان کارفرما
    project_registered = db.Column(db.Boolean, default=False)  # 2- ثبت پروژه
    employer_confirmed = db.Column(db.Boolean, default=False)  # 3- تایید کارفرما
    album_completed = db.Column(db.Boolean, default=False)  # 4- اتمام آلبوم
    engineering_approved = db.Column(db.Boolean, default=False)  # 5- تایید نظام مهندسی
    settlement_done = db.Column(db.Boolean, default=False)  # 6- تسویه حساب
    delivered_to_client = db.Column(db.Boolean, default=False)  # 7- تحویل به مشتری
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = db.relationship('Project', backref='checklist')

class ProjectMessage(db.Model):
    """پیام‌های مربوط به پروژه"""
    __tablename__ = 'project_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('Project', backref='messages')
    sender = db.relationship('User', foreign_keys=[sender_id])