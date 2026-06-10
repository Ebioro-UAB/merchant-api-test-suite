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
        // Parse the URL FIRST and sign the normalized path. WHATWG URL parsing
        // normalizes percent-encoding and dot segments, so signing the raw input
        // could produce a signature over a different string than the one
        // actually transmitted on the wire.
        const url = new URL(this.baseUrl + path);
        const signedPath = url.pathname + url.search;
        const headers = this.generateHeaders(method, signedPath, bodyJson);

        // Store request details. Auth headers are NOT stored: this snapshot is
        // surfaced by debugging endpoints (web UI /api/get-last-request) and
        // must never reflect the API key or a valid signature back to a caller.
        this.lastRequest = {
            method,
            url: url.href,
            headers: EbioroApiClient.redactAuthHeaders(headers),
            body: bodyJson,
            timestamp: new Date().toISOString()
        };

        const options = {
            hostname: url.hostname,
            port: url.port || (url.protocol === 'https:' ? 443 : 80),
            path: signedPath,
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
     * URL-encode a path parameter so untrusted ids cannot alter the request path.
     */
    static pathParam(value) {
        return encodeURIComponent(String(value));
    }

    /**
     * Return a copy of the headers with credential material removed.
     */
    static redactAuthHeaders(headers) {
        const redacted = { ...headers };
        for (const sensitive of ['X-Digest-Key', 'X-Digest-Signature']) {
            if (sensitive in redacted) {
                redacted[sensitive] = '[REDACTED]';
            }
        }
        return redacted;
    }

    /**
     * Create a payment
     */
    async createPayment(paymentData) {
        return this.makeRequest('POST', '/payments', paymentData);
    }

    /**
     * Create a shareable payment link.
     *
     * A payment link is a payment with a longer expiry window. Omit redirectUrl
     * for the Ebioro-hosted confirmation screen. The response contains shortUrl —
     * the link to share with the payer.
     *
     * If paymentData already contains expiresInHours, that value takes
     * precedence over the expiresInHours parameter.
     */
    async createPaymentLink(paymentData, expiresInHours = 168) {
        return this.makeRequest('POST', '/payments', { expiresInHours, ...paymentData });
    }

    /**
     * Get a specific payment
     */
    async getPayment(paymentId) {
        return this.makeRequest('GET', `/payments/${EbioroApiClient.pathParam(paymentId)}`);
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
        return this.makeRequest('POST', `/payments/${EbioroApiClient.pathParam(paymentId)}/refunds`, refundData);
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
     * Create an invoice (line items + optional single tax percentage).
     *
     * The response includes payment_id — fetch that payment via getPayment()
     * to obtain the shareable payment link (shortUrl) for the customer.
     */
    async createInvoice(invoiceData) {
        return this.makeRequest('POST', '/invoices', invoiceData);
    }

    /**
     * List invoices (paginated). The query string is part of the signed path.
     */
    async getInvoices(page = 1, limit = 20) {
        const query = new URLSearchParams({ page: String(page), limit: String(limit) }).toString();
        return this.makeRequest('GET', `/invoices?${query}`);
    }

    /**
     * Get a specific invoice
     */
    async getInvoice(invoiceId) {
        return this.makeRequest('GET', `/invoices/${EbioroApiClient.pathParam(invoiceId)}`);
    }

    /**
     * Cancel (void) an unpaid invoice and expire its payment link
     */
    async cancelInvoice(invoiceId) {
        return this.makeRequest('POST', `/invoices/${EbioroApiClient.pathParam(invoiceId)}/cancel`);
    }

    /**
     * Get invoice numbering settings (prefix + next number)
     */
    async getInvoiceSettings() {
        return this.makeRequest('GET', '/invoices/settings');
    }

    /**
     * Update invoice numbering settings (invoice_prefix and/or next_number)
     */
    async updateInvoiceSettings(settings) {
        return this.makeRequest('POST', '/invoices/settings', settings);
    }

    /**
     * Verify the X-WEBHOOK-AUTH signature of an incoming webhook.
     *
     * Always verify before processing a webhook. Pass the RAW request body
     * (string or Buffer) exactly as received — re-serializing the parsed JSON
     * can change the bytes and break verification. Constant-time comparison.
     */
    static verifyWebhookSignature(rawBody, signature, apiSecret) {
        if (typeof rawBody !== 'string' && !Buffer.isBuffer(rawBody)) {
            throw new TypeError('rawBody must be the raw request body (string or Buffer), not a parsed object');
        }
        if (!signature || !apiSecret) {
            return false;
        }
        const expected = crypto
            .createHmac('sha256', apiSecret)
            .update(rawBody)
            .digest('hex');
        const expectedBuf = Buffer.from(expected, 'utf8');
        const signatureBuf = Buffer.from(String(signature), 'utf8');
        if (expectedBuf.length !== signatureBuf.length) {
            return false;
        }
        return crypto.timingSafeEqual(expectedBuf, signatureBuf);
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
                process.env.EBIORO_API_KEY,
                process.env.EBIORO_API_SECRET
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