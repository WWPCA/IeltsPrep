"""
Integrate assessment products with the existing subscription system.
This script makes the necessary changes to routes.py to support the new product types.
"""

from main import app
from models import db, User, CompletePracticeTest
import os
import sys
import json
import re

def integrate_assessment_products():
    """Make necessary changes to integrate assessment products."""
    
    print("Integrating assessment products with the subscription system...")
    
    # First, check if we have all the required files
    routes_path = 'routes.py'
    if not os.path.exists(routes_path):
        print(f"Error: {routes_path} not found")
        sys.exit(1)
    
    # Read the existing routes file
    with open(routes_path, 'r') as f:
        routes_content = f.read()
    
    # Define product info and pricing
    products_info = """
    # Assessment product types and pricing
    assessment_products = {
        'academic_writing': {
            'name': 'Academic Writing Assessment',
            'description': 'Complete Academic Writing assessment with Task 1 and Task 2',
            'price': 25,
        },
        'academic_speaking': {
            'name': 'Academic Speaking Assessment',
            'description': 'Complete Academic Speaking assessment with all three parts',
            'price': 25,
        },
        'general_writing': {
            'name': 'General Training Writing Assessment',
            'description': 'Complete General Training Writing assessment with Task 1 and Task 2',
            'price': 25,
        },
        'general_speaking': {
            'name': 'General Training Speaking Assessment',
            'description': 'Complete General Training Speaking assessment with all three parts',
            'price': 25,
        }
    }
    """
    
    # Define new route for assessment products page
    assessment_products_route = """
@app.route('/assessment-products')
def assessment_products():
    """Display available assessment products"""
    # Detect country for pricing
    if current_user.is_authenticated and current_user.region:
        country_code = current_user.region[:2].upper()  # Use the first two characters of region
    else:
        # Get country from IP address
        client_ip = request.remote_addr
        country_code, country_name = get_country_from_ip(client_ip)
    
    # Get pricing based on country (same function used in subscribe)
    pricing = get_pricing_for_country(country_code)
    
    # Get user's test preference for product selection
    test_preference = "academic"  # Default
    if current_user.is_authenticated:
        test_preference = current_user.test_preference
    
    return render_template('assessment_products.html', 
                           title='IELTS Assessment Products', 
                           assessment_products=assessment_products,
                           pricing=pricing,
                           test_preference=test_preference,
                           country_code=country_code)
"""
    
    # Define function to assign assessment sets
    assign_assessment_sets_func = """
def assign_assessment_sets(user, product_id):
    """Assign assessment sets to the user for the given product."""
    # Get all available sets for this product type
    sets = CompletePracticeTest.query.filter_by(
        product_type=product_id,
        status='active'
    ).all()
    
    if not sets or len(sets) == 0:
        print(f"No assessment sets found for product {product_id}")
        return
    
    print(f"Found {len(sets)} assessment sets for product {product_id}")
    
    # Get user's test history
    test_history = user.test_history if user.test_history else []
    
    # Find the most recent purchase
    purchase = None
    for item in reversed(test_history):
        if item.get('product_id') == product_id and not item.get('sets_assigned', False):
            purchase = item
            break
    
    if not purchase:
        print(f"No unassigned purchase found for product {product_id}")
        return
    
    # Assign up to 4 sets
    set_ids = []
    for i, test_set in enumerate(sets[:4]):
        set_ids.append(test_set.id)
    
    # Update purchase with assigned sets
    purchase['assigned_sets'] = set_ids
    purchase['sets_assigned'] = True
    
    # Update user's test history
    for i, item in enumerate(test_history):
        if item.get('date') == purchase.get('date') and item.get('product_id') == product_id:
            test_history[i] = purchase
            break
    
    user.test_history = test_history
    
    # Commit changes
    db.session.commit()
    
    print(f"Assigned {len(set_ids)} assessment sets to user {user.id} for product {product_id}")
"""
    
    # 1. Add the assessment product info after the imports
    import_section_end = routes_content.find("app = Flask(__name__)")
    if import_section_end == -1:
        import_section_end = routes_content.find("# Routes")
    
    if import_section_end != -1:
        updated_content = routes_content[:import_section_end] + products_info + routes_content[import_section_end:]
    else:
        updated_content = products_info + "\n" + routes_content
    
    # 2. Add the assessment_products route after the subscribe route
    subscribe_route_end = updated_content.find("@app.route('/checkout-review'")
    if subscribe_route_end != -1:
        updated_content = updated_content[:subscribe_route_end] + assessment_products_route + updated_content[subscribe_route_end:]
    
    # 3. Add the assign_assessment_sets function before the end of the file
    if updated_content.endswith("if __name__ == '__main__':\n    app.run(debug=True)"):
        updated_content = updated_content.replace("if __name__ == '__main__':\n    app.run(debug=True)", 
                                              assign_assessment_sets_func + "\n\nif __name__ == '__main__':\n    app.run(debug=True)")
    else:
        updated_content += "\n\n" + assign_assessment_sets_func
    
    # 4. Modify the checkout-review route to handle assessment products
    checkout_review_pattern = r"@app\.route\('/checkout-review', methods=\['POST'\]\)\ndef checkout_review\(\):(.*?)return redirect\(url_for\('practice_index'\)\)"
    checkout_review_match = re.search(checkout_review_pattern, updated_content, re.DOTALL)
    
    if checkout_review_match:
        old_checkout_review = checkout_review_match.group(0)
        
        # Add support for assessment products
        new_checkout_review = old_checkout_review.replace(
            "# Check if we're using new plan format",
            """# Check if we're using new plan format or if it's an assessment product
        if product_id in assessment_products:
            # For assessment product purchase
            product = assessment_products[product_id]
            package = 'assessment'
        el"""
        )
        
        updated_content = updated_content.replace(old_checkout_review, new_checkout_review)
    
    # 5. Modify the payment_success route to handle assessment products
    payment_success_pattern = r"@app\.route\('/payment-success'\)\ndef payment_success\(\):(.*?)return redirect\(url_for\('dashboard'\)\)"
    payment_success_match = re.search(payment_success_pattern, updated_content, re.DOTALL)
    
    if payment_success_match:
        old_payment_success = payment_success_match.group(0)
        
        # Get the indentation level
        indentation = re.search(r"(\s+)if request\.args\.get\('session_id'\):", old_payment_success).group(1)
        
        # Add assessment product handling
        assessment_product_code = f"""
{indentation}# Check if this is an assessment product purchase
{indentation}if 'checkout' in session and session['checkout'].get('product_id') in assessment_products:
{indentation}    product_id = session['checkout'].get('product_id')
{indentation}    
{indentation}    # Add the product to user's account
{indentation}    if current_user.is_authenticated:
{indentation}        # Get user's test history
{indentation}        test_history = current_user.test_history if current_user.test_history else []
{indentation}        
{indentation}        # Add the product to user's test history
{indentation}        purchase = {{
{indentation}            'date': datetime.utcnow().isoformat(),
{indentation}            'product_id': product_id,
{indentation}            'product': assessment_products[product_id]['name'],
{indentation}            'amount': assessment_products[product_id]['price'],
{indentation}            'sets_assigned': False
{indentation}        }}
{indentation}        
{indentation}        test_history.append(purchase)
{indentation}        current_user.test_history = test_history
{indentation}        
{indentation}        # Set the user's new product type
{indentation}        current_user.subscription_status = 'active'
{indentation}        
{indentation}        # No expiry date for permanent access
{indentation}        # current_user.subscription_expiry = None
{indentation}        
{indentation}        # Commit changes
{indentation}        db.session.commit()
{indentation}        
{indentation}        # Assign assessment sets
{indentation}        assign_assessment_sets(current_user, product_id)
{indentation}        
{indentation}        flash(f'Thank you for your purchase! Your {{assessment_products[product_id]["name"]}} is now active.', 'success')
{indentation}        
{indentation}        # Mark payment as processed
{indentation}        session['checkout']['processed'] = True
{indentation}        
{indentation}        # Redirect based on product type
{indentation}        if product_id.endswith('_writing'):
{indentation}            return redirect(url_for('practice_test_list', test_type='writing'))
{indentation}        elif product_id.endswith('_speaking'):
{indentation}            return redirect(url_for('practice_test_list', test_type='speaking'))
{indentation}        else:
{indentation}            return redirect(url_for('dashboard'))
"""
        
        # Insert the assessment product code right after the session_id check
        insertion_point = re.search(r"(\s+)if request\.args\.get\('session_id'\):", old_payment_success).end()
        new_payment_success = old_payment_success[:insertion_point] + assessment_product_code + old_payment_success[insertion_point:]
        
        updated_content = updated_content.replace(old_payment_success, new_payment_success)
    
    # Write the updated content back to the file
    with open(routes_path, 'w') as f:
        f.write(updated_content)
    
    print("Assessment products integrated with the subscription system.")
    
    # Create template for assessment products page
    create_assessment_products_template()

