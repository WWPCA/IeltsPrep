"""
Update assessment product routes with the new Assessment model.
This script replaces the integrate_assessment_products.py file to use the Assessment model
instead of CompletePracticeTest.
"""

from main import app
from models import db, User, Assessment
import os
import sys
import json
import re
from datetime import datetime, timedelta

def update_assessment_product_routes():
    """Update assessment product routes to use the Assessment model."""
    
    print("Updating assessment product routes to use the Assessment model...")
    
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
            'assessments_included': 4,
            'validity_days': 30
        },
        'academic_speaking': {
            'name': 'Academic Speaking Assessment',
            'description': 'Complete Academic Speaking assessment with all three parts',
            'price': 25,
            'assessments_included': 4,
            'validity_days': 30
        },
        'general_writing': {
            'name': 'General Training Writing Assessment',
            'description': 'Complete General Training Writing assessment with Task 1 and Task 2',
            'price': 25,
            'assessments_included': 4,
            'validity_days': 30
        },
        'general_speaking': {
            'name': 'General Training Speaking Assessment',
            'description': 'Complete General Training Speaking assessment with all three parts',
            'price': 25,
            'assessments_included': 4,
            'validity_days': 30
        }
    }
    """
    
    # Define new route for assessment products page
    assessment_products_route = """
@app.route('/assessment-products')
def assessment_products():
    """Display available assessment products"""
    # No country-specific pricing - fixed at $25 for all assessment packages
    pricing = {'monthly_price': 25}
    
    # Get user's assessment preference for product selection
    assessment_preference = "academic"  # Default
    if current_user.is_authenticated and hasattr(current_user, 'assessment_preference'):
        assessment_preference = current_user.assessment_preference
    
    return render_template('assessment_products.html', 
                           title='IELTS GenAI Assessment Products', 
                           assessment_products=assessment_products,
                           pricing=pricing,
                           assessment_preference=assessment_preference)
"""
    
    # Define function to assign assessment sets
    assign_assessment_sets_func = """
def assign_assessment_sets(user, product_id):
    """Assign assessment sets to the user for the given product."""
    from assessment_assignment_service import assign_assessments_to_user
    
    # Determine assessment type from product ID
    assessment_type = product_id.split('_')[0]  # 'academic' or 'general'
    
    # Number of assessments included in the package
    num_assessments = assessment_products[product_id]['assessments_included']
    
    # Validity period in days
    validity_days = assessment_products[product_id]['validity_days']
    
    # Assign assessments to user
    assigned_assessment_ids, success = assign_assessments_to_user(
        user.id, 
        assessment_type,
        num_assessments,
        validity_days
    )
    
    if success:
        print(f"Assigned {len(assigned_assessment_ids)} assessments to user {user.id} for product {product_id}")
    else:
        print(f"Failed to assign assessments to user {user.id} for product {product_id}")
    
    return success
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
{indentation}        # Set the user's account to active (required for assessment access)
{indentation}        current_user.account_activated = True
{indentation}        
{indentation}        # Set the user's new assessment package status
{indentation}        current_user.assessment_package_status = 'active'
{indentation}        
{indentation}        # Set the expiry date for the assessment package
{indentation}        validity_days = assessment_products[product_id]['validity_days']
{indentation}        current_user.assessment_package_expiry = datetime.utcnow() + timedelta(days=validity_days)
{indentation}        
{indentation}        # Update payment record
{indentation}        new_payment = PaymentRecord(
{indentation}            user_id=current_user.id,
{indentation}            amount=assessment_products[product_id]['price'],
{indentation}            payment_type='stripe',
{indentation}            product_id=product_id,
{indentation}            product_name=assessment_products[product_id]['name'],
{indentation}            status='completed',
{indentation}            timestamp=datetime.utcnow()
{indentation}        )
{indentation}        
{indentation}        db.session.add(new_payment)
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
{indentation}        assessment_type = product_id.split('_')[1]  # 'writing' or 'speaking'
{indentation}        return redirect(url_for('assessment_list', assessment_type=assessment_type))
"""
        
        # Insert the assessment product code right after the session_id check
        insertion_point = re.search(r"(\s+)if request\.args\.get\('session_id'\):", old_payment_success).end()
        new_payment_success = old_payment_success[:insertion_point] + assessment_product_code + old_payment_success[insertion_point:]
        
        updated_content = updated_content.replace(old_payment_success, new_payment_success)
    
    # Write the updated content back to the file
    with open(routes_path, 'w') as f:
        f.write(updated_content)
    
    print("Assessment product routes updated to use the Assessment model.")
    
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
    
    template_content = """{% extends "layout.html" %}

