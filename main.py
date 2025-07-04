#!/usr/bin/env python3
"""
Ebioro Merchant API Testing Suite
Main entry point for testing the API integration
"""

import sys
import json
import argparse
from typing import Dict, Any, Optional
from config import config
from test_suite import ComprehensiveTestSuite
from logger_config import logger
from clients.python.ebioro_client import EbioroApiClient
from utils import TestDataGenerator, format_json_response

def create_argument_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Ebioro Merchant API Testing Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --test-all                    # Run all tests
  python main.py --test-auth                   # Test authentication only
  python main.py --test-payment               # Test payment creation
  python main.py --create-payment 1000        # Create a test payment
  python main.py --get-payment pay_123        # Get specific payment
  python main.py --list-payments              # List all payments
  python main.py --get-balances               # Get account balances
  python main.py --web                        # Start web interface
  python main.py --validate-signature         # Validate signature implementation
        """
    )
    
    # Test options
    parser.add_argument("--test-all", action="store_true", help="Run comprehensive test suite")
    parser.add_argument("--test-auth", action="store_true", help="Test authentication only")
    parser.add_argument("--test-payment", action="store_true", help="Test payment creation")
    parser.add_argument("--validate-signature", action="store_true", help="Validate signature implementation")
    
    # API operations
    parser.add_argument("--create-payment", type=int, metavar="AMOUNT", help="Create a test payment with specified amount")
    parser.add_argument("--get-payment", type=str, metavar="PAYMENT_ID", help="Get specific payment by ID")
    parser.add_argument("--list-payments", action="store_true", help="List all payments")
    parser.add_argument("--get-balances", action="store_true", help="Get account balances")
    parser.add_argument("--get-refunds", action="store_true", help="Get all refunds")
    
    # Configuration options
    parser.add_argument("--api-key", type=str, help="API key (or set EBIORO_API_KEY env var)")
    parser.add_argument("--api-secret", type=str, help="API secret (or set EBIORO_API_SECRET env var)")
    parser.add_argument("--base-url", type=str, help="Base URL (or set EBIORO_BASE_URL env var)")
    parser.add_argument("--output", type=str, help="Output file for results (JSON format)")
    
    # Web interface
    parser.add_argument("--web", action="store_true", help="Start web interface")
    parser.add_argument("--port", type=int, default=5000, help="Web interface port")
    
    # Logging
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    
    return parser

def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                   Ebioro Merchant API Test Suite             ║
    ║                                                               ║
    ║  A comprehensive testing suite for Ebioro Merchant API        ║
    ║  with HMAC authentication validation                          ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def initialize_client(args) -> Optional[EbioroApiClient]:
    """Initialize API client with provided credentials"""
    api_key = args.api_key or config.API_KEY
    api_secret = args.api_secret or config.API_SECRET_KEY
    base_url = args.base_url or config.BASE_URL
    
    if not api_key or not api_secret:
        logger.logger.error("❌ API credentials not provided!")
        logger.logger.info("Please provide credentials using:")
        logger.logger.info("  • Environment variables: EBIORO_API_KEY, EBIORO_API_SECRET")
        logger.logger.info("  • Command line arguments: --api-key, --api-secret")
        logger.logger.info("  • Or use the web interface: --web")
        return None
    
    try:
        client = EbioroApiClient(api_key, api_secret, base_url)
        logger.logger.info(f"✅ API client initialized for {base_url}")
        return client
    except Exception as e:
        logger.logger.error(f"❌ Failed to initialize API client: {str(e)}")
        return None

def run_comprehensive_tests(args):
    """Run comprehensive test suite"""
    logger.logger.info("🚀 Starting comprehensive test suite...")
    
    test_suite = ComprehensiveTestSuite(
        api_key=args.api_key,
        api_secret=args.api_secret,
        base_url=args.base_url
    )
    
    results = test_suite.run_comprehensive_test()
    
    # Save results if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        logger.logger.info(f"📁 Results saved to: {args.output}")
    
    return results

def run_authentication_test(client: EbioroApiClient):
    """Run authentication test"""
    logger.logger.info("🔐 Testing authentication...")
    
    auth_result = client.test_authentication()
    
    if auth_result["success"]:
        logger.logger.info("✅ Authentication successful!")
        print(f"Status Code: {auth_result['status_code']}")
        print(f"Response Time: {auth_result['elapsed_time']:.2f}s")
    else:
        logger.logger.error("❌ Authentication failed!")
        print(f"Status Code: {auth_result['status_code']}")
        print(f"Error: {auth_result.get('response', {}).get('message', 'Unknown error')}")
    
    return auth_result

def run_payment_test(client: EbioroApiClient):
    """Run payment creation test"""
    logger.logger.info("💳 Testing payment creation...")
    
    payment_data = TestDataGenerator.generate_payment_payload()
    status_code, response_data, elapsed_time = client.create_payment(payment_data)
    
    print(f"Status Code: {status_code}")
    print(f"Response Time: {elapsed_time:.2f}s")
    print(f"Response: {format_json_response(response_data)}")
    
    if status_code in [200, 201]:
        logger.logger.info("✅ Payment creation successful!")
        return response_data.get("id")
    else:
        logger.logger.error("❌ Payment creation failed!")
        return None

def create_payment(client: EbioroApiClient, amount: int):
    """Create a payment with specified amount"""
    logger.logger.info(f"💳 Creating payment for ${amount/100:.2f}...")
    
    payment_data = TestDataGenerator.generate_payment_payload(amount)
    status_code, response_data, elapsed_time = client.create_payment(payment_data)
    
    print(f"Status Code: {status_code}")
    print(f"Response Time: {elapsed_time:.2f}s")
    print(f"Response: {format_json_response(response_data)}")
    
    if status_code in [200, 201]:
        logger.logger.info(f"✅ Payment created: {response_data.get('id')}")
    else:
        logger.logger.error("❌ Payment creation failed!")

def get_payment(client: EbioroApiClient, payment_id: str):
    """Get specific payment by ID"""
    logger.logger.info(f"🔍 Retrieving payment: {payment_id}")
    
    status_code, response_data, elapsed_time = client.get_payment(payment_id)
    
    print(f"Status Code: {status_code}")
    print(f"Response Time: {elapsed_time:.2f}s")
    print(f"Response: {format_json_response(response_data)}")
    
    if status_code == 200:
        logger.logger.info("✅ Payment retrieved successfully!")
    else:
        logger.logger.error("❌ Payment retrieval failed!")

def list_payments(client: EbioroApiClient):
    """List all payments"""
    logger.logger.info("📋 Listing all payments...")
    
    status_code, response_data, elapsed_time = client.get_all_payments()
    
    print(f"Status Code: {status_code}")
    print(f"Response Time: {elapsed_time:.2f}s")
    print(f"Response: {format_json_response(response_data)}")
    
    if status_code == 200:
        payments = response_data.get("payments", [])
        total = response_data.get("total", len(payments))
        logger.logger.info(f"✅ Retrieved {total} payments")
    else:
        logger.logger.error("❌ Payment listing failed!")

def get_balances(client: EbioroApiClient):
    """Get account balances"""
    logger.logger.info("💰 Retrieving account balances...")
    
    status_code, response_data, elapsed_time = client.get_account_balances()
    
    print(f"Status Code: {status_code}")
    print(f"Response Time: {elapsed_time:.2f}s")
    print(f"Response: {format_json_response(response_data)}")
    
    if status_code == 200:
        balances = response_data.get("balances", [])
        logger.logger.info(f"✅ Retrieved {len(balances)} account balances")
    else:
        logger.logger.error("❌ Balance retrieval failed!")

def get_refunds(client: EbioroApiClient):
    """Get all refunds"""
    logger.logger.info("💸 Retrieving all refunds...")
    
    status_code, response_data, elapsed_time = client.get_refunds()
    
    print(f"Status Code: {status_code}")
    print(f"Response Time: {elapsed_time:.2f}s")
    print(f"Response: {format_json_response(response_data)}")
    
    if status_code == 200:
        logger.logger.info("✅ Refunds retrieved successfully!")
    else:
        logger.logger.error("❌ Refund retrieval failed!")

def validate_signature(client: EbioroApiClient):
    """Validate signature implementation"""
    logger.logger.info("🔐 Validating signature implementation...")
    
    validation_result = client.validate_signature_implementation()
    
    print(f"Total Tests: {validation_result['total_tests']}")
    print(f"Passed: {validation_result['passed']}")
    print(f"Failed: {validation_result['failed']}")
    
    for result in validation_result['results']:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['description']}")
        
        if not result['success']:
            print(f"   Error: {result.get('error', 'Unknown error')}")

def start_web_interface(args):
    """Start web interface"""
    from web_interface import app
    
    logger.logger.info(f"🌐 Starting web interface on http://{config.WEB_HOST}:{args.port}")
    
    try:
        app.run(host=config.WEB_HOST, port=args.port, debug=False)
    except Exception as e:
        logger.logger.error(f"❌ Failed to start web interface: {str(e)}")
        sys.exit(1)

def main():
    """Main function"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Handle quiet mode
    if args.quiet:
        logger.logger.setLevel("ERROR")
    elif args.verbose:
        logger.logger.setLevel("DEBUG")
    
    # Print banner unless quiet
    if not args.quiet:
        print_banner()
    
    # Handle web interface
    if args.web:
        start_web_interface(args)
        return
    
    # Handle comprehensive tests
    if args.test_all:
        results = run_comprehensive_tests(args)
        sys.exit(0 if results["overall_success"] else 1)
    
    # For other operations, initialize client
    client = initialize_client(args)
    if not client:
        sys.exit(1)
    
    # Handle specific test operations
    if args.test_auth:
        run_authentication_test(client)
    elif args.test_payment:
        run_payment_test(client)
    elif args.validate_signature:
        validate_signature(client)
    elif args.create_payment:
        create_payment(client, args.create_payment)
    elif args.get_payment:
        get_payment(client, args.get_payment)
    elif args.list_payments:
        list_payments(client)
    elif args.get_balances:
        get_balances(client)
    elif args.get_refunds:
        get_refunds(client)
    else:
        # No specific operation specified, show help
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
