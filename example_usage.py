#!/usr/bin/env python3
"""
Example usage of the Ebioro API Test Suite
Demonstrates how to make payments and interact with the API
"""

from clients.python.ebioro_client import EbioroApiClient
from utils import TestDataGenerator
import json

def main():
    """
    Example of how to use the Ebioro API client to make payments
    """
    
    # Initialize the client with your credentials
    api_key = "your_api_public_key_here"
    api_secret = "your_api_secret_key_here"
    
    print("🚀 Ebioro API Example Usage")
    print("=" * 50)
    
    # Create client
    client = EbioroApiClient(api_key, api_secret)
    
    print("\n1. Testing Authentication...")
    auth_result = client.test_authentication()
    if auth_result['success']:
        print("✅ Authentication successful!")
    else:
        print("❌ Authentication failed!")
        return
    
    print("\n2. Creating a Payment...")
    payment_data = {
        "amount": {
            "currency": "USD",
            "value": 1500  # $15.00
        },
        "description": "Test payment from Python client",
        "redirectUrl": "https://yourwebsite.com/success",
        "cancelUrl": "https://yourwebsite.com/cancel",
        "webhookUrl": "https://yourwebsite.com/webhook",
        "name": "Your Store Name",
        "locale": "en",
        "metadata": {
            "orderId": "ORDER-123",
            "customerId": "CUST-456"
        }
    }
    
    status_code, response, elapsed_time = client.create_payment(payment_data)
    
    if status_code == 200:
        print("✅ Payment created successfully!")
        print(f"   Payment ID: {response['id']}")
        print(f"   Status: {response['status']}")
        print(f"   Payment URL: {response['hostedUrl']}")
        
        # Store the payment ID for later use
        payment_id = response['id']
        
        print("\n3. Retrieving Payment Details...")
        status_code, payment_details, elapsed_time = client.get_payment(payment_id)
        
        if status_code == 200:
            print("✅ Payment details retrieved!")
            print(f"   Amount: {payment_details['amount']['value']} {payment_details['amount']['currency']}")
            print(f"   Status: {payment_details['status']}")
        else:
            print("❌ Failed to retrieve payment details")
    else:
        print("❌ Payment creation failed!")
        print(f"   Status: {status_code}")
        print(f"   Response: {json.dumps(response, indent=2)}")
        return
    
    print("\n4. Listing All Payments...")
    status_code, payments, elapsed_time = client.get_all_payments()
    
    if status_code == 200:
        print(f"✅ Found {len(payments)} payments")
        for i, payment in enumerate(payments):
            if i >= 3:  # Show first 3
                break
            print(f"   - {payment['id']}: {payment['amount']['value']} {payment['amount']['currency']} ({payment['status']})")
    else:
        print("❌ Failed to retrieve payments")
    
    print("\n5. Checking Account Balances...")
    status_code, balances, elapsed_time = client.get_account_balances()
    
    if status_code == 200:
        print("✅ Account balances retrieved!")
        for asset, balance_info in balances.items():
            print(f"   {asset}: {balance_info['balance']}")
    else:
        print("❌ Failed to retrieve balances")
    
    print("\n" + "=" * 50)
    print("🎉 Example completed successfully!")
    print("\nTo use this in your own project:")
    print("1. Install the required packages: pip install requests flask")
    print("2. Replace the API credentials with your own")
    print("3. Use the EbioroApiClient class in your application")
    print("4. Handle the responses according to your business logic")

if __name__ == "__main__":
    main()