"""
Fix prices in the assessment products to be $25 instead of $5000.
"""

def fix_assessment_prices():
    """Update the assessment product prices in add_assessment_routes.py."""
    
    print("Fixing assessment product prices...")
    
    # Read the add_assessment_routes.py file
    with open('add_assessment_routes.py', 'r') as f:
        content = f.read()
    
    # The prices appear to be in cents already in this file (2500 cents = $25)
    # but we'll check and make sure they're correct
    
    # Replace 5000 with 2500 in any product prices
    if '\'price\': 5000,' in content or '"price": 5000,' in content:
        content = content.replace('\'price\': 5000,', '\'price\': 2500,')
        content = content.replace('"price": 5000,', '"price": 2500,')
        
        print("Updated $50 prices to $25")
    elif '\'price\': 500000,' in content or '"price": 500000,' in content:
        content = content.replace('\'price\': 500000,', '\'price\': 2500,')
        content = content.replace('"price": 500000,', '"price": 2500,')
        
        print("Updated $5000 prices to $25")
    else:
        print("No price updates needed in add_assessment_routes.py")
    
    # Write the updated file
    with open('add_assessment_routes.py', 'w') as f:
        f.write(content)
    
    # Also check for unit_amount in session creation
    try:
        with open('cart_routes.py', 'r') as f:
            cart_content = f.read()
        
        if "'unit_amount': 500000" in cart_content:
            cart_content = cart_content.replace("'unit_amount': 500000", "'unit_amount': 2500")
            with open('cart_routes.py', 'w') as f:
                f.write(cart_content)
            print("Fixed unit_amount in cart_routes.py")
    except:
        print("Could not check cart_routes.py")
    
    # Also check display price in templates
    try:
        with open('templates/assessment_products.html', 'r') as f:
            template_content = f.read()
        
        if '$5000' in template_content:
            template_content = template_content.replace('$5000', '$25')
            with open('templates/assessment_products.html', 'w') as f:
                f.write(template_content)
            print("Fixed display price in assessment_products.html")
        elif '$50' in template_content:
            template_content = template_content.replace('$50', '$25')
            with open('templates/assessment_products.html', 'w') as f:
                f.write(template_content)
            print("Fixed display price in assessment_products.html")
    except:
        print("Could not check templates/assessment_products.html")
    
    print("Assessment product prices fixed!")

if __name__ == "__main__":
    fix_assessment_prices()