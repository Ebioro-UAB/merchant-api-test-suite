import unittest
from unittest.mock import patch, MagicMock
from clients.python.ebioro_client import EbioroApiClient
from utils import ResponseValidator, TestDataGenerator
from logger_config import logger
import json

class TestEndpoints(unittest.TestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.client = EbioroApiClient(
            api_key="test_key",
            api_secret="test_secret",
            base_url="https://test-merchant.ebioro.com"
        )
    
    @patch('requests.Session.request')
    def test_create_payment_success(self, mock_request):
        """Test successful payment creation"""
        logger.log_test_start("Create Payment Success")
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "pay_123",
            "amount": {"currency": "USD", "value": 1000},
            "status": "pending",
            "createdAt": "2023-01-01T00:00:00Z",
            "redirectUrl": "https://checkout.ebioro.com/pay_123"
        }
        mock_request.return_value = mock_response
        
        # Test payment creation
        payment_data = TestDataGenerator.generate_payment_payload()
        status_code, response_data, elapsed_time = self.client.create_payment(payment_data)
        
        # Verify request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        
        self.assertEqual(call_args[1]['method'], 'POST')
        self.assertTrue(call_args[1]['url'].endswith('/payments'))
        self.assertEqual(call_args[1]['json'], payment_data)
        
        # Verify response
        self.assertEqual(status_code, 201)
        self.assertEqual(response_data['id'], 'pay_123')
        self.assertEqual(response_data['status'], 'pending')
        
        logger.log_test_result("Create Payment Success", True, f"Payment created with ID: {response_data['id']}")
    
    @patch('requests.Session.request')
    def test_create_payment_validation_error(self, mock_request):
        """Test payment creation with validation error"""
        logger.log_test_start("Create Payment Validation Error")
        
        # Mock validation error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "validation_error",
            "message": "Invalid amount value",
            "details": {
                "field": "amount.value",
                "code": "invalid_value"
            }
        }
        mock_request.return_value = mock_response
        
        # Test with invalid payment data
        invalid_payment_data = TestDataGenerator.generate_payment_payload()
        invalid_payment_data['amount']['value'] = -100  # Invalid negative amount
        
        status_code, response_data, elapsed_time = self.client.create_payment(invalid_payment_data)
        
        # Verify error response
        self.assertEqual(status_code, 400)
        self.assertEqual(response_data['error'], 'validation_error')
        self.assertIn('Invalid amount value', response_data['message'])
        
        logger.log_test_result("Create Payment Validation Error", True, "Validation error handled correctly")
    
    @patch('requests.Session.request')
    def test_get_payment_success(self, mock_request):
        """Test successful payment retrieval"""
        logger.log_test_start("Get Payment Success")
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "pay_123",
            "amount": {"currency": "USD", "value": 1000},
            "status": "completed",
            "createdAt": "2023-01-01T00:00:00Z",
            "completedAt": "2023-01-01T00:05:00Z"
        }
        mock_request.return_value = mock_response
        
        # Test payment retrieval
        payment_id = "pay_123"
        status_code, response_data, elapsed_time = self.client.get_payment(payment_id)
        
        # Verify request
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        
        self.assertEqual(call_args[1]['method'], 'GET')
        self.assertTrue(call_args[1]['url'].endswith(f'/payments/{payment_id}'))
        
        # Verify response
        self.assertEqual(status_code, 200)
        self.assertEqual(response_data['id'], payment_id)
        self.assertEqual(response_data['status'], 'completed')
        
        logger.log_test_result("Get Payment Success", True, f"Retrieved payment: {payment_id}")
    
    @patch('requests.Session.request')
    def test_get_payment_not_found(self, mock_request):
        """Test payment retrieval when payment not found"""
        logger.log_test_start("Get Payment Not Found")
        
        # Mock not found response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "error": "not_found",
            "message": "Payment not found"
        }
        mock_request.return_value = mock_response
        
        # Test with non-existent payment ID
        payment_id = "pay_nonexistent"
        status_code, response_data, elapsed_time = self.client.get_payment(payment_id)
        
        # Verify error response
        self.assertEqual(status_code, 404)
        self.assertEqual(response_data['error'], 'not_found')
        
        logger.log_test_result("Get Payment Not Found", True, "404 error handled correctly")
    
    @patch('requests.Session.request')
    def test_get_all_payments_success(self, mock_request):
        """Test successful retrieval of all payments"""
        logger.log_test_start("Get All Payments Success")
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "payments": [
                {
                    "id": "pay_123",
                    "amount": {"currency": "USD", "value": 1000},
                    "status": "completed",
                    "createdAt": "2023-01-01T00:00:00Z"
                },
                {
                    "id": "pay_456",
                    "amount": {"currency": "USD", "value": 2000},
                    "status": "pending",
                    "createdAt": "2023-01-01T01:00:00Z"
                }
            ],
            "total": 2,
            "page": 1,
            "pageSize": 20
        }
        mock_request.return_value = mock_response
        
        # Test retrieval of all payments
        status_code, response_data, elapsed_time = self.client.get_all_payments()
        
        # Verify request
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        
        self.assertEqual(call_args[1]['method'], 'GET')
        self.assertTrue(call_args[1]['url'].endswith('/payments'))
        
        # Verify response
        self.assertEqual(status_code, 200)
        self.assertEqual(len(response_data['payments']), 2)
        self.assertEqual(response_data['total'], 2)
        
        logger.log_test_result("Get All Payments Success", True, f"Retrieved {response_data['total']} payments")
    
    @patch('requests.Session.request')
    def test_create_refund_success(self, mock_request):
        """Test successful refund creation"""
        logger.log_test_start("Create Refund Success")
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "ref_123",
            "paymentId": "pay_123",
            "amount": {"currency": "USD", "value": 500},
            "status": "pending",
            "createdAt": "2023-01-01T00:00:00Z"
        }
        mock_request.return_value = mock_response
        
        # Test refund creation
        payment_id = "pay_123"
        refund_data = TestDataGenerator.generate_refund_payload()
        status_code, response_data, elapsed_time = self.client.create_refund(payment_id, refund_data)
        
        # Verify request
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        
        self.assertEqual(call_args[1]['method'], 'POST')
        self.assertTrue(call_args[1]['url'].endswith(f'/payments/{payment_id}/refunds'))
        self.assertEqual(call_args[1]['json'], refund_data)
        
        # Verify response
        self.assertEqual(status_code, 201)
        self.assertEqual(response_data['id'], 'ref_123')
        self.assertEqual(response_data['paymentId'], payment_id)
        
        logger.log_test_result("Create Refund Success", True, f"Refund created with ID: {response_data['id']}")
    
    @patch('requests.Session.request')
    def test_get_account_balances_success(self, mock_request):
        """Test successful account balance retrieval"""
        logger.log_test_start("Get Account Balances Success")
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "balances": [
                {
                    "asset": "USDC",
                    "balance": "1000.00",
                    "available": "950.00",
                    "pending": "50.00"
                }
            ]
        }
        mock_request.return_value = mock_response
        
        # Test balance retrieval
        status_code, response_data, elapsed_time = self.client.get_account_balances()
        
        # Verify request
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        
        self.assertEqual(call_args[1]['method'], 'GET')
        self.assertTrue(call_args[1]['url'].endswith('/accounts/balances'))
        
        # Verify response
        self.assertEqual(status_code, 200)
        self.assertEqual(len(response_data['balances']), 1)
        self.assertEqual(response_data['balances'][0]['asset'], 'USDC')
        
        logger.log_test_result("Get Account Balances Success", True, "Account balances retrieved successfully")
    
    @patch('requests.Session.request')
    def test_authentication_test(self, mock_request):
        """Test authentication testing functionality"""
        logger.log_test_start("Authentication Test")
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"payments": []}
        mock_request.return_value = mock_response
        
        # Test authentication
        auth_result = self.client.test_authentication()
        
        # Verify result
        self.assertTrue(auth_result["success"])
        self.assertEqual(auth_result["status_code"], 200)
        self.assertIn("response", auth_result)
        
        logger.log_test_result("Authentication Test", True, "Authentication test passed")
    
    @patch('requests.Session.request')
    def test_authentication_failure(self, mock_request):
        """Test authentication failure"""
        logger.log_test_start("Authentication Failure")
        
        # Mock authentication failure response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": "unauthorized",
            "message": "Invalid API credentials"
        }
        mock_request.return_value = mock_response
        
        # Test authentication failure
        auth_result = self.client.test_authentication()
        
        # Verify result
        self.assertFalse(auth_result["success"])
        self.assertEqual(auth_result["status_code"], 401)
        self.assertEqual(auth_result["response"]["error"], "unauthorized")
        
        logger.log_test_result("Authentication Failure", True, "Authentication failure handled correctly")
    
    def test_response_validation(self):
        """Test response validation functionality"""
        logger.log_test_start("Response Validation")
        
        # Test valid payment response
        valid_response = {
            "id": "pay_123",
            "amount": {"currency": "USD", "value": 1000},
            "status": "pending",
            "createdAt": "2023-01-01T00:00:00Z"
        }
        
        validation_result = ResponseValidator.validate_payment_response(valid_response)
        self.assertTrue(validation_result["valid"])
        self.assertEqual(len(validation_result["errors"]), 0)
        
        # Test invalid payment response
        invalid_response = {
            "id": "pay_123",
            "amount": {"currency": "USD"},  # Missing value
            "status": "invalid_status"  # Invalid status
        }
        
        validation_result = ResponseValidator.validate_payment_response(invalid_response)
        self.assertFalse(validation_result["valid"])
        self.assertGreater(len(validation_result["errors"]), 0)
        
        logger.log_test_result("Response Validation", True, "Response validation works correctly")
    
    def test_signature_implementation_validation(self):
        """Test signature implementation validation"""
        logger.log_test_start("Signature Implementation Validation")
        
        # Test signature validation with test cases
        validation_result = self.client.validate_signature_implementation()
        
        # Verify validation result structure
        self.assertIn("total_tests", validation_result)
        self.assertIn("passed", validation_result)
        self.assertIn("failed", validation_result)
        self.assertIn("results", validation_result)
        
        # All test cases should pass
        self.assertEqual(validation_result["failed"], 0)
        self.assertGreater(validation_result["passed"], 0)
        
        logger.log_test_result("Signature Implementation Validation", True, 
                              f"Passed {validation_result['passed']}/{validation_result['total_tests']} tests")

if __name__ == '__main__':
    unittest.main()
