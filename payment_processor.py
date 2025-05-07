"""
Process payments for assessment products.
This module handles payment processing for assessment products.
"""

from add_assessment_routes import assessment_products, assign_assessment_sets, is_assessment_product
from flask import flash, redirect, url_for
from datetime import datetime
import json

def process_assessment_product(user, product_id):
    """Process a successful payment for an assessment product."""
    # Get product details
    if not is_assessment_product(product_id):
        print(f"Invalid product ID: {product_id}")
        return None
    
    product = assessment_products[product_id]
    
    # Add the product to user's test history
    test_history = user.test_history if user.test_history else []
    
    # Add the product to user's test history
    purchase = {
        'date': datetime.utcnow().isoformat(),
        'product_id': product_id,
        'product': product['name'],
        'amount': product['price'],
        'sets_assigned': False
    }
    
    test_history.append(purchase)
    user.test_history = test_history
    
    # Assign assessment sets
    assign_assessment_sets(user, product_id)
    
    print(f"Added {product['name']} to user {user.id}'s account")
    
    # Create appropriate redirect based on product type
    if product_id.endswith('_writing'):
        redirect_url = url_for('practice_test_list', test_type='writing')
    elif product_id.endswith('_speaking'):
        redirect_url = url_for('practice_test_list', test_type='speaking')
    else:
        redirect_url = url_for('dashboard')
    
    flash_message = f'Thank you for your purchase! Your {product["name"]} is now active.'
    
    return {
        'redirect_url': redirect_url,
        'flash_message': flash_message,
        'flash_category': 'success'
    }