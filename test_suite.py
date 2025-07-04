import unittest
import sys
import json
import time
from typing import Dict, Any, List
from config import config
from clients.python.ebioro_client import EbioroApiClient
from utils import TestDataGenerator, ValidationError
from logger_config import logger
from test_authentication import TestAuthentication
from test_endpoints import TestEndpoints

class ComprehensiveTestSuite:
    """Comprehensive test suite for Ebioro API integration"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, base_url: str = None):
        self.api_key = api_key or config.API_KEY
        self.api_secret = api_secret or config.API_SECRET_KEY
        self.base_url = base_url or config.BASE_URL
        
        self.client = None
        self.test_results = []
        self.start_time = None
        
        # Initialize client if credentials are available
        if self.api_key and self.api_secret:
            try:
                self.client = EbioroApiClient(self.api_key, self.api_secret, self.base_url)
                logger.logger.info("✅ API client initialized successfully")
            except ValidationError as e:
                logger.logger.error(f"❌ Failed to initialize API client: {str(e)}")
        else:
            logger.logger.warning("⚠️  API credentials not provided - some tests will be skipped")
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests for authentication and endpoints"""
        logger.logger.info("🧪 Running unit tests...")
        
        # Create test suite
        test_suite = unittest.TestSuite()
        
        # Add authentication tests
        test_suite.addTest(unittest.makeSuite(TestAuthentication))
        
        # Add endpoint tests
        test_suite.addTest(unittest.makeSuite(TestEndpoints))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(test_suite)
        
        return {
            "total_tests": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "success": result.wasSuccessful(),
            "failure_details": [str(failure) for failure in result.failures],
            "error_details": [str(error) for error in result.errors]
        }
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests with real API"""
        if not self.client:
            return {
                "skipped": True,
                "reason": "API client not initialized - credentials missing"
            }
        
        logger.logger.info("🔗 Running integration tests...")
        
        integration_results = []
        
        # Test 1: Authentication
        auth_result = self._test_authentication()
        integration_results.append(auth_result)
        
        # Test 2: Payment Creation
        payment_result = self._test_payment_creation()
        integration_results.append(payment_result)
        
        # Test 3: Payment Retrieval
        if payment_result.get("success") and payment_result.get("payment_id"):
            retrieval_result = self._test_payment_retrieval(payment_result["payment_id"])
            integration_results.append(retrieval_result)
        
        # Test 4: List All Payments
        list_result = self._test_payment_listing()
        integration_results.append(list_result)
        
        # Test 5: Account Balances
        balance_result = self._test_account_balances()
        integration_results.append(balance_result)
        
        # Test 6: Error Handling
        error_result = self._test_error_handling()
        integration_results.append(error_result)
        
        # Calculate summary
        successful_tests = sum(1 for result in integration_results if result.get("success"))
        total_tests = len(integration_results)
        
        return {
            "total_tests": total_tests,
            "successful": successful_tests,
            "failed": total_tests - successful_tests,
            "success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            "results": integration_results
        }
    
    def _test_authentication(self) -> Dict[str, Any]:
        """Test API authentication"""
        logger.log_test_start("API Authentication")
        
        try:
            auth_result = self.client.test_authentication()
            
            if auth_result["success"]:
                logger.log_test_result("API Authentication", True, "Authentication successful")
                return {
                    "test_name": "API Authentication",
                    "success": True,
                    "status_code": auth_result["status_code"],
                    "elapsed_time": auth_result["elapsed_time"],
                    "details": "Authentication credentials are valid"
                }
            else:
                logger.log_test_result("API Authentication", False, f"Status: {auth_result['status_code']}")
                return {
                    "test_name": "API Authentication",
                    "success": False,
                    "status_code": auth_result["status_code"],
                    "error": auth_result.get("response", {}).get("message", "Authentication failed"),
                    "details": "Check API credentials"
                }
        
        except Exception as e:
            logger.log_test_result("API Authentication", False, f"Exception: {str(e)}")
            return {
                "test_name": "API Authentication",
                "success": False,
                "error": str(e),
                "details": "Exception occurred during authentication test"
            }
    
    def _test_payment_creation(self) -> Dict[str, Any]:
        """Test payment creation"""
        logger.log_test_start("Payment Creation")
        
        try:
            payment_data = TestDataGenerator.generate_payment_payload()
            status_code, response_data, elapsed_time = self.client.create_payment(payment_data)
            
            if status_code in [200, 201]:
                payment_id = response_data.get("id")
                logger.log_test_result("Payment Creation", True, f"Payment ID: {payment_id}")
                return {
                    "test_name": "Payment Creation",
                    "success": True,
                    "status_code": status_code,
                    "elapsed_time": elapsed_time,
                    "payment_id": payment_id,
                    "details": f"Payment created successfully with ID: {payment_id}"
                }
            else:
                error_msg = response_data.get("message", "Payment creation failed")
                logger.log_test_result("Payment Creation", False, f"Status: {status_code}, Error: {error_msg}")
                return {
                    "test_name": "Payment Creation",
                    "success": False,
                    "status_code": status_code,
                    "error": error_msg,
                    "details": "Payment creation failed"
                }
        
        except Exception as e:
            logger.log_test_result("Payment Creation", False, f"Exception: {str(e)}")
            return {
                "test_name": "Payment Creation",
                "success": False,
                "error": str(e),
                "details": "Exception occurred during payment creation"
            }
    
    def _test_payment_retrieval(self, payment_id: str) -> Dict[str, Any]:
        """Test payment retrieval"""
        logger.log_test_start("Payment Retrieval")
        
        try:
            status_code, response_data, elapsed_time = self.client.get_payment(payment_id)
            
            if status_code == 200:
                retrieved_id = response_data.get("id")
                logger.log_test_result("Payment Retrieval", True, f"Retrieved payment: {retrieved_id}")
                return {
                    "test_name": "Payment Retrieval",
                    "success": True,
                    "status_code": status_code,
                    "elapsed_time": elapsed_time,
                    "payment_id": retrieved_id,
                    "details": f"Payment retrieved successfully: {retrieved_id}"
                }
            else:
                error_msg = response_data.get("message", "Payment retrieval failed")
                logger.log_test_result("Payment Retrieval", False, f"Status: {status_code}, Error: {error_msg}")
                return {
                    "test_name": "Payment Retrieval",
                    "success": False,
                    "status_code": status_code,
                    "error": error_msg,
                    "details": "Payment retrieval failed"
                }
        
        except Exception as e:
            logger.log_test_result("Payment Retrieval", False, f"Exception: {str(e)}")
            return {
                "test_name": "Payment Retrieval",
                "success": False,
                "error": str(e),
                "details": "Exception occurred during payment retrieval"
            }
    
    def _test_payment_listing(self) -> Dict[str, Any]:
        """Test payment listing"""
        logger.log_test_start("Payment Listing")
        
        try:
            status_code, response_data, elapsed_time = self.client.get_all_payments()
            
            if status_code == 200:
                payments = response_data.get("payments", [])
                total = response_data.get("total", len(payments))
                logger.log_test_result("Payment Listing", True, f"Retrieved {total} payments")
                return {
                    "test_name": "Payment Listing",
                    "success": True,
                    "status_code": status_code,
                    "elapsed_time": elapsed_time,
                    "payment_count": total,
                    "details": f"Retrieved {total} payments successfully"
                }
            else:
                error_msg = response_data.get("message", "Payment listing failed")
                logger.log_test_result("Payment Listing", False, f"Status: {status_code}, Error: {error_msg}")
                return {
                    "test_name": "Payment Listing",
                    "success": False,
                    "status_code": status_code,
                    "error": error_msg,
                    "details": "Payment listing failed"
                }
        
        except Exception as e:
            logger.log_test_result("Payment Listing", False, f"Exception: {str(e)}")
            return {
                "test_name": "Payment Listing",
                "success": False,
                "error": str(e),
                "details": "Exception occurred during payment listing"
            }
    
    def _test_account_balances(self) -> Dict[str, Any]:
        """Test account balance retrieval"""
        logger.log_test_start("Account Balances")
        
        try:
            status_code, response_data, elapsed_time = self.client.get_account_balances()
            
            if status_code == 200:
                balances = response_data.get("balances", [])
                logger.log_test_result("Account Balances", True, f"Retrieved {len(balances)} balances")
                return {
                    "test_name": "Account Balances",
                    "success": True,
                    "status_code": status_code,
                    "elapsed_time": elapsed_time,
                    "balance_count": len(balances),
                    "details": f"Retrieved {len(balances)} account balances"
                }
            else:
                error_msg = response_data.get("message", "Balance retrieval failed")
                logger.log_test_result("Account Balances", False, f"Status: {status_code}, Error: {error_msg}")
                return {
                    "test_name": "Account Balances",
                    "success": False,
                    "status_code": status_code,
                    "error": error_msg,
                    "details": "Account balance retrieval failed"
                }
        
        except Exception as e:
            logger.log_test_result("Account Balances", False, f"Exception: {str(e)}")
            return {
                "test_name": "Account Balances",
                "success": False,
                "error": str(e),
                "details": "Exception occurred during balance retrieval"
            }
    
    def _test_error_handling(self) -> Dict[str, Any]:
        """Test error handling with invalid requests"""
        logger.log_test_start("Error Handling")
        
        try:
            # Test with invalid payment ID
            status_code, response_data, elapsed_time = self.client.get_payment("invalid_payment_id")
            
            if status_code == 404:
                logger.log_test_result("Error Handling", True, "404 error handled correctly")
                return {
                    "test_name": "Error Handling",
                    "success": True,
                    "status_code": status_code,
                    "elapsed_time": elapsed_time,
                    "details": "404 error handled correctly for invalid payment ID"
                }
            else:
                logger.log_test_result("Error Handling", False, f"Unexpected status: {status_code}")
                return {
                    "test_name": "Error Handling",
                    "success": False,
                    "status_code": status_code,
                    "details": f"Expected 404, got {status_code}"
                }
        
        except Exception as e:
            logger.log_test_result("Error Handling", False, f"Exception: {str(e)}")
            return {
                "test_name": "Error Handling",
                "success": False,
                "error": str(e),
                "details": "Exception occurred during error handling test"
            }
    
    def run_signature_validation_tests(self) -> Dict[str, Any]:
        """Run signature validation tests"""
        logger.logger.info("🔐 Running signature validation tests...")
        
        if not self.client:
            return {
                "skipped": True,
                "reason": "API client not initialized"
            }
        
        return self.client.validate_signature_implementation()
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        logger.logger.info("🚀 Starting comprehensive test suite...")
        self.start_time = time.time()
        
        # Run unit tests
        unit_test_results = self.run_unit_tests()
        
        # Run integration tests
        integration_test_results = self.run_integration_tests()
        
        # Run signature validation tests
        signature_test_results = self.run_signature_validation_tests()
        
        # Calculate overall results
        total_elapsed = time.time() - self.start_time
        
        overall_results = {
            "test_suite_version": "1.0.0",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_elapsed_time": total_elapsed,
            "api_endpoint": self.base_url,
            "credentials_provided": bool(self.api_key and self.api_secret),
            "unit_tests": unit_test_results,
            "integration_tests": integration_test_results,
            "signature_tests": signature_test_results,
            "overall_success": self._calculate_overall_success(
                unit_test_results, integration_test_results, signature_test_results
            )
        }
        
        # Log summary
        self._log_test_summary(overall_results)
        
        return overall_results
    
    def _calculate_overall_success(self, unit_results: Dict, integration_results: Dict, signature_results: Dict) -> bool:
        """Calculate overall test success"""
        unit_success = unit_results.get("success", False)
        
        if integration_results.get("skipped"):
            integration_success = True  # Skip integration tests if no credentials
        else:
            integration_success = integration_results.get("successful", 0) > 0
        
        if signature_results.get("skipped"):
            signature_success = True  # Skip signature tests if no credentials
        else:
            signature_success = signature_results.get("failed", 1) == 0
        
        return unit_success and integration_success and signature_success
    
    def _log_test_summary(self, results: Dict[str, Any]):
        """Log test summary"""
        logger.logger.info("="*60)
        logger.logger.info("🎯 TEST SUITE SUMMARY")
        logger.logger.info("="*60)
        
        # Overall status
        if results["overall_success"]:
            logger.logger.info("✅ Overall Status: PASSED")
        else:
            logger.logger.error("❌ Overall Status: FAILED")
        
        # Unit tests
        unit_results = results["unit_tests"]
        logger.logger.info(f"🧪 Unit Tests: {unit_results['total_tests']} total, "
                          f"{unit_results['failures']} failures, {unit_results['errors']} errors")
        
        # Integration tests
        integration_results = results["integration_tests"]
        if integration_results.get("skipped"):
            logger.logger.info("🔗 Integration Tests: SKIPPED (no credentials)")
        else:
            logger.logger.info(f"🔗 Integration Tests: {integration_results['successful']}/{integration_results['total_tests']} passed "
                              f"({integration_results['success_rate']:.1f}%)")
        
        # Signature tests
        signature_results = results["signature_tests"]
        if signature_results.get("skipped"):
            logger.logger.info("🔐 Signature Tests: SKIPPED (no credentials)")
        else:
            logger.logger.info(f"🔐 Signature Tests: {signature_results['passed']}/{signature_results['total_tests']} passed")
        
        logger.logger.info(f"⏱️  Total Elapsed Time: {results['total_elapsed_time']:.2f} seconds")
        logger.logger.info("="*60)

def main():
    """Main function to run the test suite"""
    print("🚀 Ebioro Merchant API Test Suite")
    print("="*50)
    
    # Initialize test suite
    test_suite = ComprehensiveTestSuite()
    
    # Run comprehensive tests
    results = test_suite.run_comprehensive_test()
    
    # Export results to JSON file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Test results saved to: test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if results["overall_success"] else 1)

if __name__ == "__main__":
    main()
