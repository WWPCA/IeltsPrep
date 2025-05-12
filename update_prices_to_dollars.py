"""
Update assessment product prices from cents to dollars throughout the codebase.

This script changes prices from cents (2500 = $25.00) to dollars (25.00) in all
relevant files to ensure consistency and reduce confusion.
"""

def update_prices_to_dollars():
    """Update all prices from cents to dollars in the codebase."""
    
    print("Updating prices from cents to dollars...")
    
    # 1. Update add_assessment_routes.py first (source of truth for product prices)
    try:
        with open('add_assessment_routes.py', 'r') as f:
            content = f.read()
        
        # Replace all price comments that mention cents
        content = content.replace("'price': 2500,  # Price in cents", "'price': 25,  # Price in dollars")
        
        # Replace any other price values that might be in cents
        for product in ['academic_writing', 'academic_speaking', 'general_writing', 'general_speaking']:
            content = content.replace(f"'{product}': {{\n        'name':", f"'{product}': {{\n        'name':")
        
        # Update any direct references to price
        content = content.replace("'price': 1500,  # Price in cents", "'price': 15,  # Price in dollars")
        content = content.replace("'price': 2000,  # Price in cents", "'price': 20,  # Price in dollars")
        
        with open('add_assessment_routes.py', 'w') as f:
            f.write(content)
        
        print("Updated prices in add_assessment_routes.py")
    except Exception as e:
        print(f"Error updating add_assessment_routes.py: {str(e)}")
    
    # 2. Check cart.py for any price handling
    try:
        with open('cart.py', 'r') as f:
            cart_content = f.read()
        
        # Add a comment to clarify price handling
        if "total = sum(item['price'] for item in session['cart'])" in cart_content:
            cart_content = cart_content.replace(
                "total = sum(item['price'] for item in session['cart'])",
                "# Prices are stored in dollars\n    total = sum(item['price'] for item in session['cart'])")
        
        with open('cart.py', 'w') as f:
            f.write(cart_content)
        
        print("Updated price handling in cart.py")
    except Exception as e:
        print(f"Error updating cart.py: {str(e)}")
    
    # 3. Update cart_routes.py to handle the dollar prices correctly with Stripe
    try:
        with open('cart_routes.py', 'r') as f:
            cart_routes_content = f.read()
        
        # Make sure we're converting dollars to cents for Stripe
        if "cart_total = cart.get_cart_total()" in cart_routes_content:
            updated_section = """    # Get total price (cart holds prices in dollars)
    cart_total = cart.get_cart_total()
    # Convert to cents for Stripe
    total_price = int(cart_total * 100)
    
    # Debug log to verify correct amount
    print(f"Cart total: ${cart_total} dollars -> Stripe amount: {total_price} cents")"""
            
            cart_routes_content = cart_routes_content.replace(
                "    # Get total price in cents (stripe requires amounts in cents)\n    cart_total = cart.get_cart_total()\n    total_price = int(cart_total * 100)\n    \n    # Debug log to verify correct amount\n    print(f\"Cart total: ${cart_total} -> Stripe amount: {total_price} cents\")",
                updated_section)
        
        with open('cart_routes.py', 'w') as f:
            f.write(cart_routes_content)
        
        print("Updated Stripe price conversion in cart_routes.py")
    except Exception as e:
        print(f"Error updating cart_routes.py: {str(e)}")
    
    # 4. Update payment_services.py to ensure consistency
    try:
        with open('payment_services.py', 'r') as f:
            payment_content = f.read()
        
        # Update any price conversion code
        if "price_in_cents = int(price)" in payment_content:
            payment_content = payment_content.replace(
                "price_in_cents = int(price)",
                "price_in_cents = int(price * 100)  # Convert dollars to cents for Stripe")
        
        with open('payment_services.py', 'w') as f:
            f.write(payment_content)
        
        print("Updated price handling in payment_services.py")
    except Exception as e:
        print(f"Error updating payment_services.py: {str(e)}")
    
    print("Price update complete!")
    print("All prices now consistently stored as dollars throughout the codebase.")
    print("Note: When sending to Stripe, prices are converted from dollars to cents as required.")

if __name__ == "__main__":
    update_prices_to_dollars()