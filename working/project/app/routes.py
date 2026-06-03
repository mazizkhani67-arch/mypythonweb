from flask import Blueprint, render_template, redirect, url_for, flash, request,session # مطمئن شو که import شده
from .models import User
from .form import LoginForm
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash # check_password_hash را هم اضافه کردیم
from flask_login import login_user, logout_user, login_required, current_user

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
    
    return render_template('index.html', projects=SAMPLE_PROJECTS)

@main.route("/login", methods=['GET', 'POST'])
def login():
    # اگر کاربر از قبل لاگین شده، به صفحه اصلی هدایتش کن
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm() # نمونه فرم لاگین

    # وقتی کاربر دکمه submit رو میزنه و فرم ارسال میشه
    if form.validate_on_submit():
        # فرض می‌کنیم در LoginForm فیلد email (یا username) و password و remember_me داریم
        # اگر فیلد email رو نداری و از username استفاده می‌کنی، خط زیر رو تغییر بده
        user = User.query.filter_by(email=form.email.data).first()
        # یا اگر از username استفاده می‌کنی:
        # user = User.query.filter_by(username=form.username.data).first()

        # بررسی می‌کنیم که کاربر پیدا شده باشه و رمز عبورش درست باشه
        # فرض می‌کنیم مدل User متد check_password رو داره
        if user and user.check_password(form.password.data):
            # وارد کردن کاربر با استفاده از Flask-Login
            # remember=form.remember_me.data رو چک می‌کنه که آیا کاربر تیک "مرا به خاطر بسپار" رو زده یا نه
            login_user(user, remember=form.remember_me.data)

            flash('ورود شما موفقیت‌آمیز بود.', 'success')

            # بررسی می‌کنیم آیا پارامتری به نام 'next' در URL وجود داره یا نه
            # اگر وجود داشت، کاربر را به اون صفحه هدایت می‌کنیم، در غیر این صورت به صفحه اصلی
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            # اگر نام کاربری یا رمز عبور اشتباه بود
            flash('نام کاربری یا رمز عبور نامعتبر است.', 'danger')

    # اگر متد GET بود (صفحه اول باز میشه) یا اعتبارسنجی فرم ناموفق بود
    # قالب login.html رو با فرم نمایش می‌دهیم
    # توجه: در login.html، فرم باید با {{ form.hidden_tag() }} و {{ form.email }} و {{ form.password }} و {{ form.remember_me }} رندر شود
    return render_template('login.html', form=form)

@main.route("/contact", methods=['GET', 'POST'])
def contact():
    TYPES = ["کارفرما", "همکار", "بازدید کننده"]

    if request.method == 'POST':
        print("FORM DATA:", request.form)

        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        usertype = request.form.get('user_type')

        try:
            existing_user = User.query.filter_by(username=username).first() or \
                            User.query.filter_by(email=email).first()
            if existing_user:
                flash("این نام کاربری یا ایمیل قبلاً ثبت شده است.", "danger")
                
                
                return redirect(url_for('main.contact'))

            # استفاده از check_password_hash هنگام ثبت نام معمول نیست، معمولا فقط هش می‌کنیم
            # generate_password_hash برای هش کردن رمز عبور استفاده می‌شود
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            new_user = User(
                username=username,
                email=email,
                phone=phone,
                password_hash=hashed_password, # اینجا رمز عبور هش شده را ذخیره می‌کنیم
                usertype=usertype
            )

            db.session.add(new_user)
            db.session.commit()

            flash("ثبت‌نام با موفقیت انجام شد.", "success")
            # بعد از ثبت نام، بهتر است کاربر وارد سیستم شود یا به صفحه ورود هدایت شود
            # return redirect(url_for('main.login')) # هدایت به صفحه ورود
           
            return redirect(url_for('main.home')) # یا هدایت به صفحه اصلی

        except Exception as e:
            db.session.rollback()
            print(f"Database Error: {e}")
            flash(f"خطا در ثبت اطلاعات: {e}", "danger")
            return redirect(url_for('main.contact'))

    return render_template('contact.html', types=TYPES)


@main.route("/aboout")
def about():
    return render_template('about.html')

def not_found(e):
    return render_template('404.html'), 404

@main.route("/services")
@login_required # need to login
def services():
    return render_template('services.html')

@main.route('/logout')
@login_required # این دکوراتور اختیاری است، اما معمولاً برای خروج لازم نیست. اگر بخواهید فقط کاربر وارد شده بتواند خارج شود، آن را نگه دارید.
def logout():
    logout_user() # این تابع از flask_login اطلاعات نشست کاربر را پاک می‌کند
    flash('شما با موفقیت خارج شدید.', 'info') # یک پیام برای اطلاع‌رسانی به کاربر
    
    
    return redirect(url_for('main.home')) # کاربر را به صفحه اصلی هدایت می‌کند (می‌توانید به url_for('main.login') هم هدایت کنید)