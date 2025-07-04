<?php

/**
 * Ebioro API Client for PHP
 * 
 * This client implements HMAC-SHA256 authentication for the Ebioro Merchant API.
 * Signature format: path + timestamp + method + body
 * 
 * Usage:
 * $client = new EbioroApiClient($apiKey, $apiSecret);
 * $response = $client->createPayment($paymentData);
 */
class EbioroApiClient {
    
    private $apiKey;
    private $apiSecret;
    private $baseUrl;
    private $lastRequest;
    private $lastResponse;
    
    public function __construct($apiKey, $apiSecret, $baseUrl = 'https://test-merchant.ebioro.com') {
        $this->apiKey = $apiKey;
        $this->apiSecret = $apiSecret;
        $this->baseUrl = $baseUrl;
        $this->lastRequest = null;
        $this->lastResponse = null;
    }
    
    /**
     * Generate HMAC-SHA256 signature
     * Payload format: path + timestamp + method + body
     */
    private function generateSignature($path, $timestamp, $method, $body) {
        $payloadString = $path . $timestamp . $method . $body;
        return hash_hmac('sha256', $payloadString, $this->apiSecret);
    }
    
    /**
     * Generate authentication headers
     */
    private function generateHeaders($method, $path, $body) {
        $timestamp = (string)time();
        $signature = $this->generateSignature($path, $timestamp, $method, $body);
        
        return [
            'Content-Type: application/json',
            'X-Digest-Key: ' . $this->apiKey,
            'X-Digest-Timestamp: ' . $timestamp,
            'X-Digest-Signature: ' . $signature
        ];
    }
    
    /**
     * Make authenticated API request
     */
    private function makeRequest($method, $path, $requestBody = null) {
        $bodyJson = '';
        if ($requestBody !== null) {
            $bodyJson = json_encode($requestBody, JSON_UNESCAPED_SLASHES);
        }
        
        $headers = $this->generateHeaders($method, $path, $bodyJson);
        $url = $this->baseUrl . $path;
        
        // Store request details
        $this->lastRequest = [
            'method' => $method,
            'url' => $url,
            'headers' => $headers,
            'body' => $bodyJson,
            'timestamp' => date('Y-m-d H:i:s')
        ];
        
        // Initialize cURL
        $ch = curl_init();
        
        curl_setopt_array($ch, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 30,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_SSL_VERIFYHOST => 2
        ]);
        
        // Add body for POST/PUT requests
        if (in_array($method, ['POST', 'PUT']) && !empty($bodyJson)) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, $bodyJson);
        }
        
        $startTime = microtime(true);
        $response = curl_exec($ch);
        $elapsedTime = microtime(true) - $startTime;
        
        $statusCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        
        curl_close($ch);
        
        if ($error) {
            throw new Exception('cURL Error: ' . $error);
        }
        
        // Store response details
        $this->lastResponse = [
            'status_code' => $statusCode,
            'body' => $response,
            'elapsed_time' => $elapsedTime,
            'timestamp' => date('Y-m-d H:i:s')
        ];
        
        return new ApiResponse($statusCode, $response, $elapsedTime);
    }
    
    /**
     * Create a payment
     */
    public function createPayment($paymentData) {
        return $this->makeRequest('POST', '/payments', $paymentData);
    }
    
    /**
     * Get a specific payment
     */
    public function getPayment($paymentId) {
        return $this->makeRequest('GET', '/api/v1/payments/' . $paymentId);
    }
    
    /**
     * Get all payments
     */
    public function getAllPayments() {
        return $this->makeRequest('GET', '/api/v1/payments');
    }
    
    /**
     * Create a refund
     */
    public function createRefund($paymentId, $refundData) {
        return $this->makeRequest('POST', '/api/v1/payments/' . $paymentId . '/refunds', $refundData);
    }
    
    /**
     * Get all refunds
     */
    public function getAllRefunds() {
        return $this->makeRequest('GET', '/api/v1/refunds');
    }
    
    /**
     * Get account balances
     */
    public function getAccountBalances() {
        return $this->makeRequest('GET', '/api/v1/account/balances');
    }
    
    /**
     * Test authentication
     */
    public function testAuthentication() {
        return $this->makeRequest('GET', '/payments');
    }
    
    /**
     * Get last request details
     */
    public function getLastRequest() {
        return $this->lastRequest;
    }
    
    /**
     * Get last response details
     */
    public function getLastResponse() {
        return $this->lastResponse;
    }
}

/**
 * API Response wrapper
 */
class ApiResponse {
    private $statusCode;
    private $body;
    private $elapsedTime;
    private $data;
    
    public function __construct($statusCode, $body, $elapsedTime) {
        $this->statusCode = $statusCode;
        $this->body = $body;
        $this->elapsedTime = $elapsedTime;
        $this->data = json_decode($body, true);
    }
    
    public function getStatusCode() {
        return $this->statusCode;
    }
    
    public function getBody() {
        return $this->body;
    }
    
    public function getData() {
        return $this->data;
    }
    
    public function getElapsedTime() {
        return $this->elapsedTime;
    }
    
    public function isSuccess() {
        return $this->statusCode >= 200 && $this->statusCode < 300;
    }
    
    public function toArray() {
        return [
            'status_code' => $this->statusCode,
            'body' => $this->body,
            'data' => $this->data,
            'elapsed_time' => $this->elapsedTime,
            'success' => $this->isSuccess()
        ];
    }
}

// Example usage
if (basename(__FILE__) == basename($_SERVER['PHP_SELF'])) {
    try {
        // Initialize client
        $client = new EbioroApiClient(
            getenv('API_KEY'),
            getenv('API_SECRET_KEY')
        );
        
        // Test authentication
        $authResponse = $client->testAuthentication();
        echo "Auth test: " . $authResponse->getStatusCode() . "\n";
        
        // Create payment
        $paymentData = [
            'amount' => 1000,
            'currency' => 'USD',
            'description' => 'Test payment from PHP client'
        ];
        
        $paymentResponse = $client->createPayment($paymentData);
        echo "Payment creation: " . $paymentResponse->getStatusCode() . "\n";
        echo "Response: " . $paymentResponse->getBody() . "\n";
        
    } catch (Exception $e) {
        echo "Error: " . $e->getMessage() . "\n";
    }
}

?>