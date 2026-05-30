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
def home():
    # فعلاً از SAMPLE_PROJECTS برای قالب استفاده می‌کنیم
    # بعداً پروژه‌ها را از دیتابیس می‌گیریم
    return render_template('index.html', projects=SAMPLE_PROJECTS)
    
@main.route("/contact", methods=['GET', 'POST'])
def contact():
    
    if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            phone=request.form['phone']
            password = request.form['password']

            # بررسی اینکه آیا کاربر با این نام کاربری یا ایمیل وجود دارد
            existing_user = User.query.filter_by(username=username).first() or \
                            User.query.filter_by(email=email).first()
            if existing_user:
                # نمایش پیام خطا به کاربر
                return "Username or email already exists!" # باید این را بهتر مدیریت کنید (مثلا با flash messages)

            # هش کردن پسورد قبل از ذخیره
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            new_user = User(username=username, email=email, phone= phone ,password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('main.home')) # یا صفحه موفقیت آمیز ثبت نام

    return render_template('contact.html')   


@main.route("/aboout")
def about():
    return render_template('about.html')
def not_found(e):
    return render_template('404.html'), 404

@main.route("/services")
def services():
    return render_template('services.html',items = SAMPLE_PROJECTS)