{% block content %}
<div class="container mt-5">
    <div class="row mb-4">
        <div class="col">
            <h1>IELTS GenAI Assessment Products</h1>
            <p class="lead">Get detailed assessments for IELTS Writing and Speaking tasks powered by TrueScore® and Elaris® assessment engines</p>
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
                        <li>4 complete assessments included</li>
                        <li>Graph/chart description assessment (Task 1)</li>
                        <li>Essay writing assessment (Task 2)</li>
                        <li>Band scores for all IELTS criteria</li>
                        <li>Detailed feedback and improvement suggestions</li>
                        <li>Valid for 30 days from purchase</li>
                    </ul>
                    <h4 class="price">${{ pricing.monthly_price }} USD</h4>
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
                    <p>Practice all three parts of the IELTS Academic Speaking test with TrueScore® assessment.</p>
                    <ul>
                        <li>4 complete assessments included</li>
                        <li>Introduction and interview practice (Part 1)</li>
                        <li>Individual long turn with preparation (Part 2)</li>
                        <li>Two-way discussion practice (Part 3)</li>
                        <li>Detailed feedback on pronunciation, fluency, vocabulary, and grammar</li>
                        <li>Valid for 30 days from purchase</li>
                    </ul>
                    <h4 class="price">${{ pricing.monthly_price }} USD</h4>
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
                        <li>4 complete assessments included</li>
                        <li>Letter writing assessment (Task 1)</li>
                        <li>Essay writing assessment (Task 2)</li>
                        <li>Band scores for all IELTS criteria</li>
                        <li>Detailed feedback and improvement suggestions</li>
                        <li>Valid for 30 days from purchase</li>
                    </ul>
                    <h4 class="price">${{ pricing.monthly_price }} USD</h4>
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
                    <p>Practice all three parts of the IELTS General Training Speaking test with Elaris® assessment.</p>
                    <ul>
                        <li>4 complete assessments included</li>
                        <li>Introduction and interview practice (Part 1)</li>
                        <li>Individual long turn with preparation (Part 2)</li>
                        <li>Two-way discussion practice (Part 3)</li>
                        <li>Detailed feedback on pronunciation, fluency, vocabulary, and grammar</li>
                        <li>Valid for 30 days from purchase</li>
                    </ul>
                    <h4 class="price">${{ pricing.monthly_price }} USD</h4>
                </div>
                <div class="card-footer">
                    <a href="{{ url_for('checkout', plan='general_speaking') }}" class="btn btn-warning text-dark btn-block">Purchase Now</a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col">
            <div class="card bg-light">
                <div class="card-body">
                    <h4>Why Choose IELTS GenAI Prep?</h4>
                    <p>Our platform features the ONLY GenAI assessor tools for IELTS in the world:</p>
                    <ul>
                        <li><strong>TrueScore®</strong> - The world's first IELTS assessment engine built specifically for Academic and General Training</li>
                        <li><strong>Elaris®</strong> - Advanced speaking assessment technology that evaluates pronunciation, fluency, vocabulary, and grammar</li>
                    </ul>
                    <p>All assessments provide detailed feedback aligned with official IELTS band descriptors to help you improve your score.</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
    
    # Write the template to file
    with open(template_path, 'w') as f:
        f.write(template_content)
    
    print(f"Created assessment products template at {template_path}")

if __name__ == "__main__":
    update_assessment_product_routes()