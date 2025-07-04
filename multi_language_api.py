"""
Multi-Language API Router for Ebioro API Test Suite

This module provides a unified interface to test API clients in different languages
through subprocess calls. It acts as a bridge between the web interface and
various language implementations.
"""

import json
import subprocess
import os
import tempfile
from typing import Dict, Any, Optional, Tuple
from logger_config import ApiLogger

class MultiLanguageApiRouter:
    """Router that can execute API calls in different programming languages"""
    
    def __init__(self):
        self.logger = ApiLogger("multi_language_router")
        self.supported_languages = {
            'python': {
                'name': 'Python',
                'description': 'Python implementation using requests library',
                'executor': self._execute_python
            },
            'java': {
                'name': 'Java',
                'description': 'Java implementation using HttpClient',
                'executor': self._execute_java
            },
            'php': {
                'name': 'PHP',
                'description': 'PHP implementation using cURL',
                'executor': self._execute_php
            },
            'nodejs': {
                'name': 'Node.js',
                'description': 'Node.js implementation using native https module',
                'executor': self._execute_nodejs
            },
            'csharp': {
                'name': 'C#',
                'description': 'C# implementation using HttpClient',
                'executor': self._execute_csharp
            }
        }
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Get list of supported languages"""
        return {
            lang: {
                'name': config['name'],
                'description': config['description']
            }
            for lang, config in self.supported_languages.items()
        }
    
    def execute_api_call(self, language: str, operation: str, api_key: str, 
                        api_secret: str, **kwargs) -> Dict[str, Any]:
        """Execute an API call in the specified language"""
        
        if language not in self.supported_languages:
            return {
                'success': False,
                'error': f'Unsupported language: {language}',
                'status_code': 400
            }
        
        try:
            executor = self.supported_languages[language]['executor']
            return executor(operation, api_key, api_secret, **kwargs)
        except Exception as e:
            self.logger.error(f"Error executing {language} API call: {str(e)}")
            return {
                'success': False,
                'error': f'Execution error: {str(e)}',
                'status_code': 500
            }
    
    def _execute_python(self, operation: str, api_key: str, api_secret: str, **kwargs) -> Dict[str, Any]:
        """Execute Python API call using the existing client"""
        from clients.python.ebioro_client import EbioroApiClient
        
        try:
            client = EbioroApiClient(api_key, api_secret)
            
            if operation == 'test_auth':
                result = client.test_authentication()
                return {
                    'success': result['success'],
                    'status_code': result['status_code'],
                    'response': result['response'],
                    'elapsed_time': result['elapsed_time'],
                    'language': 'python'
                }
            
            elif operation == 'create_payment':
                payment_data = kwargs.get('payment_data', {})
                status_code, response_data, elapsed_time = client.create_payment(payment_data)
                return {
                    'success': status_code == 200,
                    'status_code': status_code,
                    'response': response_data,
                    'elapsed_time': elapsed_time,
                    'language': 'python'
                }
            
            elif operation == 'get_payment':
                payment_id = kwargs.get('payment_id', '')
                status_code, response_data, elapsed_time = client.get_payment(payment_id)
                return {
                    'success': status_code == 200,
                    'status_code': status_code,
                    'response': response_data,
                    'elapsed_time': elapsed_time,
                    'language': 'python'
                }
            
            elif operation == 'list_payments':
                status_code, response_data, elapsed_time = client.get_all_payments()
                return {
                    'success': status_code == 200,
                    'status_code': status_code,
                    'response': response_data,
                    'elapsed_time': elapsed_time,
                    'language': 'python'
                }
            
            elif operation == 'get_balances':
                status_code, response_data, elapsed_time = client.get_account_balances()
                return {
                    'success': status_code == 200,
                    'status_code': status_code,
                    'response': response_data,
                    'elapsed_time': elapsed_time,
                    'language': 'python'
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported operation: {operation}',
                    'status_code': 400,
                    'language': 'python'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': 500,
                'language': 'python'
            }
    
    def _execute_java(self, operation: str, api_key: str, api_secret: str, **kwargs) -> Dict[str, Any]:
        """Execute Java API call via subprocess"""
        # For now, return a simulated response since we don't have Java runtime
        return {
            'success': False,
            'error': 'Java runtime not available in this environment',
            'status_code': 503,
            'language': 'java',
            'note': 'This would execute the Java client if Java runtime was available'
        }
    
    def _execute_php(self, operation: str, api_key: str, api_secret: str, **kwargs) -> Dict[str, Any]:
        """Execute PHP API call via subprocess"""
        try:
            # Create a temporary PHP script
            php_code = self._generate_php_script(operation, api_key, api_secret, **kwargs)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
                f.write(php_code)
                temp_file = f.name
            
            try:
                # Execute PHP script
                result = subprocess.run(
                    ['php', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    try:
                        response_data = json.loads(result.stdout)
                        response_data['language'] = 'php'
                        return response_data
                    except json.JSONDecodeError:
                        return {
                            'success': False,
                            'error': 'Invalid JSON response from PHP script',
                            'status_code': 500,
                            'language': 'php',
                            'raw_output': result.stdout
                        }
                else:
                    return {
                        'success': False,
                        'error': f'PHP script failed: {result.stderr}',
                        'status_code': 500,
                        'language': 'php'
                    }
                    
            finally:
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'PHP execution timeout',
                'status_code': 504,
                'language': 'php'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'PHP runtime not available in this environment',
                'status_code': 503,
                'language': 'php'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': 500,
                'language': 'php'
            }
    
    def _execute_nodejs(self, operation: str, api_key: str, api_secret: str, **kwargs) -> Dict[str, Any]:
        """Execute Node.js API call via subprocess"""
        try:
            # Create a temporary Node.js script
            js_code = self._generate_nodejs_script(operation, api_key, api_secret, **kwargs)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(js_code)
                temp_file = f.name
            
            try:
                # Execute Node.js script
                result = subprocess.run(
                    ['node', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    try:
                        response_data = json.loads(result.stdout)
                        response_data['language'] = 'nodejs'
                        return response_data
                    except json.JSONDecodeError:
                        return {
                            'success': False,
                            'error': 'Invalid JSON response from Node.js script',
                            'status_code': 500,
                            'language': 'nodejs',
                            'raw_output': result.stdout
                        }
                else:
                    return {
                        'success': False,
                        'error': f'Node.js script failed: {result.stderr}',
                        'status_code': 500,
                        'language': 'nodejs'
                    }
                    
            finally:
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Node.js execution timeout',
                'status_code': 504,
                'language': 'nodejs'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'Node.js runtime not available in this environment',
                'status_code': 503,
                'language': 'nodejs'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': 500,
                'language': 'nodejs'
            }
    
    def _execute_csharp(self, operation: str, api_key: str, api_secret: str, **kwargs) -> Dict[str, Any]:
        """Execute C# API call via subprocess"""
        # For now, return a simulated response since we don't have .NET runtime
        return {
            'success': False,
            'error': '.NET runtime not available in this environment',
            'status_code': 503,
            'language': 'csharp',
            'note': 'This would execute the C# client if .NET runtime was available'
        }
    
    def _generate_php_script(self, operation: str, api_key: str, api_secret: str, **kwargs) -> str:
        """Generate PHP script for API call"""
        
        # Include the client code
        php_client_path = os.path.join(os.path.dirname(__file__), 'clients', 'php', 'EbioroApiClient.php')
        
        script = f"""<?php
require_once '{php_client_path}';

try {{
    $client = new EbioroApiClient('{api_key}', '{api_secret}');
    
"""
        
        if operation == 'test_auth':
            script += """
    $response = $client->testAuthentication();
    echo json_encode($response->toArray());
"""
        elif operation == 'create_payment':
            payment_data = kwargs.get('payment_data', {})
            payment_json = json.dumps(payment_data)
            script += f"""
    $paymentData = json_decode('{payment_json}', true);
    $response = $client->createPayment($paymentData);
    echo json_encode($response->toArray());
"""
        elif operation == 'list_payments':
            script += """
    $response = $client->getAllPayments();
    echo json_encode($response->toArray());
"""
        elif operation == 'get_balances':
            script += """
    $response = $client->getAccountBalances();
    echo json_encode($response->toArray());
"""
        
        script += """
} catch (Exception $e) {
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage(),
        'status_code' => 500
    ]);
}
?>"""
        
        return script
    
    def _generate_nodejs_script(self, operation: str, api_key: str, api_secret: str, **kwargs) -> str:
        """Generate Node.js script for API call"""
        
        # Include the client code
        js_client_path = os.path.join(os.path.dirname(__file__), 'clients', 'nodejs', 'ebioro-client.js')
        
        script = f"""
const {{ EbioroApiClient }} = require('{js_client_path}');

async function executeApiCall() {{
    try {{
        const client = new EbioroApiClient('{api_key}', '{api_secret}');
        
"""
        
        if operation == 'test_auth':
            script += """
        const response = await client.testAuthentication();
        console.log(JSON.stringify(response.toObject()));
"""
        elif operation == 'create_payment':
            payment_data = kwargs.get('payment_data', {})
            payment_json = json.dumps(payment_data)
            script += f"""
        const paymentData = {payment_json};
        const response = await client.createPayment(paymentData);
        console.log(JSON.stringify(response.toObject()));
"""
        elif operation == 'list_payments':
            script += """
        const response = await client.getAllPayments();
        console.log(JSON.stringify(response.toObject()));
"""
        elif operation == 'get_balances':
            script += """
        const response = await client.getAccountBalances();
        console.log(JSON.stringify(response.toObject()));
"""
        
        script += """
    } catch (error) {
        console.log(JSON.stringify({
            success: false,
            error: error.message,
            status_code: 500
        }));
    }
}

executeApiCall();
"""
        
        return script