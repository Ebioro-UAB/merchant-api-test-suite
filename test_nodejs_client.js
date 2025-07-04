// Test script for Node.js Ebioro API client
const { EbioroApiClient } = require('./clients/nodejs/ebioro-client.js');

async function testNodejsClient() {
    // Use test credentials (these are public test keys)
    const apiKey = "pk_testrSWmOfY4FJo3fDEDQb3xf0L/djbB2vFwMzam/x4OMGg=";
    const apiSecret = "sk_testR3tSbF78YLHwNod9T3fBV0+cFkS0t2mJSbv71EwJjPg=";
    
    console.log("Testing Node.js Ebioro API Client");
    console.log("=====================================");
    
    try {
        // Initialize client
        const client = new EbioroApiClient(apiKey, apiSecret);
        console.log("✅ Client initialized");
        
        // Test authentication
        console.log("\n🔐 Testing authentication...");
        const authResponse = await client.testAuthentication();
        
        console.log(`Status Code: ${authResponse.getStatusCode()}`);
        console.log(`Success: ${authResponse.isSuccess()}`);
        console.log(`Elapsed Time: ${authResponse.getElapsedTime().toFixed(3)}s`);
        
        if (authResponse.isSuccess()) {
            console.log("✅ Authentication successful!");
            
            // Test payment creation
            console.log("\n💳 Testing payment creation...");
            const paymentData = {
                amount: 1000,
                currency: "USD",
                description: "Test payment from Node.js client"
            };
            
            const paymentResponse = await client.createPayment(paymentData);
            console.log(`Payment Status: ${paymentResponse.getStatusCode()}`);
            console.log(`Payment Success: ${paymentResponse.isSuccess()}`);
            console.log(`Payment Response: ${paymentResponse.getBody()}`);
            
            if (paymentResponse.isSuccess()) {
                console.log("✅ Payment creation successful!");
            } else {
                console.log("❌ Payment creation failed");
            }
        } else {
            console.log("❌ Authentication failed");
            console.log(`Response: ${authResponse.getBody()}`);
        }
        
    } catch (error) {
        console.error("❌ Test failed with error:", error.message);
        console.error("Stack trace:", error.stack);
    }
}

// Run the test
testNodejsClient().then(() => {
    console.log("\n🏁 Node.js client test completed");
}).catch(error => {
    console.error("💥 Test crashed:", error);
});