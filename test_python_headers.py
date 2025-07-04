#!/usr/bin/env python3
"""Test Python client headers generation"""

from clients.python.ebioro_client import EbioroApiClient
import json

# Use test credentials
api_key = "pk_testrSWmOfY4FJo3fDEDQb3xf0L/djbB2vFwMzam/x4OMGg="
api_secret = "sk_testR3tSbF78YLHwNod9T3fBV0+cFkS0t2mJSbv71EwJjPg="

print("=== Python Client Headers Debug ===")

client = EbioroApiClient(api_key, api_secret)

# Mock a fixed timestamp for comparison
import time
original_time = time.time
time.time = lambda: 1234567890  # Fixed timestamp

try:
    headers = client.generate_headers("GET", "/payments", None)
    print("Headers generated:")
    for key, value in headers.items():
        print(f"  {key}: {value}")
        
    print("\nPayload string components:")
    print(f"  Path: '/payments'")
    print(f"  Timestamp: '{headers['X-Timestamp']}'")
    print(f"  Method: 'GET'")
    print(f"  Body: ''")
    print(f"  Payload: '/payments{headers['X-Timestamp']}GET'")
    
finally:
    # Restore original time function
    time.time = original_time