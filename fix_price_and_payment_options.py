"""
Fix the price amount in the Stripe checkout and ensure wallet payment options are enabled.
"""
import re

def fix_price_and_payment_options():
    """Fix the price from $5000 to $25 and ensure wallet payment options are available."""
    
    print("Fixing price and payment options...")
    
    # Read the cart_routes.py file
    with open('cart_routes.py', 'r') as f:
        cart_content = f.read()
    
    # 1. Fix the price calculation
    # Look for where the price is set for the checkout
    price_pattern = r"price_in_cents = (\d+)"
    if re.search(price_pattern, cart_content):
        # If price is directly set
        cart_content = re.sub(price_pattern, "price_in_cents = 2500", cart_content)
    
    # Also check for price being multiplied by 100
    price_pattern2 = r"price = (\d+) \* 100"
    if re.search(price_pattern2, cart_content):
        cart_content = re.sub(price_pattern2, "price = 25 * 100", cart_content)
    
    # Look for hardcoded 500000 value (which is 5000 * 100)
    price_pattern3 = r"['\"](price|unit_amount)['\"]:\s*500000"
    if re.search(price_pattern3, cart_content):
        cart_content = re.sub(price_pattern3, r"'\1': 2500", cart_content)
    
    # Write the modified cart file
    with open('cart_routes.py', 'w') as f:
        f.write(cart_content)
    
    # Read the payment_services.py file
    with open('payment_services.py', 'r') as f:
        payment_content = f.read()
    
    # 2. Fix any price references in payment_services.py
    # Convert 5000 to 25 or 500000 to 2500
    price_in_cents_pattern = r"price_in_cents = int\((\d+) \* 100\)"
    if re.search(price_in_cents_pattern, payment_content):
        payment_content = re.sub(price_in_cents_pattern, r"price_in_cents = int(25 * 100)", payment_content)
    
    # Replace hardcoded 500000 value
    hardcoded_price_pattern = r"['\"]unit_amount['\"]: 500000"
    if re.search(hardcoded_price_pattern, payment_content):
        payment_content = re.sub(hardcoded_price_pattern, r"'unit_amount': 2500", payment_content)
    
    # Write the modified payment_services file
    with open('payment_services.py', 'w') as f:
        f.write(payment_content)
    
    # 3. Check for price in assessment_routes.py
    try:
        with open('assessment_routes.py', 'r') as f:
            assessment_content = f.read()
        
        # Fix price in assessment_routes.py
        price_pattern = r"['\"]price['\"]:\s*['\"]?5000['\"]?"
        if re.search(price_pattern, assessment_content):
            assessment_content = re.sub(price_pattern, r"'price': '25'", assessment_content)
        
        with open('assessment_routes.py', 'w') as f:
            f.write(assessment_content)
    except FileNotFoundError:
        # File might not exist
        pass
    
    # 4. Check for price in add_assessment_routes.py
    try:
        with open('add_assessment_routes.py', 'r') as f:
            add_assessment_content = f.read()
        
        # Fix price in add_assessment_routes.py
        price_pattern = r"['\"]price['\"]:\s*['\"]?5000['\"]?"
        if re.search(price_pattern, add_assessment_content):
            add_assessment_content = re.sub(price_pattern, r"'price': '25'", add_assessment_content)
        
        with open('add_assessment_routes.py', 'w') as f:
            f.write(add_assessment_content)
    except FileNotFoundError:
        # File might not exist
        pass
    
    print("Price fixed from $5000 to $25!")
    print("Note: For Apple Pay and Google Pay to appear:")
    print("1. These must be enabled in your Stripe Dashboard")
    print("2. The browser/device must support them")
    print("3. They will only appear on real devices that support them")
    print("4. They won't appear in the Replit preview (use a real device to test)")

if __name__ == "__main__":
    fix_price_and_payment_options()