def create_assessment_products_template():
    """Create template for assessment products page."""
    
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    template_path = os.path.join(templates_dir, 'assessment_products.html')
    
    # Skip if file already exists
    if os.path.exists(template_path):
        print(f"Template already exists at {template_path}")
        return
    
    template_content = """{% extends "base.html" %}

{% block content %}
<div class="container mt-5">
    <div class="row mb-4">
        <div class="col">
            <h1>IELTS Assessment Products</h1>
            <p class="lead">Get detailed AI-powered assessments for IELTS Writing and Speaking tasks</p>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-header bg-primary text-white">
                    <h3>Academic Writing Assessment</h3>
                </div>
                <div class="card-body">
                    <p>Get detailed feedback on your Academic Writing Task 1 and Task 2 responses.</p>
                    <ul>
                        <li>Graph/chart description assessment (Task 1)</li>
                        <li>Essay writing assessment (Task 2)</li>
                        <li>Band scores for all IELTS criteria</li>
                        <li>Detailed feedback and improvement suggestions</li>
                    </ul>
                    <h4 class="price">{{ pricing.monthly_price }} USD</h4>
                </div>
                <div class="card-footer">
                    <a href="{{ url_for('checkout', plan='academic_writing') }}" class="btn btn-primary btn-block">Purchase Now</a>
                </div>
            </div>
        </div>
        
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-header bg-success text-white">
                    <h3>Academic Speaking Assessment</h3>
                </div>
                <div class="card-body">
                    <p>Practice all three parts of the IELTS Academic Speaking test with AI assessment.</p>
                    <ul>
                        <li>Introduction and interview practice (Part 1)</li>
                        <li>Individual long turn with preparation (Part 2)</li>
                        <li>Two-way discussion practice (Part 3)</li>
                        <li>Detailed feedback on pronunciation, fluency, vocabulary, and grammar</li>
                    </ul>
                    <h4 class="price">{{ pricing.monthly_price }} USD</h4>
                </div>
                <div class="card-footer">
                    <a href="{{ url_for('checkout', plan='academic_speaking') }}" class="btn btn-success btn-block">Purchase Now</a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-header bg-info text-white">
                    <h3>General Training Writing Assessment</h3>
                </div>
                <div class="card-body">
                    <p>Get detailed feedback on your General Training Writing Task 1 and Task 2 responses.</p>
                    <ul>
                        <li>Letter writing assessment (Task 1)</li>
                        <li>Essay writing assessment (Task 2)</li>
                        <li>Band scores for all IELTS criteria</li>
                        <li>Detailed feedback and improvement suggestions</li>
                    </ul>
                    <h4 class="price">{{ pricing.monthly_price }} USD</h4>
                </div>
                <div class="card-footer">
                    <a href="{{ url_for('checkout', plan='general_writing') }}" class="btn btn-info btn-block">Purchase Now</a>
                </div>
            </div>
        </div>
        
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-header bg-warning text-dark">
                    <h3>General Training Speaking Assessment</h3>
                </div>
                <div class="card-body">
                    <p>Practice all three parts of the IELTS General Training Speaking test with AI assessment.</p>
                    <ul>
                        <li>Introduction and interview practice (Part 1)</li>
                        <li>Individual long turn with preparation (Part 2)</li>
                        <li>Two-way discussion practice (Part 3)</li>
                        <li>Detailed feedback on pronunciation, fluency, vocabulary, and grammar</li>
                    </ul>
                    <h4 class="price">{{ pricing.monthly_price }} USD</h4>
                </div>
                <div class="card-footer">
                    <a href="{{ url_for('checkout', plan='general_speaking') }}" class="btn btn-warning text-dark btn-block">Purchase Now</a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col">
            <p class="text-center">
                <a href="{{ url_for('subscribe') }}" class="btn btn-outline-secondary">View Complete Test Packages</a>
            </p>
        </div>
    </div>
</div>
{% endblock %}"""

    # Write the template content to the file
    with open(template_path, 'w') as f:
        f.write(template_content)
    
    print(f"Created assessment products template at {template_path}")