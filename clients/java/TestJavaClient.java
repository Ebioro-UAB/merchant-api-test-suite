/**
 * Simple test for Java Ebioro API Client
 */
public class TestJavaClient {
    public static void main(String[] args) {
        try {
            // Test credentials
            String apiKey = "pk_testrSWmOfY4FJo3fDEDQb3xf0L/djbB2vFwMzam/x4OMGg=";
            String apiSecret = "sk_testEaFcSJwPgRKyYmLkAJwHdLuRXNYFzIcGUjr4u7ZMgVjNmEWs";
            
            System.out.println("Testing Java Ebioro API Client");
            System.out.println("=====================================");
            
            // Initialize client
            EbioroApiClient client = new EbioroApiClient(apiKey, apiSecret);
            System.out.println("✅ Client initialized");
            
            // Test authentication
            System.out.println("\n🔐 Testing authentication...");
            EbioroApiClient.ApiResponse authResponse = client.testAuthentication();
            System.out.println("Status Code: " + authResponse.getStatusCode());
            System.out.println("Response: " + authResponse.getBody());
            
            if (authResponse.getStatusCode() == 200) {
                System.out.println("✅ Authentication successful!");
            } else {
                System.out.println("❌ Authentication failed");
            }
            
            System.out.println("\n🏁 Java client test completed");
            
        } catch (Exception e) {
            System.err.println("❌ Test failed: " + e.getMessage());
            e.printStackTrace();
        }
    }
}