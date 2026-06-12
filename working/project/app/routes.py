from flask import Blueprint, render_template, redirect, url_for, flash,jsonify ,request
from .models import User,Content,ContactMessage,UTMCoordinate
from .form import LoginForm, RegistrationForm,RequestForm,UTMCoodinateForm
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .decorators import super_admin_required  # ایمپورت دکوراتور
import folium
from folium.plugins import MousePosition
import os

from pyproj.exceptions import ProjError

# در بالای routes.py، بعد از importها
# بیس‌مپ مشترک برای هر دو سرویس
BASE_MAP_URL = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
BASE_MAP_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'

main = Blueprint("main", __name__)



@main.route("/")
def landing():
    return render_template('landing.html')

@main.route("/index")
def home():
    active_contents = Content.query.filter_by(is_visible=True).order_by(Content.created_at.desc()).all()
    if not active_contents:
        SAMPLE_CONTENTS = [
            {"id":1,"title": "پروژه اداری جعفرپور", "description": "طراحی و اجرای معماری با تمرکز بر نورگیری.", "cover_image": "uploads/contents/content1.png"},
            {"id":2,"title": "پروژه مسکونی روشن", "description": "طراحی نما و چیدمان کاربری.", "cover_image": "uploads/contents/content2.jpg"},
            {"id":3,"title": "پروژه اداری آزمایشگاه رستگار", "description": "پلان‌های استاندارد و جزئیات اجرایی.", "cover_image": "uploads/contents/content2.png"},
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
        # اگر کاربر قبلاً وارد شده، به صفحه درخواستی یا خانه هدایت شود
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('ورود شما موفقیت‌آمیز بود.', 'success')
            
            # هدایت به صفحه درخواست‌کننده
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.home'))
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

def services():
    return render_template('services.html')

@main.route('/services/utm-converter', methods=['GET', 'POST'])
@login_required
def utm_converter():
    form = UTMCoodinateForm()
    map_html = None
    coordinates = None
    
    if form.validate_on_submit():
        easting = form.easting.data
        northing = form.northing.data
        zone = form.zone.data
        hemisphere = form.hemisphere.data
        
        try:
            import pyproj
            
            if hemisphere == 'N':
                utm_crs = pyproj.CRS(f"EPSG:326{zone}")
            else:
                utm_crs = pyproj.CRS(f"EPSG:327{zone}")
            
            wgs84_crs = pyproj.CRS("EPSG:4326")
            transformer = pyproj.Transformer.from_crs(utm_crs, wgs84_crs, always_xy=True)
            
            lon, lat = transformer.transform(easting, northing)
            coordinates = {'lat': lat, 'lon': lon, 'easting': easting, 'northing': northing, 'zone': zone}
            
            # ذخیره در دیتابیس
            utm_coord = UTMCoordinate(
                user_id=current_user.id,
                easting=easting,
                northing=northing,
                zone=zone,
                hemisphere=hemisphere,
                latitude=lat,
                longitude=lon
            )
            db.session.add(utm_coord)
            db.session.commit()
            
            # ایجاد نقشه با folium و استفاده از بیس‌مپ مشترک
            m = folium.Map(location=[lat, lon], zoom_start=15, control_scale=True)
            
            # اضافه کردن بیس‌مپ یکسان
            folium.TileLayer(
                tiles=BASE_MAP_URL,
                attr=BASE_MAP_ATTRIBUTION,
                name='نقشه پایه',
                control=False
            ).add_to(m)
            
            # افزودن نشانگر
            folium.Marker(
                [lat, lon],
                popup=f"""
                <b>مختصات UTM:</b><br>
                Easting: {easting}<br>
                Northing: {northing}<br>
                Zone: {zone}{hemisphere}<br>
                <b>طول و عرض جغرافیایی:</b><br>
                Lat: {lat:.6f}<br>
                Lon: {lon:.6f}
                """,
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
            # افزودن نمایش مختصات ماوس
            MousePosition().add_to(m)
            
            map_html = m._repr_html_()
            
        except Exception as e:
            flash(f'خطا در تبدیل مختصات: {str(e)}', 'danger')
            print(f"Error: {e}")
    
    user_coordinates = UTMCoordinate.query.filter_by(user_id=current_user.id).order_by(UTMCoordinate.created_at.desc()).limit(10).all()
    
    return render_template('utm_converter.html', 
                         form=form, 
                         map_html=map_html, 
                         coordinates=coordinates,
                         user_coordinates=user_coordinates)

@main.route('/services/utm-picker', methods=['GET', 'POST'])
@login_required
def utm_picker():
    if request.method == 'POST':
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'داده‌ای ارسال نشده است'}), 400
        
        lat = data.get('lat')
        lon = data.get('lon')
        should_save = data.get('save', False)
        
        # اعتبارسنجی دقیق
        if lat is None or lon is None:
            return jsonify({'success': False, 'message': 'مختصات معتبر نیست'}), 400
        
        try:
            import pyproj
            
            # تبدیل به float
            lat = float(lat)
            lon = float(lon)
            
            # محاسبه zone (با محدودیت)
            zone = int((lon + 180) // 6) + 1
            zone = max(1, min(60, zone))
            
            # تعیین نیمکره و سیستم مختصات UTM
            if lat < 0:
                hemisphere = 'S'
                epsg_code = 32700 + zone
            else:
                hemisphere = 'N'
                epsg_code = 32600 + zone
            
            utm_crs = pyproj.CRS(f"EPSG:{epsg_code}")
            wgs84_crs = pyproj.CRS("EPSG:4326")
            
            # ایجاد تبدیل‌کننده
            transformer = pyproj.Transformer.from_crs(wgs84_crs, utm_crs, always_xy=True)
            
            # تبدیل مختصات
            easting, northing = transformer.transform(lon, lat)
            
            # گرد کردن
            easting = round(float(easting), 2)
            northing = round(float(northing), 2)
            
            # اگر درخواست ذخیره باشد
            if should_save:
                # بررسی وجود کاربر
                if not current_user or not current_user.is_authenticated:
                    return jsonify({'success': False, 'message': 'لطفا وارد شوید'}), 401
                
                # ذخیره در دیتابیس
                utm_coord = UTMCoordinate(
                    user_id=current_user.id,
                    easting=easting,
                    northing=northing,
                    zone=zone,
                    hemisphere=hemisphere,
                    latitude=lat,
                    longitude=lon
                )
                db.session.add(utm_coord)
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'مختصات با موفقیت ذخیره شد'
                })
            
            # برگرداندن مختصات تبدیل شده (بدون ذخیره)
            return jsonify({
                'success': True,
                'easting': easting,
                'northing': northing,
                'zone': zone,
                'hemisphere': hemisphere,
                'lat': lat,
                'lon': lon
            })
            
        except ProjError as e:  # ✅ دیگر خطا نمی‌دهد
            return jsonify({'success': False, 'message': f'خطا در تبدیل مختصات: {str(e)}'}), 500
        except ValueError as e:
            return jsonify({'success': False, 'message': f'مقدار نامعتبر: {str(e)}'}), 400
        except Exception as e:
            db.session.rollback()
            print(f"Error in utm_picker: {e}")
            return jsonify({'success': False, 'message': f'خطای داخلی: {str(e)}'}), 500
    
    # دریافت تاریخچه مختصات کاربر
    user_coordinates = UTMCoordinate.query.filter_by(user_id=current_user.id).order_by(UTMCoordinate.created_at.desc()).all()
    return render_template('utm_picker.html', user_coordinates=user_coordinates)

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
