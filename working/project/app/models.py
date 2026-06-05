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
    password_hash = db.Column(db.String(128), nullable=False)
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


class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    employer_name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(100), nullable=True, default='default_project.jpg')
    project_type = db.Column(db.String(50), nullable=False)
    is_visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # فیلدهای اختیاری برای مدیریت بهتر
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    creator = db.relationship('User', backref='projects')
    
    def __repr__(self):
        return f"Project('{self.title}', '{self.employer_name}')"
    

    # app/models.py - اضافه کنید
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