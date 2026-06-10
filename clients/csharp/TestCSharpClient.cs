using System;
using System.Threading.Tasks;

class TestCSharpClient
{
    static async Task Main(string[] args)
    {
        try
        {
            // Test credentials
            string apiKey = Environment.GetEnvironmentVariable("EBIORO_API_KEY");
            string apiSecret = Environment.GetEnvironmentVariable("EBIORO_API_SECRET");
            
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