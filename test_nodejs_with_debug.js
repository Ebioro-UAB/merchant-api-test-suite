// Enhanced test script with debug output
const { EbioroApiClient } = require('./clients/nodejs/ebioro-client.js');

class DebugEbioroApiClient extends EbioroApiClient {
    generateHeaders(method, path, body) {
        const timestamp = Math.floor(Date.now() / 1000).toString();
        const signature = this.generateSignature(path, timestamp, method, body);
        
        console.log('=== Request Debug Info ===');
        console.log(`Method: ${method}`);
        console.log(`Path: ${path}`);
        console.log(`Body: ${body}`);
        console.log(`Timestamp: ${timestamp}`);
        console.log(`Payload String: ${path + timestamp + method + body}`);
        console.log(`Signature: ${signature}`);
        
        return {
            'Content-Type': 'application/json',
            'X-API-Key': this.apiKey,
            'X-Timestamp': timestamp,
            'X-Signature': signature
        };
    }
}

async function testNodejsClientWithDebug() {
    // Use test credentials
    const apiKey = "pk_testrSWmOfY4FJo3fDEDQb3xf0L/djbB2vFwMzam/x4OMGg=";
    const apiSecret = "sk_testR3tSbF78YLHwNod9T3fBV0+cFkS0t2mJSbv71EwJjPg=";
    
    console.log("Testing Node.js Ebioro API Client with Debug");
    console.log("============================================");
    
    try {
        const client = new DebugEbioroApiClient(apiKey, apiSecret);
        console.log("✅ Debug client initialized");
        
        console.log("\n🔐 Testing authentication with debug info...");
        const authResponse = await client.testAuthentication();
        
        console.log('\n=== Response Info ===');
        console.log(`Status Code: ${authResponse.getStatusCode()}`);
        console.log(`Success: ${authResponse.isSuccess()}`);
        console.log(`Elapsed Time: ${authResponse.getElapsedTime().toFixed(3)}s`);
        console.log(`Response Body: ${authResponse.getBody()}`);
        
        if (authResponse.isSuccess()) {
            console.log("✅ Authentication successful!");
        } else {
            console.log("❌ Authentication failed");
            
            // Let's also test the Python client for comparison
            console.log("\n🐍 Comparing with Python client...");
            const { spawn } = require('child_process');
            
            const pythonTest = spawn('python3', ['-c', `
from ebioro_client import EbioroApiClient
client = EbioroApiClient("${apiKey}", "${apiSecret}")
result = client.test_authentication()
print(f"Python Status: {result.get('status_code', 'unknown')}")
print(f"Python Success: {result.get('success', False)}")
print(f"Python Response: {result.get('response', {})}")
            `]);
            
            pythonTest.stdout.on('data', (data) => {
                console.log(`Python output: ${data}`);
            });
            
            pythonTest.stderr.on('data', (data) => {
                console.log(`Python error: ${data}`);
            });
        }
        
    } catch (error) {
        console.error("❌ Test failed with error:", error.message);
        console.error("Stack trace:", error.stack);
    }
}

testNodejsClientWithDebug().then(() => {
    console.log("\n🏁 Debug test completed");
}).catch(error => {
    console.error("💥 Test crashed:", error);
});