"""
Create a country-specific pricing table for the IELTS preparation app.
"""

from app import app, db
from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.exc import SQLAlchemyError

class CountryPricing(db.Model):
    """Table for storing country-specific pricing information."""
    id = Column(Integer, primary_key=True)
    country_code = Column(String(2), nullable=False, unique=True)
    country_name = Column(String(100), nullable=False)
    
    # Pricing for different subscription levels (in USD)
    monthly_price = Column(Float, nullable=False)
    quarterly_price = Column(Float, nullable=False)
    yearly_price = Column(Float, nullable=False)
    
    # Default country flag (for showing as default option)
    is_default = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<CountryPricing {self.country_name} - ${self.monthly_price}/month>"

# Sample country pricing data with a wide range of countries and appropriate pricing
COUNTRIES = [
    # High-income regions
    {"country_code": "US", "country_name": "United States", "monthly_price": 14.99, "quarterly_price": 39.99, "yearly_price": 149.99, "is_default": True},
    {"country_code": "CA", "country_name": "Canada", "monthly_price": 14.99, "quarterly_price": 39.99, "yearly_price": 149.99, "is_default": False},
    {"country_code": "GB", "country_name": "United Kingdom", "monthly_price": 11.99, "quarterly_price": 32.99, "yearly_price": 119.99, "is_default": False},
    {"country_code": "AU", "country_name": "Australia", "monthly_price": 15.99, "quarterly_price": 42.99, "yearly_price": 159.99, "is_default": False},
    {"country_code": "NZ", "country_name": "New Zealand", "monthly_price": 15.99, "quarterly_price": 42.99, "yearly_price": 159.99, "is_default": False},
    {"country_code": "SG", "country_name": "Singapore", "monthly_price": 14.99, "quarterly_price": 39.99, "yearly_price": 149.99, "is_default": False},
    {"country_code": "JP", "country_name": "Japan", "monthly_price": 14.99, "quarterly_price": 39.99, "yearly_price": 149.99, "is_default": False},
    {"country_code": "KR", "country_name": "South Korea", "monthly_price": 13.99, "quarterly_price": 37.99, "yearly_price": 139.99, "is_default": False},
    
    # Middle-income regions
    {"country_code": "CN", "country_name": "China", "monthly_price": 9.99, "quarterly_price": 26.99, "yearly_price": 99.99, "is_default": False},
    {"country_code": "BR", "country_name": "Brazil", "monthly_price": 8.99, "quarterly_price": 23.99, "yearly_price": 89.99, "is_default": False},
    {"country_code": "MX", "country_name": "Mexico", "monthly_price": 8.99, "quarterly_price": 23.99, "yearly_price": 89.99, "is_default": False},
    {"country_code": "RU", "country_name": "Russia", "monthly_price": 8.99, "quarterly_price": 23.99, "yearly_price": 89.99, "is_default": False},
    {"country_code": "TR", "country_name": "Turkey", "monthly_price": 7.99, "quarterly_price": 21.99, "yearly_price": 79.99, "is_default": False},
    {"country_code": "TH", "country_name": "Thailand", "monthly_price": 7.99, "quarterly_price": 21.99, "yearly_price": 79.99, "is_default": False},
    {"country_code": "MY", "country_name": "Malaysia", "monthly_price": 7.99, "quarterly_price": 21.99, "yearly_price": 79.99, "is_default": False},
    
    # Lower-middle-income regions
    {"country_code": "IN", "country_name": "India", "monthly_price": 4.99, "quarterly_price": 12.99, "yearly_price": 49.99, "is_default": False},
    {"country_code": "PH", "country_name": "Philippines", "monthly_price": 4.99, "quarterly_price": 12.99, "yearly_price": 49.99, "is_default": False},
    {"country_code": "VN", "country_name": "Vietnam", "monthly_price": 4.99, "quarterly_price": 12.99, "yearly_price": 49.99, "is_default": False},
    {"country_code": "ID", "country_name": "Indonesia", "monthly_price": 4.99, "quarterly_price": 12.99, "yearly_price": 49.99, "is_default": False},
    {"country_code": "EG", "country_name": "Egypt", "monthly_price": 4.99, "quarterly_price": 12.99, "yearly_price": 49.99, "is_default": False},
    {"country_code": "PK", "country_name": "Pakistan", "monthly_price": 4.99, "quarterly_price": 12.99, "yearly_price": 49.99, "is_default": False},
    {"country_code": "NG", "country_name": "Nigeria", "monthly_price": 4.99, "quarterly_price": 12.99, "yearly_price": 49.99, "is_default": False},
    
    # Low-income regions
    {"country_code": "KE", "country_name": "Kenya", "monthly_price": 2.99, "quarterly_price": 7.99, "yearly_price": 29.99, "is_default": False},
    {"country_code": "ET", "country_name": "Ethiopia", "monthly_price": 2.99, "quarterly_price": 7.99, "yearly_price": 29.99, "is_default": False},
    {"country_code": "TZ", "country_name": "Tanzania", "monthly_price": 2.99, "quarterly_price": 7.99, "yearly_price": 29.99, "is_default": False},
    {"country_code": "BD", "country_name": "Bangladesh", "monthly_price": 2.99, "quarterly_price": 7.99, "yearly_price": 29.99, "is_default": False},
    {"country_code": "NP", "country_name": "Nepal", "monthly_price": 2.99, "quarterly_price": 7.99, "yearly_price": 29.99, "is_default": False},
    
    # Special regions with high IELTS demand
    {"country_code": "AE", "country_name": "United Arab Emirates", "monthly_price": 12.99, "quarterly_price": 34.99, "yearly_price": 129.99, "is_default": False},
    {"country_code": "SA", "country_name": "Saudi Arabia", "monthly_price": 12.99, "quarterly_price": 34.99, "yearly_price": 129.99, "is_default": False},
]

def create_country_pricing_table():
    """Create the CountryPricing table and populate it with sample data."""
    with app.app_context():
        try:
            # Create the table
            db.create_all()
            
            # Check if data already exists
            existing_count = CountryPricing.query.count()
            if existing_count > 0:
                print(f"Country pricing data already exists ({existing_count} entries). Skipping initialization.")
                return
            
            # Insert sample data
            for country_data in COUNTRIES:
                country = CountryPricing(
                    country_code=country_data["country_code"],
                    country_name=country_data["country_name"],
                    monthly_price=country_data["monthly_price"],
                    quarterly_price=country_data["quarterly_price"],
                    yearly_price=country_data["yearly_price"],
                    is_default=country_data["is_default"]
                )
                db.session.add(country)
            
            db.session.commit()
            print(f"Successfully added {len(COUNTRIES)} countries with pricing data.")
        
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error creating country pricing data: {str(e)}")

if __name__ == "__main__":
    create_country_pricing_table()