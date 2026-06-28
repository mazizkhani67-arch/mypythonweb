# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,SelectField,TextAreaField,FloatField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange,Length


class RegistrationForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('ایمیل', validators=[DataRequired(), Email()])
    phone = StringField('تلفن', validators=[DataRequired(), Length(min=11, max=11)])
    # اضافه کردن فیلد انتخاب نوع کاربر
    password = PasswordField('رمز عبور', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('تأیید رمز عبور', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('ثبت نام')


class LoginForm(FlaskForm):
    
    email = StringField('ایمیل', validators=[DataRequired(), Email()])
    password = PasswordField('رمز عبور', validators=[DataRequired()])
    remember_me = BooleanField('مرا به خاطر بسپار')
    submit = SubmitField('ورود')

# app/form.py - اصلاح کلاس RequestForm
class RequestForm(FlaskForm):
    name = StringField('نام و نام خانوادگی', validators=[DataRequired(), Length(max=100)])
    email = StringField('ایمیل', validators=[DataRequired(), Email()])
    phone = StringField('تلفن تماس', validators=[DataRequired(), Length(min=11, max=11)])
    message = TextAreaField('پیام شما', validators=[DataRequired()])
    submit = SubmitField('ارسال پیام')

class UTMCoodinateForm(FlaskForm):
    easting = FloatField('Easting (مختصات شرقی)', 
                         validators=[DataRequired(), NumberRange(min=100000, max=999999)])
    northing = FloatField('Northing (مختصات شمالی)', 
                          validators=[DataRequired(), NumberRange(min=0, max=10000000)])
    zone = IntegerField('Zone (ناحیه UTM)', 
                        validators=[DataRequired(), NumberRange(min=1, max=60)])
    hemisphere = SelectField('نیمکره', choices=[('N', 'شمالی'), ('S', 'جنوبی')])
    submit = SubmitField('نمایش روی نقشه')


    # app/forms.py - اضافه کردن فرم‌های جدید

from wtforms import SelectField, TextAreaField, FileField, IntegerField, HiddenField, FloatField
from wtforms.validators import Optional

class ProjectTypeForm(FlaskForm):
    code = IntegerField('کد نوع پروژه', validators=[DataRequired()])
    name = StringField('نام نوع پروژه', validators=[DataRequired()])
    parent_code = SelectField('دسته اصلی', coerce=int, choices=[(0, 'دسته اصلی')])
    submit = SubmitField('ذخیره')

# app/forms.py - اضافه کردن فیلد title به ProjectForm

class ProjectForm(FlaskForm):
    title = StringField('عنوان پروژه', validators=[DataRequired(), Length(max=200)])
    project_type_code = SelectField('نوع پروژه', coerce=int, validators=[Optional()])
    employer_id = SelectField('کارفرما', coerce=int, validators=[DataRequired()])
    new_employer_name = StringField('نام کاربر جدید', validators=[Optional()])
    new_employer_email = StringField('ایمیل کاربر جدید', validators=[Optional(), Email()])
    new_employer_phone = StringField('تلفن کاربر جدید', validators=[Optional()])
    location_lat = FloatField('عرض جغرافیایی', validators=[Optional()])
    location_lon = FloatField('طول جغرافیایی', validators=[Optional()])
    address = TextAreaField('آدرس پروژه', validators=[Optional()])
    description = TextAreaField('توضیحات', validators=[Optional()])
    cover_image = FileField('فایل روکش پروژه')
    project_zip = FileField('فایل زیپ پروژه')
    submit = SubmitField('ذخیره پروژه')

class ChecklistUpdateForm(FlaskForm):
    user_registered = BooleanField('ثبت کاربر به عنوان کارفرما')
    project_registered = BooleanField('ثبت پروژه')
    employer_confirmed = BooleanField('تایید کارفرما')
    album_completed = BooleanField('اتمام آلبوم')
    engineering_approved = BooleanField('تایید نظام مهندسی')
    settlement_done = BooleanField('تسویه حساب')
    delivered_to_client = BooleanField('تحویل به مشتری')
    send_message = BooleanField('آیا نیاز به ارسال پیام هست؟')
    submit = SubmitField('به‌روزرسانی پیشرفت')

    # app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FileField, IntegerField, FloatField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange

# ... سایر فرم‌ها ...

class SMSForm(FlaskForm):
    recipient = StringField('گیرنده (شماره تلفن)', validators=[DataRequired(), Length(min=11, max=11)])
    project_id = SelectField('پروژه مرتبط', coerce=int, validators=[Optional()])
    custom_step = StringField('مرحله سفارشی', validators=[Optional()])
    message = TextAreaField('پیش‌نمایش پیام', validators=[DataRequired()])
    submit = SubmitField('ارسال پیامک')