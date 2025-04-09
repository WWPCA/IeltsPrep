from app import app, db
from models import PaymentMethod

def init_payment_methods():
    """Initialize the payment methods in the database."""
    with app.app_context():
        # Clear existing payment methods
        PaymentMethod.query.delete()
        
        # Regional Payment Methods
        regional_methods = [
            # India
            {"name": "Razorpay", "region": "India", "display_order": 1},
            
            # Pakistan
            {"name": "JazzCash", "region": "Pakistan", "display_order": 1},
            {"name": "Easypaisa", "region": "Pakistan", "display_order": 1},
            
            # Bangladesh
            {"name": "bKash", "region": "Bangladesh", "display_order": 1},
            {"name": "Nagad", "region": "Bangladesh", "display_order": 1},
            
            # Sri Lanka
            {"name": "LankaPay", "region": "Sri Lanka", "display_order": 1},
            {"name": "Direct Pay", "region": "Sri Lanka", "display_order": 1},
            
            # Nepal
            {"name": "ConnectIPS", "region": "Nepal", "display_order": 1},
            {"name": "PrabhuPAY", "region": "Nepal", "display_order": 1},
            {"name": "eSewa", "region": "Nepal", "display_order": 1},
            
            # Saudi Arabia
            {"name": "STC Pay", "region": "Saudi Arabia", "display_order": 1},
            
            # UAE
            {"name": "Amazon Payment Services", "region": "UAE", "display_order": 1},
            
            # Japan
            {"name": "LINE Pay", "region": "Japan", "display_order": 1},
            {"name": "PayPay", "region": "Japan", "display_order": 1},
            {"name": "Suica/PASMO", "region": "Japan", "display_order": 1},
            
            # South Korea
            {"name": "KakaoPay", "region": "South Korea", "display_order": 1},
            {"name": "Naver Pay", "region": "South Korea", "display_order": 1},
            {"name": "ZeroPay", "region": "South Korea", "display_order": 1},
            
            # Eastern Europe
            {"name": "Revolut", "region": "Eastern Europe", "display_order": 1},
            
            # Poland
            {"name": "BLIK", "region": "Poland", "display_order": 1},
            
            # Netherlands
            {"name": "iDEAL", "region": "Netherlands", "display_order": 1},
            
            # Germany
            {"name": "Sofort", "region": "Germany", "display_order": 1},
            
            # France
            {"name": "Cartes Bancaires", "region": "France", "display_order": 1},
        ]
        
        # Global Payment Methods
        global_methods = [
            {"name": "Stripe", "region": None, "display_order": 2},
            {"name": "Google Pay", "region": None, "display_order": 2},
            {"name": "Apple Pay", "region": None, "display_order": 2},
            {"name": "Qiwi", "region": None, "display_order": 2},
            {"name": "PayPal", "region": None, "display_order": 2},
        ]
        
        # Add all payment methods
        for method_data in regional_methods + global_methods:
            method = PaymentMethod(**method_data)
            db.session.add(method)
        
        # Commit changes
        db.session.commit()
        print(f"Added {len(regional_methods)} regional and {len(global_methods)} global payment methods")

if __name__ == "__main__":
    init_payment_methods()