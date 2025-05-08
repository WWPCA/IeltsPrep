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
            
            # In a production environment, you would send an email here
            # For now, we'll just display a success message
            flash(f"Thank you, {name}! Your message has been received. We'll get back to you shortly at {email}.", "success")
            return redirect(url_for('contact'))
        
        return render_template('contact.html', form=form)
