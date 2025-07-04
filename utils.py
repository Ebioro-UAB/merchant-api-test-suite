import json
import time
import hashlib
import hmac
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class SignatureValidator:
    """Validates HMAC signature generation"""
    
    @staticmethod
    def validate_signature_components(path: str, timestamp: str, method: str, body: str) -> Dict[str, Any]:
        """Validate all components used in signature generation"""
        errors = []
        
        # Validate path
        if not path.startswith('/'):
            errors.append("Path must start with '/'")
        
        # Validate timestamp
        try:
            ts = int(timestamp)
            current_time = int(time.time())
            if abs(current_time - ts) > 300:  # 5 minutes tolerance
                errors.append(f"Timestamp {timestamp} is too old or in future")
        except ValueError:
            errors.append("Invalid timestamp format")
        
        # Validate method
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        if method not in valid_methods:
            errors.append(f"Invalid HTTP method: {method}")
        
        # Validate body for POST/PUT requests
        if method in ['POST', 'PUT', 'PATCH'] and body:
            try:
                json.loads(body)
            except json.JSONDecodeError:
                errors.append("Invalid JSON in request body")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "components": {
                "path": path,
                "timestamp": timestamp,
                "method": method,
                "body": body
            }
        }
    
    @staticmethod
    def compare_signatures(expected: str, actual: str, payload_string: str) -> Dict[str, Any]:
        """Compare two signatures and provide debugging information"""
        match = expected == actual
        
        return {
            "match": match,
            "expected": expected,
            "actual": actual,
            "payload_string": payload_string,
            "payload_length": len(payload_string),
            "payload_hash": hashlib.md5(payload_string.encode()).hexdigest()
        }

class ResponseValidator:
    """Validates API responses"""
    
    @staticmethod
    def validate_payment_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate payment creation response"""
        errors = []
        required_fields = ['id', 'amount', 'status', 'createdAt']
        
        for field in required_fields:
            if field not in response_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate amount structure
        if 'amount' in response_data:
            amount = response_data['amount']
            if not isinstance(amount, dict):
                errors.append("Amount must be an object")
            else:
                if 'currency' not in amount:
                    errors.append("Amount missing currency")
                if 'value' not in amount:
                    errors.append("Amount missing value")
        
        # Validate status
        if 'status' in response_data:
            valid_statuses = ['pending', 'completed', 'failed', 'cancelled']
            if response_data['status'] not in valid_statuses:
                errors.append(f"Invalid status: {response_data['status']}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "response_data": response_data
        }
    
    @staticmethod
    def validate_error_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate error response structure"""
        errors = []
        
        if 'error' not in response_data and 'message' not in response_data:
            errors.append("Error response missing error or message field")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "response_data": response_data
        }

class TestDataGenerator:
    """Generates test data for API testing"""
    
    @staticmethod
    def generate_payment_payload(amount: int = 1000, currency: str = "USD") -> Dict[str, Any]:
        """Generate a valid payment payload"""
        return {
            "amount": {
                "currency": currency,
                "value": amount
            },
            "description": f"Test payment {int(time.time())}",
            "redirectUrl": "https://example.com/redirect",
            "name": "Test Store",
            "cancelUrl": "https://example.com/cancel",
            "webhookUrl": "https://example.com/webhook",
            "locale": "en",
            "metadata": {
                "orderId": int(time.time()),
                "testMode": True
            }
        }
    
    @staticmethod
    def generate_refund_payload(amount: int = 500, description: str = "Test refund") -> Dict[str, Any]:
        """Generate a valid refund payload"""
        return {
            "amount": {
                "currency": "USD",
                "value": amount
            },
            "description": description,
            "metadata": {
                "refundReason": "customer_request",
                "testMode": True
            }
        }

def format_json_response(data: Any, indent: int = 2) -> str:
    """Format JSON response for display"""
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(data)

def calculate_elapsed_time(start_time: float) -> float:
    """Calculate elapsed time from start time"""
    return time.time() - start_time

def mask_sensitive_data(data: str, fields: list = None) -> str:
    """Mask sensitive data in logs"""
    if fields is None:
        fields = ['api_key', 'secret', 'password', 'token']
    
    masked_data = data
    for field in fields:
        if field in data.lower():
            # Simple masking - replace with asterisks
            import re
            pattern = f'("{field}"\\s*:\\s*"[^"]*")'
            masked_data = re.sub(pattern, f'"{field}": "***"', masked_data, flags=re.IGNORECASE)
    
    return masked_data

def generate_timestamp() -> str:
    """Generate current Unix timestamp as string"""
    return str(int(time.time()))

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, OSError):
        return timestamp
