# Ebioro API Python Client

This is the Python implementation of the Ebioro Merchant API client with HMAC-SHA256 authentication.

## Features

- HMAC-SHA256 authentication with hex encoding
- Comprehensive logging and debugging
- Request/response validation
- Support for all Ebioro API endpoints:
  - Payments (create, retrieve, list)
  - Refunds (create, retrieve, list)
  - Account balances (retrieve)
  - Authentication testing

## Usage

```python
from clients.python.ebioro_client import EbioroApiClient

# Initialize client
client = EbioroApiClient(
    api_key="your_api_key", 
    api_secret="your_api_secret"
)

# Test authentication
auth_result = client.test_authentication()
print(f"Authentication: {auth_result['success']}")

# Create a payment
payment_data = {
    "amount": {"value": 1000, "currency": "USD"},
    "redirectUrl": "https://example.com/success"
}
status, response, elapsed = client.create_payment(payment_data)
print(f"Payment Status: {status}")
```

## Authentication Format

The client uses the following HMAC-SHA256 authentication format:

- **Payload String**: `path + timestamp + method + body`
- **Signature**: `HMAC-SHA256(payload_string, api_secret).hexdigest()`
- **Headers**:
  - `X-Digest-Key`: API key
  - `X-Digest-Timestamp`: Unix timestamp
  - `X-Digest-Signature`: Hex-encoded HMAC signature

## Dependencies

- `requests`: HTTP client
- `hashlib`: HMAC signature generation
- `json`: JSON payload handling
- `time`: Timestamp generation