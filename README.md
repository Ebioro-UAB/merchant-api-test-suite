# Ebioro Merchant API Test Suite

A testing suite and reference client library for the Ebioro Merchant API with HMAC-SHA256 authentication.

- **Maintained clients (full API surface, tested live):** **Python** and **Node.js**
- **Authentication references (HMAC signing example only):** Java, PHP, C#

> **Last verified: 2026-06-10** — Python and Node.js clients tested live against the Ebioro test environment: payments, payment links, invoices, refunds, balances, webhook signature verification.

## 🚀 Quick Start

### Web Interface
1. Run the application: `python main.py --web --port 5000`
2. Open your browser to `http://localhost:5000`
3. **Select your preferred programming language** from the dropdown
4. Enter your API credentials in the "API Credentials" section
5. Test API functionality using your chosen language implementation

### Programmatic Usage
```python
from clients.python.ebioro_client import EbioroApiClient

# Initialize client
client = EbioroApiClient(
    api_key="your_public_key",
    api_secret="your_secret_key"
)

# Create a payment
payment_data = {
    "amount": {
        "currency": "USD",
        "value": 1500  # $15.00
    },
    "description": "Test payment",
    "redirectUrl": "https://yourstore.com/success",
    "cancelUrl": "https://yourstore.com/cancel",
    "name": "Your Store"
}

status_code, response, elapsed_time = client.create_payment(payment_data)
if status_code == 200:
    print(f"Payment created: {response['id']}")
    print(f"Payment URL: {response['hostedUrl']}")
```

## 🌐 Multi-Language Support

This test suite includes complete API client implementations in multiple programming languages:

### Supported Languages

| Language | File | Status | Description |
|----------|------|--------|-------------|
| **Python** | `clients/python/ebioro_client.py` | ✅ Maintained | Full API surface, tested live |
| **Node.js** | `clients/nodejs/ebioro-client.js` | ✅ Maintained | Full API surface, tested live |
| **Java** | `clients/java/EbioroApiClient.java` | 📘 Auth reference | Shows HMAC signing; core payment ops only |
| **PHP** | `clients/php/EbioroApiClient.php` | 📘 Auth reference | Shows HMAC signing; core payment ops only |
| **C#** | `clients/csharp/EbioroApiClient.cs` | 📘 Auth reference | Shows HMAC signing; core payment ops only |

The auth-reference clients demonstrate the request-signing scheme — the genuinely tricky part of integrating — and core payment operations. New API features (payment links, invoices) are added to the maintained clients only.

### Using Different Languages

**Web Interface**: Select your preferred language from the dropdown in the credentials section. The interface will test authentication and execute API calls using your chosen language implementation.

**Direct Usage**: Each client implementation includes example code and can be used independently. See the `clients/` directory for language-specific documentation and usage examples.

All implementations:
- ✅ Use identical HMAC-SHA256 authentication
- ✅ Support all API operations (payments, refunds, balances)
- ✅ Include proper error handling and logging
- ✅ Follow language-specific best practices

## 💳 How to Make Payments

### Using the Web Interface

1. **Set up credentials**: Enter your Ebioro API key and secret in the web interface
2. **Create a payment**: Go to the "API Operations" tab and click "Create Payment"
3. **Get payment URL**: The response will include a `hostedUrl` where customers can pay
4. **Track payment**: Use the payment ID to check status and retrieve details

### Using the Python Client

```python
# Create payment
payment_data = {
    "amount": {
        "currency": "USD",
        "value": 1000  # Amount in smallest currency unit (cents)
    },
    "description": "Order #12345",
    "redirectUrl": "https://yourstore.com/success",
    "cancelUrl": "https://yourstore.com/cancel",
    "webhookUrl": "https://yourstore.com/webhook",  # Optional
    "name": "Your Store Name",
    "locale": "en",
    "metadata": {
        "orderId": "12345",
        "customerId": "CUST-456"
    }
}

# Make the request
status_code, response, elapsed_time = client.create_payment(payment_data)

if status_code == 200:
    payment_id = response['id']
    payment_url = response['hostedUrl']
    
    # Redirect customer to payment_url
    print(f"Direct customer to: {payment_url}")
    
    # Later, check payment status
    status_code, payment_details, elapsed_time = client.get_payment(payment_id)
    if status_code == 200:
        print(f"Payment status: {payment_details['status']}")
```

