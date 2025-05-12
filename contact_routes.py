"""
Contact Us form functionality for IELTS GenAI Prep.
This module provides routes for the contact form.
"""
import os
from flask import flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, EmailField
from wtforms.validators import DataRequired, Email, Length

class ContactForm(FlaskForm):
    """Contact form with name, email, and message fields."""
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Your Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])

def add_contact_routes(app):
    """Add contact form routes to the application."""
    
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        """Display and process the contact form."""
        form = ContactForm()
        
        if request.method == 'POST' and form.validate_on_submit():
            # Process form submission
            name = form.name.data
            email = form.email.data
            message = form.message.data
            
            # Send the contact form message to the backend email
            from email_service import send_email
            
            # Email subject and content
            subject = f"Contact Form Submission from {name}"
            text_body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"
            
            # Send the email to the admin
            admin_email = os.environ.get('ADMIN_EMAIL', 'worldwidepublishingco@gmail.com')
            send_email(admin_email, subject, text_body)
            
            # Display success message without revealing the email address
            flash(f"Thank you, {name}! Your message has been received. We'll get back to you shortly.", "success")
            return redirect(url_for('contact'))
        
        return render_template('contact.html', form=form)
