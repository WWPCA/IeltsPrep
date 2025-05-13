"""
DEPRECATED: Update assessment package routes to handle our new product types.

This file should no longer be actively used as we've moved to cart-based checkout.
The implementation was functional but has been superceded by cart_routes.py.
Kept for historical reference.

Previously named update_subscription_routes.py - renamed for terminology consistency.
"""

from main import app
from models import db, User, Assessment
from routes import assessment_package_required
from payment_services import create_stripe_checkout_session
from datetime import datetime, timedelta
from flask import flash, redirect, url_for, render_template, request, jsonify, session
from flask_login import current_user
import os
import json

def update_assessment_package_routes():
    """Update the routes to handle our new product types."""
    
    # This file is deprecated and kept only for historical reference
    # See cart_routes.py for the current implementation
    return "Deprecated: use cart_routes.py instead"