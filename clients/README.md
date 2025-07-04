# Multi-Language Ebioro API Clients

This directory contains API client implementations for the Ebioro Merchant API in multiple programming languages. Each implementation provides the same functionality with language-specific patterns and best practices.

## Available Languages

### Python (`python/`)
- **File**: `ebioro_client.py` (in root directory)
- **Description**: Python implementation using the requests library
- **Features**: Comprehensive error handling, detailed logging, type hints
- **Dependencies**: `requests`
- **Status**: ✅ Fully functional and tested

### Java (`java/`)
- **File**: `EbioroApiClient.java`
- **Description**: Java implementation using HttpClient (Java 11+)
- **Features**: Modern Java patterns, proper exception handling, builder pattern
- **Dependencies**: Jackson for JSON processing
- **Status**: 🔶 Code complete, requires Java runtime for testing

### PHP (`php/`)
- **File**: `EbioroApiClient.php`
- **Description**: PHP implementation using cURL
- **Features**: Object-oriented design, error handling, PSR compliance
- **Dependencies**: cURL extension
- **Status**: 🔶 Code complete, requires PHP runtime for testing

### Node.js (`nodejs/`)
- **File**: `ebioro-client.js`
- **Description**: Node.js implementation using native https module
- **Features**: Promise-based async/await, ES6 classes, no external dependencies
- **Dependencies**: None (uses Node.js built-ins)
- **Status**: 🔶 Code complete, requires Node.js runtime for testing

### C# (`csharp/`)
- **File**: `EbioroApiClient.cs`
- **Description**: C# implementation using HttpClient
- **Features**: Async/await patterns, LINQ, proper disposal patterns
- **Dependencies**: System.Text.Json
- **Status**: 🔶 Code complete, requires .NET runtime for testing

## Common Features

All implementations provide:

- ✅ HMAC-SHA256 authentication with correct signature format
- ✅ Support for all major API operations (payments, refunds, balances)
- ✅ Proper error handling and response validation
- ✅ Request/response logging and debugging
- ✅ Configurable base URL for different environments
- ✅ Consistent API interface across languages

## Authentication Implementation

All clients implement the same HMAC-SHA256 signature generation:

```
Signature = HMAC-SHA256(
    payload = path + timestamp + method + body,
    secret = api_secret_key
)
```

Headers included in all requests:
- `Content-Type: application/json`
- `X-Digest-Key: {api_public_key}`
- `X-Digest-Timestamp: {unix_timestamp}`
- `X-Digest-Signature: {hex_encoded_signature}`

## Usage Examples

### Python
```python
from ebioro_client import EbioroApiClient

client = EbioroApiClient(api_key, api_secret)
status_code, response, elapsed_time = client.create_payment({
    "amount": 1000,
    "currency": "USD",
    "description": "Test payment"
})
```

### Java
```java
EbioroApiClient client = new EbioroApiClient(apiKey, apiSecret);
ApiResponse response = client.createPayment(paymentData);
System.out.println("Status: " + response.getStatusCode());
```

### PHP
```php
$client = new EbioroApiClient($apiKey, $apiSecret);
$response = $client->createPayment($paymentData);
echo "Status: " . $response->getStatusCode();
```

### Node.js
```javascript
const { EbioroApiClient } = require('./ebioro-client');

const client = new EbioroApiClient(apiKey, apiSecret);
const response = await client.createPayment(paymentData);
console.log('Status:', response.getStatusCode());
```

### C#
```csharp
using var client = new EbioroApiClient(apiKey, apiSecret);
var response = await client.CreatePaymentAsync(paymentData);
Console.WriteLine($"Status: {response.StatusCode}");
```

## Testing

All implementations can be tested through:

1. **Web Interface**: Use the dropdown to select your preferred language
2. **Command Line**: Each implementation includes example usage code
3. **Unit Tests**: Available for Python implementation in the test suite

## Runtime Requirements

To test different language implementations locally:

- **Python**: `python 3.7+` with `requests` library
- **Java**: `Java 11+` with Jackson library
- **PHP**: `PHP 7.4+` with cURL extension
- **Node.js**: `Node.js 14+` (no additional dependencies)
- **C#**: `.NET 6.0+` or .NET Framework 4.7.2+

## Security Notes

- All implementations use environment variables for API credentials
- No credentials are hardcoded in any client code
- Proper certificate validation is enabled for HTTPS requests
- Sensitive data is masked in logs and debugging output

## Contributing

When adding new language implementations:

1. Follow the established patterns for authentication and error handling
2. Include comprehensive example usage
3. Add appropriate error handling and logging
4. Update this README with the new language
5. Test against the actual API endpoints

## Support

For issues or questions:
- Check the main project README for general API documentation
- Refer to language-specific documentation in each subdirectory
- Test using the web interface for interactive debugging