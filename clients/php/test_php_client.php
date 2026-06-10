<?php
require_once 'EbioroApiClient.php';

// Test credentials
$apiKey = getenv('EBIORO_API_KEY');
$apiSecret = getenv('EBIORO_API_SECRET');

echo "Testing PHP Ebioro API Client\n";
echo "=====================================\n";

try {
    // Initialize client
    $client = new EbioroApiClient($apiKey, $apiSecret);
    echo "✅ Client initialized\n";
    
    // Test authentication
    echo "\n🔐 Testing authentication...\n";
    $authResponse = $client->testAuthentication();
    echo "Status Code: " . $authResponse->getStatusCode() . "\n";
    echo "Response: " . $authResponse->getBody() . "\n";
    
    if ($authResponse->getStatusCode() == 200) {
        echo "✅ Authentication successful!\n";
    } else {
        echo "❌ Authentication failed\n";
    }
    
    echo "\n🏁 PHP client test completed\n";
    
} catch (Exception $e) {
    echo "❌ Test failed: " . $e->getMessage() . "\n";
}
?>