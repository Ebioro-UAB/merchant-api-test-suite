using System;
using System.Threading.Tasks;

class TestCSharpClient
{
    static async Task Main(string[] args)
    {
        try
        {
            // Test credentials
            string apiKey = "pk_testrSWmOfY4FJo3fDEDQb3xf0L/djbB2vFwMzam/x4OMGg=";
            string apiSecret = "sk_testEaFcSJwPgRKyYmLkAJwHdLuRXNYFzIcGUjr4u7ZMgVjNmEWs";
            
            Console.WriteLine("Testing C# Ebioro API Client");
            Console.WriteLine("=====================================");
            
            // Initialize client
            var client = new EbioroApiClient(apiKey, apiSecret);
            Console.WriteLine("✅ Client initialized");
            
            // Test authentication
            Console.WriteLine("\n🔐 Testing authentication...");
            var authResponse = await client.TestAuthenticationAsync();
            Console.WriteLine($"Status Code: {authResponse.StatusCode}");
            Console.WriteLine($"Response: {authResponse.Body}");
            
            if (authResponse.StatusCode == 200)
            {
                Console.WriteLine("✅ Authentication successful!");
            }
            else
            {
                Console.WriteLine("❌ Authentication failed");
            }
            
            Console.WriteLine("\n🏁 C# client test completed");
        }
        catch (Exception e)
        {
            Console.WriteLine($"❌ Test failed: {e.Message}");
        }
    }
}