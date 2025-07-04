using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace Ebioro.Api
{
    /// <summary>
    /// Ebioro API Client for C#
    /// 
    /// This client implements HMAC-SHA256 authentication for the Ebioro Merchant API.
    /// Signature format: path + timestamp + method + body
    /// 
    /// Usage:
    /// var client = new EbioroApiClient(apiKey, apiSecret);
    /// var response = await client.CreatePaymentAsync(paymentData);
    /// </summary>
    public class EbioroApiClient : IDisposable
    {
        private readonly string _apiKey;
        private readonly string _apiSecret;
        private readonly string _baseUrl;
        private readonly HttpClient _httpClient;
        private ApiRequestDetails _lastRequest;
        private ApiResponseDetails _lastResponse;
        private bool _disposed;

        public EbioroApiClient(string apiKey, string apiSecret, string baseUrl = "https://test-merchant.ebioro.com")
        {
            _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));
            _apiSecret = apiSecret ?? throw new ArgumentNullException(nameof(apiSecret));
            _baseUrl = baseUrl ?? throw new ArgumentNullException(nameof(baseUrl));
            
            _httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromSeconds(30)
            };
        }

        /// <summary>
        /// Generate HMAC-SHA256 signature
        /// Payload format: path + timestamp + method + body
        /// </summary>
        private string GenerateSignature(string path, string timestamp, string method, string body)
        {
            var payloadString = path + timestamp + method + body;
            var keyBytes = Encoding.UTF8.GetBytes(_apiSecret);
            var payloadBytes = Encoding.UTF8.GetBytes(payloadString);

            using (var hmac = new HMACSHA256(keyBytes))
            {
                var signatureBytes = hmac.ComputeHash(payloadBytes);
                return Convert.ToHexString(signatureBytes).ToLowerInvariant();
            }
        }

        /// <summary>
        /// Generate authentication headers
        /// </summary>
        private Dictionary<string, string> GenerateHeaders(string method, string path, string body)
        {
            var timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString();
            var signature = GenerateSignature(path, timestamp, method, body);

            return new Dictionary<string, string>
            {
                { "Content-Type", "application/json" },
                { "X-Digest-Key", _apiKey },
                { "X-Digest-Timestamp", timestamp },
                { "X-Digest-Signature", signature }
            };
        }

        /// <summary>
        /// Make authenticated API request
        /// </summary>
        private async Task<ApiResponse> MakeRequestAsync(string method, string path, object requestBody = null)
        {
            var bodyJson = string.Empty;
            if (requestBody != null)
            {
                bodyJson = JsonSerializer.Serialize(requestBody, new JsonSerializerOptions
                {
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });
            }

            var headers = GenerateHeaders(method, path, bodyJson);
            var url = _baseUrl + path;

            // Store request details
            _lastRequest = new ApiRequestDetails
            {
                Method = method,
                Url = url,
                Headers = headers,
                Body = bodyJson,
                Timestamp = DateTime.UtcNow
            };

            var request = new HttpRequestMessage(new HttpMethod(method), url);

            // Add headers
            foreach (var header in headers)
            {
                if (header.Key == "Content-Type")
                    continue; // Will be set with content
                request.Headers.Add(header.Key, header.Value);
            }

            // Add body for POST/PUT requests
            if (method.Equals("POST", StringComparison.OrdinalIgnoreCase) || 
                method.Equals("PUT", StringComparison.OrdinalIgnoreCase))
            {
                if (!string.IsNullOrEmpty(bodyJson))
                {
                    request.Content = new StringContent(bodyJson, Encoding.UTF8, "application/json");
                }
            }

            var startTime = DateTime.UtcNow;
            var response = await _httpClient.SendAsync(request);
            var elapsedTime = (DateTime.UtcNow - startTime).TotalSeconds;

            var responseBody = await response.Content.ReadAsStringAsync();

            // Store response details
            _lastResponse = new ApiResponseDetails
            {
                StatusCode = (int)response.StatusCode,
                Body = responseBody,
                ElapsedTime = elapsedTime,
                Timestamp = DateTime.UtcNow
            };

            return new ApiResponse((int)response.StatusCode, responseBody, elapsedTime);
        }

        /// <summary>
        /// Create a payment
        /// </summary>
        public async Task<ApiResponse> CreatePaymentAsync(object paymentData)
        {
            return await MakeRequestAsync("POST", "/api/v1/payments", paymentData);
        }

        /// <summary>
        /// Get a specific payment
        /// </summary>
        public async Task<ApiResponse> GetPaymentAsync(string paymentId)
        {
            return await MakeRequestAsync("GET", $"/api/v1/payments/{paymentId}");
        }

        /// <summary>
        /// Get all payments
        /// </summary>
        public async Task<ApiResponse> GetAllPaymentsAsync()
        {
            return await MakeRequestAsync("GET", "/api/v1/payments");
        }

        /// <summary>
        /// Create a refund
        /// </summary>
        public async Task<ApiResponse> CreateRefundAsync(string paymentId, object refundData)
        {
            return await MakeRequestAsync("POST", $"/api/v1/payments/{paymentId}/refunds", refundData);
        }

        /// <summary>
        /// Get all refunds
        /// </summary>
        public async Task<ApiResponse> GetAllRefundsAsync()
        {
            return await MakeRequestAsync("GET", "/api/v1/refunds");
        }

        /// <summary>
        /// Get account balances
        /// </summary>
        public async Task<ApiResponse> GetAccountBalancesAsync()
        {
            return await MakeRequestAsync("GET", "/api/v1/account/balances");
        }

        /// <summary>
        /// Test authentication
        /// </summary>
        public async Task<ApiResponse> TestAuthenticationAsync()
        {
            return await MakeRequestAsync("GET", "/api/v1/payments");
        }

        /// <summary>
        /// Get last request details
        /// </summary>
        public ApiRequestDetails GetLastRequest()
        {
            return _lastRequest;
        }

        /// <summary>
        /// Get last response details
        /// </summary>
        public ApiResponseDetails GetLastResponse()
        {
            return _lastResponse;
        }

        public void Dispose()
        {
            if (!_disposed)
            {
                _httpClient?.Dispose();
                _disposed = true;
            }
        }
    }

    /// <summary>
    /// API Response wrapper
    /// </summary>
    public class ApiResponse
    {
        public int StatusCode { get; }
        public string Body { get; }
        public double ElapsedTime { get; }
        public object Data { get; }

        public ApiResponse(int statusCode, string body, double elapsedTime)
        {
            StatusCode = statusCode;
            Body = body;
            ElapsedTime = elapsedTime;
            
            try
            {
                Data = JsonSerializer.Deserialize<object>(body);
            }
            catch
            {
                Data = null;
            }
        }

        public bool IsSuccess => StatusCode >= 200 && StatusCode < 300;

        public T GetData<T>() where T : class
        {
            try
            {
                return JsonSerializer.Deserialize<T>(Body, new JsonSerializerOptions
                {
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });
            }
            catch
            {
                return null;
            }
        }
    }

    /// <summary>
    /// API Request details
    /// </summary>
    public class ApiRequestDetails
    {
        public string Method { get; set; }
        public string Url { get; set; }
        public Dictionary<string, string> Headers { get; set; }
        public string Body { get; set; }
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// API Response details
    /// </summary>
    public class ApiResponseDetails
    {
        public int StatusCode { get; set; }
        public string Body { get; set; }
        public double ElapsedTime { get; set; }
        public DateTime Timestamp { get; set; }
    }
}

// Example usage
/*
using System;
using System.Threading.Tasks;

class Program
{
    static async Task Main(string[] args)
    {
        try
        {
            // Initialize client
            using var client = new EbioroApiClient(
                Environment.GetEnvironmentVariable("API_KEY"),
                Environment.GetEnvironmentVariable("API_SECRET_KEY")
            );

            // Test authentication
            var authResponse = await client.TestAuthenticationAsync();
            Console.WriteLine($"Auth test: {authResponse.StatusCode}");

            // Create payment
            var paymentData = new
            {
                amount = 1000,
                currency = "USD",
                description = "Test payment from C# client"
            };

            var paymentResponse = await client.CreatePaymentAsync(paymentData);
            Console.WriteLine($"Payment creation: {paymentResponse.StatusCode}");
            Console.WriteLine($"Response: {paymentResponse.Body}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}
*/