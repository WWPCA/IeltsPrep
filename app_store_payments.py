"""
App Store Payment Verification for IELTS GenAI Prep
Handles Apple App Store and Google Play Store purchase verification
"""

import requests
import json
import base64
import os
from datetime import datetime
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class AppStorePayments:
    """Handles app store payment verification and module unlocking"""
    
    def __init__(self):
        self.apple_verify_url = "https://buy.itunes.apple.com/verifyReceipt"
        self.apple_sandbox_url = "https://sandbox.itunes.apple.com/verifyReceipt"
        self.apple_shared_secret = os.environ.get("APPLE_SHARED_SECRET")
        
        # Google Play credentials
        self.google_package_name = "com.ieltsaiprep.app"
        self.google_service_account = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        
        # Assessment module pricing
        self.module_prices = {
            "academic_speaking": 36.00,
            "academic_writing": 36.00,
            "general_speaking": 36.00,
            "general_writing": 36.00
        }
    
    def verify_apple_receipt(self, receipt_data: str, user_email: str) -> Tuple[bool, Dict]:
        """Verify Apple App Store receipt and return purchase details"""
        try:
            # Prepare verification request
            request_data = {
                "receipt-data": receipt_data,
                "password": self.apple_shared_secret,
                "exclude-old-transactions": True
            }
            
            # Try production first
            response = requests.post(
                self.apple_verify_url,
                json=request_data,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            result = response.json()
            
            # If sandbox receipt, try sandbox endpoint
            if result.get("status") == 21007:
                response = requests.post(
                    self.apple_sandbox_url,
                    json=request_data,
                    timeout=10,
                    headers={"Content-Type": "application/json"}
                )
                result = response.json()
            
            # Check verification status
            if result.get("status") == 0:
                receipt = result.get("receipt", {})
                in_app_purchases = receipt.get("in_app", [])
                
                if not in_app_purchases:
                    return False, {"error": "No in-app purchases found"}
                
                # Get latest purchase
                latest_purchase = in_app_purchases[-1]
                product_id = latest_purchase.get("product_id")
                transaction_id = latest_purchase.get("transaction_id")
                purchase_date = latest_purchase.get("purchase_date_ms")
                
                # Validate product ID
                if product_id not in self.module_prices:
                    return False, {"error": f"Invalid product ID: {product_id}"}
                
                purchase_details = {
                    "product_id": product_id,
                    "transaction_id": transaction_id,
                    "purchase_date": datetime.fromtimestamp(int(purchase_date) / 1000).isoformat(),
                    "price": self.module_prices[product_id],
                    "platform": "apple",
                    "user_email": user_email,
                    "verified_at": datetime.utcnow().isoformat()
                }
                
                logger.info(f"Apple purchase verified: {product_id} for {user_email}")
                return True, purchase_details
            
            else:
                error_message = self._get_apple_error_message(result.get("status"))
                return False, {"error": error_message, "status": result.get("status")}
        
        except Exception as e:
            logger.error(f"Apple receipt verification error: {e}")
            return False, {"error": "Receipt verification failed"}
    
    def verify_google_purchase(self, purchase_token: str, product_id: str, user_email: str) -> Tuple[bool, Dict]:
        """Verify Google Play Store purchase using Play Billing API"""
        try:
            if not self.google_service_account:
                return False, {"error": "Google service account not configured"}
            
            # Parse service account JSON
            service_account_info = json.loads(self.google_service_account)
            
            # Get access token for Google Play Developer API
            access_token = self._get_google_access_token(service_account_info)
            if not access_token:
                return False, {"error": "Failed to get Google access token"}
            
            # Verify purchase with Google Play Developer API
            api_url = f"https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{self.google_package_name}/purchases/products/{product_id}/tokens/{purchase_token}"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                purchase_data = response.json()
                
                # Check purchase state (0 = purchased, 1 = canceled)
                if purchase_data.get("purchaseState") != 0:
                    return False, {"error": "Purchase not valid or canceled"}
                
                # Check consumption state (0 = not consumed, 1 = consumed)
                if purchase_data.get("consumptionState") == 1:
                    return False, {"error": "Purchase already consumed"}
                
                purchase_details = {
                    "product_id": product_id,
                    "purchase_token": purchase_token,
                    "purchase_time": datetime.fromtimestamp(int(purchase_data.get("purchaseTimeMillis", 0)) / 1000).isoformat(),
                    "price": self.module_prices.get(product_id, 36.00),
                    "platform": "google",
                    "user_email": user_email,
                    "verified_at": datetime.utcnow().isoformat(),
                    "order_id": purchase_data.get("orderId")
                }
                
                logger.info(f"Google purchase verified: {product_id} for {user_email}")
                return True, purchase_details
            
            else:
                return False, {"error": f"Google API error: {response.status_code}"}
        
        except Exception as e:
            logger.error(f"Google purchase verification error: {e}")
            return False, {"error": "Purchase verification failed"}
    
    def _get_google_access_token(self, service_account_info: Dict) -> Optional[str]:
        """Get Google API access token using service account"""
        try:
            import jwt
            from datetime import timedelta
            
            # Create JWT for Google API
            now = datetime.utcnow()
            payload = {
                "iss": service_account_info["client_email"],
                "scope": "https://www.googleapis.com/auth/androidpublisher",
                "aud": "https://oauth2.googleapis.com/token",
                "iat": int(now.timestamp()),
                "exp": int((now + timedelta(hours=1)).timestamp())
            }
            
            # Sign JWT with private key
            private_key = service_account_info["private_key"]
            token = jwt.encode(payload, private_key, algorithm="RS256")
            
            # Exchange JWT for access token
            token_data = {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": token
            }
            
            response = requests.post(
                "https://oauth2.googleapis.com/token",
                data=token_data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("access_token")
            
            return None
        
        except Exception as e:
            logger.error(f"Google access token error: {e}")
            return None
    
    def _get_apple_error_message(self, status_code: int) -> str:
        """Get human-readable error message for Apple status codes"""
        error_messages = {
            21000: "The App Store could not read the JSON object you provided.",
            21002: "The data in the receipt-data property was malformed or missing.",
            21003: "The receipt could not be authenticated.",
            21004: "The shared secret you provided does not match the shared secret on file for your account.",
            21005: "The receipt server is not currently available.",
            21006: "This receipt is valid but the subscription has expired.",
            21007: "This receipt is from the test environment, but it was sent to the production environment for verification.",
            21008: "This receipt is from the production environment, but it was sent to the test environment for verification.",
            21010: "This receipt could not be authorized."
        }
        
        return error_messages.get(status_code, f"Unknown error (status: {status_code})")
    
    def unlock_assessment_module(self, user_email: str, product_id: str, purchase_details: Dict) -> bool:
        """Unlock assessment module for user after successful payment verification"""
        try:
            # This would integrate with your DynamoDB user management
            # For now, return success to indicate the module should be unlocked
            logger.info(f"Unlocking {product_id} for {user_email}")
            return True
        
        except Exception as e:
            logger.error(f"Module unlock error: {e}")
            return False

# Global payment handler instance
payment_handler = AppStorePayments()