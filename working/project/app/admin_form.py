from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class UserForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('ایمیل', validators=[DataRequired(), Email()])
    phone = StringField('تلفن', validators=[DataRequired(), Length(min=11, max=11)])
    password = PasswordField('رمز عبور', validators=[DataRequired(), Length(min=6)])
    usertype = SelectField('نوع کاربر', choices=[
        ('user', 'کاربر عادی'),
        ('admin', 'ادمین'),
        ('super_admin', 'سوپر ادمین')
    ])
    submit = SubmitField('ذخیره')