"""
Update routes.py to integrate assessment products.
This script modifies the payment_success route to handle assessment products.
"""

import re
from add_assessment_routes import is_assessment_product

def update_routes():
    """Update routes.py to handle assessment products."""
    
    # Read routes.py
    with open('routes.py', 'r') as f:
        content = f.read()
    
    # Pattern to match the payment_success function
    payment_success_pattern = r'@app\.route\(\'/payment-success\'\)\ndef payment_success\(\):(.*?)return redirect\(url_for\(\'dashboard\'\)\)'
    payment_success_match = re.search(payment_success_pattern, content, re.DOTALL)
    
    if not payment_success_match:
        print("Could not find payment_success function in routes.py")
        return
    
    old_payment_success = payment_success_match.group(0)
    
    # Code to add to handle assessment products
    assessment_code = """
    # Check if this is an assessment product payment
    if 'checkout' in session and session['checkout'].get('product_id'):
        product_id = session['checkout'].get('product_id')
        from add_assessment_routes import is_assessment_product
        
        if is_assessment_product(product_id):
            print(f"Processing assessment product payment: {product_id}")
            
            # Mark payment as processed
            session['checkout']['processed'] = True
            
            # Process assessment product
            from payment_processor import process_assessment_product
            result = process_assessment_product(current_user, product_id)
            
            if result:
                flash(result['flash_message'], result['flash_category'])
                return redirect(result['redirect_url'])
    """
    
    # Find the insertion point - right before the else that handles expired subscriptions
    insertion_text = "# Add product to user's account"
    insertion_index = old_payment_success.find(insertion_text)
    
    if insertion_index == -1:
        insertion_text = "# Get subscription details from the URL"
        insertion_index = old_payment_success.find(insertion_text)
    
    if insertion_index == -1:
        print("Could not find insertion point in payment_success function")
        return
    
    # Get the indentation before the insertion point
    lines = old_payment_success[:insertion_index].split('\n')
    if len(lines) > 1:
        indentation = re.match(r'(\s*)', lines[-1]).group(1)
    else:
        indentation = '    '
    
    # Indent the assessment code
    assessment_code_indented = ''.join([indentation + line + '\n' for line in assessment_code.split('\n')])
    
    # Insert the assessment code
    new_payment_success = old_payment_success[:insertion_index] + assessment_code_indented + old_payment_success[insertion_index:]
    
    # Replace the old payment_success function with the new one
    updated_content = content.replace(old_payment_success, new_payment_success)
    
    # Write the updated content back to routes.py
    with open('routes.py', 'w') as f:
        f.write(updated_content)
    
    print("Updated routes.py to handle assessment products.")

if __name__ == '__main__':
    update_routes()