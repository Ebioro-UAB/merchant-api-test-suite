import os
import json
import time
from flask import Flask, render_template, request, jsonify, session
from config import config
from clients.python.ebioro_client import EbioroApiClient
from test_suite import ComprehensiveTestSuite
from utils import TestDataGenerator, format_json_response
from logger_config import logger
from multi_language_api import MultiLanguageApiRouter

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global variables to store test results
test_results = {}
api_client = None
multi_language_router = MultiLanguageApiRouter()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', config=config.get_api_config())

@app.route('/api/supported-languages')
def supported_languages():
    """Get supported programming languages"""
    return jsonify({
        'success': True,
        'languages': multi_language_router.get_supported_languages()
    })

@app.route('/api/test-credentials', methods=['POST'])
def test_credentials():
    """Test API credentials"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        api_secret = data.get('api_secret', '').strip()
        base_url = data.get('base_url', config.BASE_URL).strip()
        language = data.get('language', 'python').strip()
        
        if not api_key or not api_secret:
            return jsonify({
                'success': False,
                'error': 'API key and secret are required'
            })
        
        # Test authentication using selected language
        result = multi_language_router.execute_api_call(
            language=language,
            operation='test_auth',
            api_key=api_key,
            api_secret=api_secret
        )
        
        if result['success']:
            # Store credentials in session
            session['api_key'] = api_key
            session['api_secret'] = api_secret
            session['base_url'] = base_url
            session['language'] = language
            
            # Also initialize Python client for legacy support
            if language == 'python':
                global api_client
                api_client = EbioroApiClient(api_key, api_secret, base_url)
            
            return jsonify({
                'success': True,
                'status_code': result.get('status_code', 200),
                'elapsed_time': result.get('elapsed_time', 0),
                'language': language,
                'message': f'Credentials validated successfully using {language.capitalize()}'
            })
        else:
            return jsonify({
                'success': False,
                'status_code': result.get('status_code', 500),
                'language': language,
                'error': result.get('error', 'Authentication failed')
            })
    
    except Exception as e:
        logger.logger.error(f"Error testing credentials: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    """Run comprehensive tests"""
    try:
        if not api_client:
            return jsonify({
                'success': False,
                'error': 'API client not initialized. Please test credentials first.'
            })
        
        test_suite = ComprehensiveTestSuite(
            api_key=session.get('api_key'),
            api_secret=session.get('api_secret'),
            base_url=session.get('base_url')
        )
        
        results = test_suite.run_comprehensive_test()
        
        # Store results globally
        global test_results
        test_results = results
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        logger.logger.error(f"Error running tests: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    """Create a test payment"""
    try:
        if not api_client:
            return jsonify({
                'success': False,
                'error': 'API client not initialized'
            })
        
        data = request.get_json()
        amount = data.get('amount', 1000)
        currency = data.get('currency', 'USD')
        description = data.get('description', 'Test payment from web interface')
        
        payment_data = TestDataGenerator.generate_payment_payload(amount, currency)
        payment_data['description'] = description
        status_code, response_data, elapsed_time = api_client.create_payment(payment_data)
        
        return jsonify({
            'success': status_code in [200, 201],
            'status_code': status_code,
            'elapsed_time': elapsed_time,
            'response': response_data,
            'request_data': payment_data
        })
    
    except Exception as e:
        logger.logger.error(f"Error creating payment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/get-payment/<payment_id>')
def get_payment(payment_id):
    """Get specific payment"""
    try:
        if not api_client:
            return jsonify({
                'success': False,
                'error': 'API client not initialized'
            })
        
        status_code, response_data, elapsed_time = api_client.get_payment(payment_id)
        
        return jsonify({
            'success': status_code == 200,
            'status_code': status_code,
            'elapsed_time': elapsed_time,
            'response': response_data
        })
    
    except Exception as e:
        logger.logger.error(f"Error getting payment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/list-payments')
def list_payments():
    """List all payments"""
    try:
        if not api_client:
            return jsonify({
                'success': False,
                'error': 'API client not initialized'
            })
        
        status_code, response_data, elapsed_time = api_client.get_all_payments()
        
        return jsonify({
            'success': status_code == 200,
            'status_code': status_code,
            'elapsed_time': elapsed_time,
            'response': response_data
        })
    
    except Exception as e:
        logger.logger.error(f"Error listing payments: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/get-balances')
def get_balances():
    """Get account balances"""
    try:
        if not api_client:
            return jsonify({
                'success': False,
                'error': 'API client not initialized'
            })
        
        status_code, response_data, elapsed_time = api_client.get_account_balances()
        
        return jsonify({
            'success': status_code == 200,
            'status_code': status_code,
            'elapsed_time': elapsed_time,
            'response': response_data
        })
    
    except Exception as e:
        logger.logger.error(f"Error getting balances: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/create-refund', methods=['POST'])
def create_refund():
    """Create a refund for a payment"""
    try:
        if not api_client:
            return jsonify({
                'success': False,
                'error': 'API client not initialized'
            })
        
        data = request.get_json()
        payment_id = data.get('payment_id')
        amount = data.get('amount')
        
        if not payment_id:
            return jsonify({
                'success': False,
                'error': 'Payment ID is required'
            })
        
        refund_data = TestDataGenerator.generate_refund_payload(
            amount if amount else 500, 
            "Refund from web interface"
        )
        
        status_code, response_data, elapsed_time = api_client.create_refund(payment_id, refund_data)
        
        return jsonify({
            'success': status_code in [200, 201],
            'status_code': status_code,
            'elapsed_time': elapsed_time,
            'response': response_data,
            'request_data': refund_data
        })
    
    except Exception as e:
        logger.logger.error(f"Error creating refund: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/validate-signature')
def validate_signature():
    """Validate signature implementation"""
    try:
        if not api_client:
            return jsonify({
                'success': False,
                'error': 'API client not initialized'
            })
        
        validation_result = api_client.validate_signature_implementation()
        
        return jsonify({
            'success': validation_result['failed'] == 0,
            'results': validation_result
        })
    
    except Exception as e:
        logger.logger.error(f"Error validating signature: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/get-last-request')
def get_last_request():
    """Get details of last API request"""
    try:
        if not api_client:
            return jsonify({
                'success': False,
                'error': 'API client not initialized'
            })
        
        request_details = api_client.get_last_request_details()
        response_details = api_client.get_last_response_details()
        
        return jsonify({
            'success': True,
            'request': request_details,
            'response': response_details
        })
    
    except Exception as e:
        logger.logger.error(f"Error getting last request: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/export-results')
def export_results():
    """Export test results as JSON"""
    try:
        global test_results
        
        if not test_results:
            return jsonify({
                'success': False,
                'error': 'No test results available'
            })
        
        return jsonify({
            'success': True,
            'results': test_results
        })
    
    except Exception as e:
        logger.logger.error(f"Error exporting results: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/test-results')
def test_results_page():
    """Test results page"""
    return render_template('test_results.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
