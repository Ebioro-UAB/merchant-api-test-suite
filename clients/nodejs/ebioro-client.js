const crypto = require('crypto');
const https = require('https');
const http = require('http');
const { URL } = require('url');

/**
 * Ebioro API Client for Node.js
 * 
 * This client implements HMAC-SHA256 authentication for the Ebioro Merchant API.
 * Signature format: path + timestamp + method + body
 * 
 * Usage:
 * const client = new EbioroApiClient(apiKey, apiSecret);
 * const response = await client.createPayment(paymentData);
 */
class EbioroApiClient {
    
    constructor(apiKey, apiSecret, baseUrl = 'https://test-merchant.ebioro.com') {
        this.apiKey = apiKey;
        this.apiSecret = apiSecret;
        this.baseUrl = baseUrl;
        this.lastRequest = null;
        this.lastResponse = null;
    }
    
    /**
     * Generate HMAC-SHA256 signature
     * Payload format: path + timestamp + method + body
     */
    generateSignature(path, timestamp, method, body) {
        const payloadString = path + timestamp + method + body;
        const hmac = crypto.createHmac('sha256', this.apiSecret);
        hmac.update(payloadString, 'utf8');
        return hmac.digest('hex');
    }
    
    /**
     * Generate authentication headers
     */
    generateHeaders(method, path, body) {
        const timestamp = Math.floor(Date.now() / 1000).toString();
        const signature = this.generateSignature(path, timestamp, method, body);
        
        return {
            'Content-Type': 'application/json',
            'X-Digest-Key': this.apiKey,
            'X-Digest-Timestamp': timestamp,
            'X-Digest-Signature': signature
        };
    }
    
    /**
     * Make authenticated API request
     */
    async makeRequest(method, path, requestBody = null) {
        const bodyJson = requestBody ? JSON.stringify(requestBody, null, 0) : '';
        const headers = this.generateHeaders(method, path, bodyJson);
        const url = new URL(this.baseUrl + path);
        
        // Store request details
        this.lastRequest = {
            method,
            url: url.href,
            headers,
            body: bodyJson,
            timestamp: new Date().toISOString()
        };
        
        const options = {
            hostname: url.hostname,
            port: url.port || (url.protocol === 'https:' ? 443 : 80),
            path: url.pathname + url.search,
            method: method.toUpperCase(),
            headers: headers,
            timeout: 30000
        };
        
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            const httpModule = url.protocol === 'https:' ? https : http;
            
            const req = httpModule.request(options, (res) => {
                let responseData = '';
                
                res.on('data', (chunk) => {
                    responseData += chunk;
                });
                
                res.on('end', () => {
                    const elapsedTime = (Date.now() - startTime) / 1000;
                    
                    // Store response details
                    this.lastResponse = {
                        statusCode: res.statusCode,
                        body: responseData,
                        elapsedTime,
                        timestamp: new Date().toISOString()
                    };
                    
                    resolve(new ApiResponse(res.statusCode, responseData, elapsedTime));
                });
            });
            
            req.on('error', (error) => {
                reject(new Error(`Request failed: ${error.message}`));
            });
            
            req.on('timeout', () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });
            
            // Send request body for POST/PUT requests
            if (['POST', 'PUT'].includes(method.toUpperCase()) && bodyJson) {
                req.write(bodyJson);
            }
            
            req.end();
        });
    }
    
    /**
     * Create a payment
     */
    async createPayment(paymentData) {
        return this.makeRequest('POST', '/payments', paymentData);
    }
    
    /**
     * Get a specific payment
     */
    async getPayment(paymentId) {
        return this.makeRequest('GET', `/payments/${paymentId}`);
    }
    
    /**
     * Get all payments
     */
    async getAllPayments() {
        return this.makeRequest('GET', '/payments');
    }
    
    /**
     * Create a refund
     */
    async createRefund(paymentId, refundData) {
        return this.makeRequest('POST', `/payments/${paymentId}/refunds`, refundData);
    }
    
    /**
     * Get all refunds
     */
    async getAllRefunds() {
        return this.makeRequest('GET', '/refunds');
    }
    
    /**
     * Get account balances
     */
    async getAccountBalances() {
        return this.makeRequest('GET', '/accounts/balances');
    }
    
    /**
     * Test authentication
     */
    async testAuthentication() {
        return this.makeRequest('GET', '/payments');
    }
    
    /**
     * Get last request details
     */
    getLastRequest() {
        return this.lastRequest;
    }
    
    /**
     * Get last response details
     */
    getLastResponse() {
        return this.lastResponse;
    }
}

/**
 * API Response wrapper
 */
class ApiResponse {
    constructor(statusCode, body, elapsedTime) {
        this.statusCode = statusCode;
        this.body = body;
        this.elapsedTime = elapsedTime;
        this.data = null;
        
        try {
            this.data = JSON.parse(body);
        } catch (error) {
            // Body is not valid JSON
            this.data = null;
        }
    }
    
    getStatusCode() {
        return this.statusCode;
    }
    
    getBody() {
        return this.body;
    }
    
    getData() {
        return this.data;
    }
    
    getElapsedTime() {
        return this.elapsedTime;
    }
    
    isSuccess() {
        return this.statusCode >= 200 && this.statusCode < 300;
    }
    
    toObject() {
        return {
            statusCode: this.statusCode,
            body: this.body,
            data: this.data,
            elapsedTime: this.elapsedTime,
            success: this.isSuccess()
        };
    }
}

// Export for use as module
module.exports = {
    EbioroApiClient,
    ApiResponse
};

// Example usage (only runs when script is executed directly)
if (require.main === module) {
    async function example() {
        try {
            // Initialize client
            const client = new EbioroApiClient(
                process.env.API_KEY,
                process.env.API_SECRET_KEY
            );
            
            // Test authentication
            const authResponse = await client.testAuthentication();
            console.log('Auth test:', authResponse.getStatusCode());
            
            // Create payment
            const paymentData = {
                amount: 1000,
                currency: 'USD',
                description: 'Test payment from Node.js client'
            };
            
            const paymentResponse = await client.createPayment(paymentData);
            console.log('Payment creation:', paymentResponse.getStatusCode());
            console.log('Response:', paymentResponse.getBody());
            
        } catch (error) {
            console.error('Error:', error.message);
        }
    }
    
    example();
}