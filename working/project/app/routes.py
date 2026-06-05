from flask import Blueprint, render_template, redirect, url_for, flash, request
from .models import User,Content,ContactMessage
from .form import LoginForm, RegistrationForm,RequestForm
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .decorators import super_admin_required  # ایمپورت دکوراتور

main = Blueprint("main", __name__)



@main.route("/")
def landing():
    return render_template('landing.html')

@main.route("/index")
def home():
    active_contents = Content.query.filter_by(is_visible=True).order_by(Content.created_at.desc()).all()
    if not active_contents:
        SAMPLE_CONTENTS = [
            {"title": "پروژه اداری جعفرپور", "description": "طراحی و اجرای معماری با تمرکز بر نورگیری.", "cover_image": "img/contents/content1.png"},
            {"title": "پروژه مسکونی روشن", "description": "طراحی نما و چیدمان کاربری.", "cover_image": "img/contents/content2.jpg"},
            {"title": "پروژه اداری آزمایشگاه رستگار", "description": "پلان‌های استاندارد و جزئیات اجرایی.", "cover_image": "img/contents/content2.png"},
        ]
        return render_template('index.html', contents=SAMPLE_CONTENTS)
    return render_template('index.html', contents=active_contents)
# app/routes.py
@main.route("/content/<int:content_id>")
@login_required
def content_detail(content_id):
    content = Content.query.get_or_404(content_id)
    return render_template('content_detail.html', content=content)

@main.route("/login", methods=['GET', 'POST'])
def login():
    
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        # جستجو بر اساس ایمیل
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('ورود شما موفقیت‌آمیز بود.', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('ایمیل یا رمز عبور اشتباه است.', 'danger')

    return render_template('login.html', form=form)

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # بررسی تکراری نبودن نام کاربری، ایمیل و تلفن
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data) | 
            (User.phone == form.phone.data)  # اضافه کردن بررسی تلفن
        ).first()
        
        if existing_user:
            if existing_user.username == form.username.data:
                flash("این نام کاربری قبلاً ثبت شده است.", "danger")
            elif existing_user.email == form.email.data:
                flash("این ایمیل قبلاً ثبت شده است.", "danger")
            elif existing_user.phone == form.phone.data:
                flash("این شماره تلفن قبلاً ثبت شده است.", "danger")
            return redirect(url_for('main.register'))

        # ایجاد کاربر جدید
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            phone=form.phone.data,
            usertype=form.usertype.data,
            is_super_admin=False
        )
        new_user.password = form.password.data

        db.session.add(new_user)
        db.session.commit()

        flash("ثبت‌نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.", "success")
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)

@main.route("/contact", methods=['GET', 'POST'])
def contact():
    form = RequestForm()
    if form.validate_on_submit():
        # ذخیره پیام در دیتابیس
        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            message=form.message.data
        )
        db.session.add(message)
        db.session.commit()
        
        flash("پیام شما با موفقیت دریافت شد. بزودی با شما تماس می‌گیریم.", "success")
        return redirect(url_for('main.home'))

    return render_template('contact.html', form=form)

@main.route("/about")
def about():
    return render_template('about.html')

@main.route("/services")
@login_required
def services():
    return render_template('services.html')





# ================ خروج ================
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('شما با موفقیت خارج شدید.', 'info')
    return redirect(url_for('main.home'))

# ================ خطای 404 ================
def not_found(e):
    return render_template('404.html'), 404