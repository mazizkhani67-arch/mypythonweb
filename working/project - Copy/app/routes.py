from flask import Blueprint, render_template,redirect,url_for,flash
from .models import User
from .form import RegistrationForm
from .extensions import db

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
    return render_template('index_simple.html', projects=SAMPLE_PROJECTS)
    
@main.route("/index")
def index():
    return render_template('index.html')
@main.route("/contact")
def contact():
    return render_template('contact.html')
@main.route("/aboout")
def about():
    return render_template('about.html')
def not_found(e):
    return render_template('404.html'), 404

@main.route("/services")
def services():
    return render_template('services.html',items = SAMPLE_PROJECTS)
