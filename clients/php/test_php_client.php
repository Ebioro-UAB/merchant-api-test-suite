<?php
require_once 'EbioroApiClient.php';

// Test credentials
$apiKey = "pk_testrSWmOfY4FJo3fDEDQb3xf0L/djbB2vFwMzam/x4OMGg=";
$apiSecret = "sk_testEaFcSJwPgRKyYmLkAJwHdLuRXNYFzIcGUjr4u7ZMgVjNmEWs";

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