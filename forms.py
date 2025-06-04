"""
Flask-WTF Forms for IELTS AI Prep Application
Following Google reCAPTCHA v2 documentation standards
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    """Login form with manual reCAPTCHA v2 integration per Google docs"""
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    # Manual reCAPTCHA handling as per Google documentation
    g_recaptcha_response = HiddenField('g-recaptcha-response')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """Registration form with manual reCAPTCHA v2 integration per Google docs"""
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    # Manual reCAPTCHA handling as per Google documentation
    g_recaptcha_response = HiddenField('g-recaptcha-response')
    submit = SubmitField('Create Account')