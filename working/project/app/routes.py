from flask import Blueprint, render_template,redirect,url_for,flash,request
from .models import User
from .form import RegistrationForm
from .extensions import db
from werkzeug.security import generate_password_hash # برای هش کردن پسورد
main = Blueprint("main", __name__)

# دیتای نمونه برای نمایش در صفحه Home
SAMPLE_PROJECTS = [
    {
        "title": "پروژه اداری جعفرپور",
        "description": "طراحی و اجرای معماری با تمرکز بر نورگیری و بهینه‌سازی فضا.",
        "cover_image": "img/project1.png",
    },
    {
        "title": "پروژه مسکونی روشن",
        "description": "طراحی نما و چیدمان کاربری با رویکرد انعطاف‌پذیر.",
        "cover_image": "img/project2.jpg",
    },
    {
        "title": "پروژه اداری آزمایشگاه رستگار",
        "description": "پلان‌های استاندارد، مسیرهای حرکتی دقیق و جزئیات اجرایی.",
        "cover_image": "img/project3.png",
    },
]
@main.route("/")
def landing():
    return render_template('landing.html')

@main.route("/index")
def home():
    # فعلاً از SAMPLE_PROJECTS برای قالب استفاده می‌کنیم
    # بعداً پروژه‌ها را از دیتابیس می‌گیریم
    return render_template('index.html', projects=SAMPLE_PROJECTS)


@main.route("/contact", methods=['GET', 'POST'])
def contact():
    TYPES = ["مشتری", "همکار", "بازدید کننده"]

    if request.method == 'POST':
        print("FORM DATA:", request.form)

        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        usertype = request.form.get('user_type')

        # ----- تغییرات این قسمت -----
        try:
            existing_user = User.query.filter_by(username=username).first() or \
                            User.query.filter_by(email=email).first()
            if existing_user:
                flash("این نام کاربری یا ایمیل قبلاً ثبت شده است.", "danger")
                return redirect(url_for('main.contact'))

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            new_user = User(
                username=username,
                email=email,
                phone=phone,
                password_hash=hashed_password,
                usertype=usertype
            )

            db.session.add(new_user)
            db.session.commit() # اینجا احتمالاً خطا رخ می‌دهد

            flash("ثبت‌نام با موفقیت انجام شد.", "success")
            return redirect(url_for('main.home'))

        except Exception as e:
            db.session.rollback() # برای اطمینان از برگشت تراکنش در صورت خطا
            print(f"Database Error: {e}") # چاپ خطا در کنسول
            flash(f"خطا در ثبت اطلاعات: {e}", "danger") # نمایش خطا به کاربر
            return redirect(url_for('main.contact'))
        # ----- پایان تغییرات -----

    return render_template('contact.html', types=TYPES)
   


@main.route("/aboout")
def about():
    return render_template('about.html')
def not_found(e):
    return render_template('404.html'), 404

@main.route("/services")
def services():
    return render_template('services.html',items = SAMPLE_PROJECTS)
