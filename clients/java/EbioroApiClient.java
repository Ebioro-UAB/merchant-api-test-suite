// package com.ebioro.api;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Map;
import java.util.HashMap;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;
// Using built-in Java classes instead of Jackson

/**
 * Ebioro API Client for Java
 * 
 * This client implements HMAC-SHA256 authentication for the Ebioro Merchant API.
 * Signature format: path + timestamp + method + body
 * 
 * Usage:
 * EbioroApiClient client = new EbioroApiClient("your_api_key", "your_api_secret");
 * ApiResponse response = client.createPayment(paymentData);
 */
public class EbioroApiClient {
    
    private final String apiKey;
    private final String apiSecret;
    private final String baseUrl;
    private final HttpClient httpClient;
    // Using built-in JSON handling instead of Jackson
    
    public EbioroApiClient(String apiKey, String apiSecret) {
        this(apiKey, apiSecret, "https://test-merchant.ebioro.com");
    }
    
    public EbioroApiClient(String apiKey, String apiSecret, String baseUrl) {
        this.apiKey = apiKey;
        this.apiSecret = apiSecret;
        this.baseUrl = baseUrl;
        this.httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();
        // Using built-in JSON handling
    }
    
    /**
     * Generate HMAC-SHA256 signature
     * Payload format: path + timestamp + method + body
     */
    private String generateSignature(String path, String timestamp, String method, String body) {
        try {
            String payloadString = path + timestamp + method + body;
            
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKeySpec = new SecretKeySpec(apiSecret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            mac.init(secretKeySpec);
            
            byte[] signatureBytes = mac.doFinal(payloadString.getBytes(StandardCharsets.UTF_8));
            return bytesToHex(signatureBytes);
            
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate signature", e);
        }
    }
    
    /**
     * Convert byte array to hex string
     */
    private String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
    
    /**
     * Simple JSON converter for Map objects
     */
    private String convertToJson(Object obj) {
        if (obj instanceof Map) {
            Map<?, ?> map = (Map<?, ?>) obj;
            StringBuilder json = new StringBuilder("{");
            boolean first = true;
            for (Map.Entry<?, ?> entry : map.entrySet()) {
                if (!first) json.append(",");
                json.append("\"").append(entry.getKey()).append("\":");
                Object value = entry.getValue();
                if (value instanceof String) {
                    json.append("\"").append(value).append("\"");
                } else if (value instanceof Map) {
                    json.append(convertToJson(value));
                } else {
                    json.append(value);
                }
                first = false;
            }
            json.append("}");
            return json.toString();
        }
        return obj.toString();
    }
    
    /**
     * Generate authentication headers
     */
    private Map<String, String> generateHeaders(String method, String path, String body) {
        String timestamp = String.valueOf(System.currentTimeMillis() / 1000);
        String signature = generateSignature(path, timestamp, method, body);
        
        Map<String, String> headers = new HashMap<>();
        headers.put("Content-Type", "application/json");
        headers.put("X-Digest-Key", apiKey);
        headers.put("X-Digest-Timestamp", timestamp);
        headers.put("X-Digest-Signature", signature);
        
        return headers;
    }
    
    /**
     * Make authenticated API request
     */
    private ApiResponse makeRequest(String method, String path, Object requestBody) throws IOException, InterruptedException {
        String bodyJson = "";
        if (requestBody != null) {
            try {
                bodyJson = convertToJson(requestBody);
            } catch (Exception e) {
                throw new RuntimeException("Failed to serialize request body", e);
            }
        }
        
        Map<String, String> headers = generateHeaders(method, path, bodyJson);
        
        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + path))
            .timeout(Duration.ofSeconds(30));
        
        // Add headers
        for (Map.Entry<String, String> header : headers.entrySet()) {
            requestBuilder.header(header.getKey(), header.getValue());
        }
        
        // Set method and body
        switch (method.toUpperCase()) {
            case "GET":
                requestBuilder.GET();
                break;
            case "POST":
                requestBuilder.POST(HttpRequest.BodyPublishers.ofString(bodyJson, StandardCharsets.UTF_8));
                break;
            case "PUT":
                requestBuilder.PUT(HttpRequest.BodyPublishers.ofString(bodyJson, StandardCharsets.UTF_8));
                break;
            case "DELETE":
                requestBuilder.DELETE();
                break;
        }
        
        HttpRequest request = requestBuilder.build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        
        return new ApiResponse(response.statusCode(), response.body(), headers);
    }
    
    /**
     * Create a payment
     */
    public ApiResponse createPayment(Map<String, Object> paymentData) throws IOException, InterruptedException {
        return makeRequest("POST", "/payments", paymentData);
    }
    
    /**
     * Get a specific payment
     */
    public ApiResponse getPayment(String paymentId) throws IOException, InterruptedException {
        return makeRequest("GET", "/api/v1/payments/" + paymentId, null);
    }
    
    /**
     * Get all payments
     */
    public ApiResponse getAllPayments() throws IOException, InterruptedException {
        return makeRequest("GET", "/api/v1/payments", null);
    }
    
    /**
     * Create a refund
     */
    public ApiResponse createRefund(String paymentId, Map<String, Object> refundData) throws IOException, InterruptedException {
        return makeRequest("POST", "/api/v1/payments/" + paymentId + "/refunds", refundData);
    }
    
    /**
     * Get account balances
     */
    public ApiResponse getAccountBalances() throws IOException, InterruptedException {
        return makeRequest("GET", "/api/v1/account/balances", null);
    }
    
    /**
     * Test authentication
     */
    public ApiResponse testAuthentication() throws IOException, InterruptedException {
        return makeRequest("GET", "/payments", null);
    }
    
    /**
     * API Response wrapper
     */
    public static class ApiResponse {
        private final int statusCode;
        private final String body;
        private final Map<String, String> requestHeaders;
        
        public ApiResponse(int statusCode, String body, Map<String, String> requestHeaders) {
            this.statusCode = statusCode;
            this.body = body;
            this.requestHeaders = requestHeaders;
        }
        
        public int getStatusCode() { return statusCode; }
        public String getBody() { return body; }
        public Map<String, String> getRequestHeaders() { return requestHeaders; }
        public boolean isSuccess() { return statusCode >= 200 && statusCode < 300; }
    }
    
    /**
     * Example usage
     */
    public static void main(String[] args) {
        try {
            // Initialize client
            EbioroApiClient client = new EbioroApiClient(
                System.getenv("API_KEY"),
                System.getenv("API_SECRET_KEY")
            );
            
            // Test authentication
            ApiResponse authResponse = client.testAuthentication();
            System.out.println("Auth test: " + authResponse.getStatusCode());
            
            // Create payment
            Map<String, Object> paymentData = new HashMap<>();
            paymentData.put("amount", 1000);
            paymentData.put("currency", "USD");
            paymentData.put("description", "Test payment from Java client");
            
            ApiResponse paymentResponse = client.createPayment(paymentData);
            System.out.println("Payment creation: " + paymentResponse.getStatusCode());
            System.out.println("Response: " + paymentResponse.getBody());
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}