# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,SelectField,TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length


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