## 🔐 Authentication

This client correctly implements HMAC-SHA256 authentication as required by the Ebioro API:

- **Signature Format**: `path + timestamp + method + body`
- **Headers**: `X-Digest-Key`, `X-Digest-Signature`, `X-Digest-Timestamp`
- **Body Handling**: Raw JSON string for POST requests (matches server expectations)

## 📋 Available Operations

### Payments
- `create_payment(payment_data)` - Create a new payment
- `create_payment_link(payment_data, expires_in_hours=168)` - Create a shareable payment link (response includes `shortUrl`)
- `get_payment(payment_id)` - Retrieve payment details
- `get_all_payments()` - List all payments

### Invoices
- `create_invoice(invoice_data)` - Create an invoice (line items + optional single tax percentage)
- `get_invoices(page, limit)` - List invoices
- `get_invoice(invoice_id)` - Retrieve an invoice
- `cancel_invoice(invoice_id)` - Cancel (void) an unpaid invoice
- `get_invoice_settings()` / `update_invoice_settings(settings)` - Invoice numbering settings

### Webhooks
- `verify_webhook_signature(raw_body, signature, api_secret)` - Verify the `X-WEBHOOK-AUTH` header (constant-time; pass the raw request body)

### Account Management
- `get_account_balances()` - Get current account balances
- `get_asset_balance(asset)` - Get specific asset balance

### Refunds
- `create_refund(payment_id, refund_data)` - Create a refund
- `get_refunds()` - List all refunds
- `get_refund(refund_id)` - Get specific refund details

### Testing & Debugging
- `test_authentication()` - Test API credentials
- `validate_signature_implementation()` - Validate HMAC signature
- `get_last_request_details()` - Get details of last request
- `get_last_response_details()` - Get details of last response

## 🧪 Running Tests

### Web Interface Tests
1. Go to the "Comprehensive Tests" tab
2. Click "Run All Tests"
3. View results including unit tests, integration tests, and signature validation

### Command Line Tests
```bash
# Run all tests
python main.py --test

# Run specific test types
python test_suite.py
python test_authentication.py
python test_endpoints.py
```

## 🛠️ Installation

1. Clone or download this project
2. Install dependencies: `pip install flask requests`
3. Set environment variables (optional):
   ```bash
   export EBIORO_API_KEY="your_public_key"
   export EBIORO_API_SECRET="your_secret_key"
   ```
4. Run the application: `python main.py --web --port 5000`

## 🔧 Configuration

The client supports various configuration options:

- **Base URL**: Default is `https://test-merchant.ebioro.com` (test environment)
- **Timeout**: Default is 30 seconds
- **Logging**: Comprehensive logging for debugging
- **Session Management**: Web interface maintains credentials in session

## 📱 Web Interface Features

- **Responsive Design**: Works on desktop and mobile
- **Real-time Testing**: Execute API calls and see results immediately
- **Debug Information**: View request/response details for troubleshooting
- **Export Results**: Download test results as JSON
- **Professional UI**: Clean, modern interface using Bootstrap

## 🔒 Security

- **Never hardcode credentials.** Every script in this repo reads `EBIORO_API_KEY` / `EBIORO_API_SECRET` from the environment. Keep it that way — this is a public repository.
- **Never commit a `.env` file.** `.gitignore` covers it, but verify before pushing.
- **Rotate any key that may have been exposed** (pasted in a chat, a log, a screenshot), even test keys.
- **Always verify webhook signatures** with the provided constant-time helpers, and verify against the **raw request body** — re-serializing parsed JSON can change the bytes and break verification.
- Path parameters are URL-encoded by the clients so untrusted ids cannot alter the request path.
- Log files (`*.log`) are gitignored; they can contain request payloads.

## 🎯 Production Considerations

- Replace test credentials with production keys
- Use production base URL: `https://merchant-api.ebioro.com`
- Implement proper error handling in your application
- Set up webhook endpoints to receive payment notifications
- Add proper logging and monitoring
- Secure credential storage (environment variables, key management)

## 📞 Support

This test suite validates the complete Ebioro API integration including:
- ✅ HMAC-SHA256 authentication
- ✅ Payment creation and management
- ✅ Account balance checking
- ✅ Refund processing
- ✅ Signature validation
- ✅ Comprehensive error handling

For API documentation and support, refer to the official Ebioro documentation or contact their support team.