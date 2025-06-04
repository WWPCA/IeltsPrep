"""
Flask-WTF Forms for IELTS AI Prep Application
This module provides form classes with proper CSRF protection.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.recaptcha import RecaptchaField

class LoginForm(FlaskForm):
    """Login form with reCAPTCHA v2 integration"""
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    recaptcha = RecaptchaField()
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """Registration form with reCAPTCHA v2 integration"""
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Create Account')