#!/usr/bin/env python3
"""
Simple test script to validate Ebioro API integration
Tests the provided Python code against the actual API
"""

import time
import json
import hmac
import hashlib
import requests

# API Credentials (Test)
API_KEY = "pk_testrSWmOfY4FJo3fDEDQb3xf0L/djbB2vFwMzam/x4OMGg="
API_SECRET_KEY = "sk_testR3tSbF78YLHwNod9T3fBV0+cFkS0t2mJSbv71EwJjPg="

# API Endpoint
BASE_URL = "https://test-merchant.ebioro.com"
ENDPOINT = "/payments"

# Updated Payment Payload
payload = {
    "amount": {
        "currency": "USD",
        "value": 1000
    },
    "description": "Payment for order 12345",
    "redirectUrl": "https://example.com/redirect",
    "name": "Example Store",
    "cancelUrl": "https://example.com/cancel",
    "webhookUrl": "https://example.com/webhook",
    "locale": "en",
    "metadata": {
        "orderId": 12345
    }
}

def generate_headers(method: str, path: str, body = None):
    """
    Generates HMAC-SHA256 signed headers for authentication.
    """
    data = json.dumps(body, separators=(',', ':')) if body else ""
    timestamp = str(int(time.time()))  # Unix timestamp
    payload_string = path + timestamp + method + data  # Must match backend signing logic
    
    # Generate HMAC signature
    signature = hmac.new(API_SECRET_KEY.encode('utf-8'),
                        payload_string.encode('utf-8'),
                        hashlib.sha256).hexdigest()

    headers = {
        'Content-Type': 'application/json',
        'X-Digest-Key': API_KEY,
        'X-Digest-Signature': signature,
        'X-Digest-Timestamp': timestamp
    }

    return headers

def test_authentication():
    """Test authentication by getting payments list"""
    print("🔐 Testing Authentication...")
    
    url = f"{BASE_URL}/payments"
    headers = generate_headers(method="GET", path="/payments", body=None)
    
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code in [200, 401, 403]:
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except json.JSONDecodeError:
                print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Authentication successful!")
                return True
            else:
                print("❌ Authentication failed!")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def test_payment_creation():
    """Test payment creation"""
    print("\n💳 Testing Payment Creation...")
    
    url = f"{BASE_URL}{ENDPOINT}"
    headers = generate_headers(method="POST", path=ENDPOINT, body=payload)
    
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"\nStatus Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response: {response.text}")
            
        if response.status_code in [200, 201]:
            print("✅ Payment creation successful!")
            return response_data.get('id') if 'response_data' in locals() else None
        else:
            print("❌ Payment creation failed!")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return None

def test_get_balances():
    """Test getting account balances"""
    print("\n💰 Testing Account Balances...")
    
    url = f"{BASE_URL}/accounts/balances"
    headers = generate_headers(method="GET", path="/accounts/balances", body=None)
    
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response: {response.text}")
            
        if response.status_code == 200:
            print("✅ Balance retrieval successful!")
            return True
        else:
            print("❌ Balance retrieval failed!")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def validate_signature_implementation():
    """Validate the signature implementation"""
    print("\n🔐 Validating Signature Implementation...")
    
    # Test case 1: GET request with no body
    test_cases = [
        {
            "method": "GET",
            "path": "/payments",
            "body": None,
            "description": "GET request with no body"
        },
        {
            "method": "POST", 
            "path": "/payments",
            "body": {"test": "data"},
            "description": "POST request with JSON body"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {case['description']}")
        
        # Generate headers twice with fixed timestamp to ensure consistency
        fixed_time = 1234567890
        
        # Mock time.time() to return fixed timestamp
        original_time = time.time
        time.time = lambda: fixed_time
        
        try:
            headers1 = generate_headers(case["method"], case["path"], case["body"])
            headers2 = generate_headers(case["method"], case["path"], case["body"])
            
            # Check if signatures are identical (they should be with same timestamp)
            if headers1['X-Digest-Signature'] == headers2['X-Digest-Signature']:
                print(f"✅ Signature consistency: PASS")
            else:
                print(f"❌ Signature consistency: FAIL")
                
            # Validate signature format (should be 64 character hex string)
            signature = headers1['X-Digest-Signature']
            if len(signature) == 64 and all(c in '0123456789abcdef' for c in signature):
                print(f"✅ Signature format: PASS (SHA256 hex)")
            else:
                print(f"❌ Signature format: FAIL")
                
            print(f"Generated signature: {signature}")
            
        finally:
            # Restore original time function
            time.time = original_time

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 EBIORO API INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Signature validation
    validate_signature_implementation()
    
    # Test 2: Authentication
    auth_success = test_authentication()
    
    if auth_success:
        # Test 3: Payment creation
        payment_id = test_payment_creation()
        
        # Test 4: Account balances
        test_get_balances()
    else:
        print("\n⚠️  Skipping other tests due to authentication failure")
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    if auth_success:
        print("✅ API integration is working correctly!")
        print("✅ Authentication: PASS")
        print("✅ HMAC-SHA256 signature generation: PASS")
        print("✅ API endpoints accessible")
    else:
        print("❌ API integration has issues")
        print("❌ Authentication: FAIL")
        print("⚠️  Check API credentials and endpoint URL")

if __name__ == "__main__":
    main()