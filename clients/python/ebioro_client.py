import time
import json
import hmac
import hashlib
import requests
from typing import Dict, Any, Optional, Tuple
from urllib.parse import quote, urlencode
from logger_config import logger
from utils import ValidationError, SignatureValidator, ResponseValidator, format_json_response, calculate_elapsed_time

class EbioroApiClient:
    """Enhanced Ebioro API client with comprehensive testing capabilities"""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://test-merchant.ebioro.com"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.last_request_details = {}
        self.last_response_details = {}
        
        # Validate credentials
        if not api_key or not api_secret:
            raise ValidationError("API key and secret are required")
        
        logger.logger.info(f"🔧 Initialized Ebioro API client for {base_url}")
    
    def generate_headers(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate HMAC-SHA256 signed headers for authentication
        
        Based on the official documentation:
        - Payload string format: path + timestamp + method + body
        - HMAC-SHA256 signature using API secret
        """
        # Prepare body data
        data = json.dumps(body, separators=(',', ':')) if body else ""
        timestamp = str(int(time.time()))
        
        # Create payload string per official documentation: path + timestamp + method + body
        payload_string = path + timestamp + method + data
        
        # Generate HMAC signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            payload_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Log signature generation details
        logger.log_signature_debug(payload_string, signature, timestamp)
        
        # Validate signature components
        validation_result = SignatureValidator.validate_signature_components(
            path, timestamp, method, data
        )
        
        if not validation_result["valid"]:
            logger.logger.warning(f"Signature validation warnings: {validation_result['errors']}")
        
        headers = {
            'Content-Type': 'application/json',
            'X-Digest-Key': self.api_key,
            'X-Digest-Signature': signature,
            'X-Digest-Timestamp': timestamp
        }
        
        return headers
    
    def _make_request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any], float]:
        """
        Make authenticated API request with comprehensive logging
        
        Returns:
            Tuple of (status_code, response_data, elapsed_time)
        """
        url = f"{self.base_url}{path}"
        headers = self.generate_headers(method, path, body)

        # Store request details. Auth headers are NOT stored: the snapshot is
        # surfaced by debugging endpoints (web UI /api/get-last-request) and
        # must never reflect the API key or a valid signature back to a caller.
        self.last_request_details = {
            "method": method,
            "url": url,
            "headers": self._redact_auth_headers(headers),
            "body": body,
            "timestamp": time.time()
        }

        # Log request (auth headers redacted for the same reason)
        logger.log_request(method, url, self._redact_auth_headers(headers), json.dumps(body) if body else None)
        
        start_time = time.time()
        
        try:
            # Use data parameter for POST requests to match signature calculation
            if method in ['POST', 'PUT', 'PATCH'] and body:
                # Send as string data to match the signed payload
                data = json.dumps(body, separators=(',', ':'))
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    timeout=30
                )
            else:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=30
                )
            
            elapsed_time = calculate_elapsed_time(start_time)
            
            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"raw_response": response.text}
            
            # Store response details
            self.last_response_details = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response_data,
                "elapsed_time": elapsed_time,
                "timestamp": time.time()
            }
            
            # Log response
            logger.log_response(response.status_code, json.dumps(response_data), elapsed_time)
            
            return response.status_code, response_data, elapsed_time
            
        except requests.exceptions.RequestException as e:
            elapsed_time = calculate_elapsed_time(start_time)
            logger.logger.error(f"Request failed: {str(e)}")
            
            error_data = {
                "error": "request_failed",
                "message": str(e),
                "type": type(e).__name__
            }
            
            return 0, error_data, elapsed_time
    
    @staticmethod
    def _path_param(value: str) -> str:
        """URL-encode a path parameter so untrusted ids cannot alter the request path."""
        return quote(str(value), safe='')

    @staticmethod
    def _redact_auth_headers(headers: Dict[str, str]) -> Dict[str, str]:
        """Return a copy of the headers with credential material removed."""
        redacted = dict(headers)
        for sensitive in ("X-Digest-Key", "X-Digest-Signature"):
            if sensitive in redacted:
                redacted[sensitive] = "[REDACTED]"
        return redacted

    def create_payment(self, payment_data: Dict[str, Any]) -> Tuple[int, Dict[str, Any], float]:
        """Create a new payment"""
        logger.logger.info("💳 Creating payment")
        return self._make_request("POST", "/payments", payment_data)

    def create_payment_link(self, payment_data: Dict[str, Any], expires_in_hours: int = 168) -> Tuple[int, Dict[str, Any], float]:
        """
        Create a shareable payment link.

        A payment link is a payment with a longer expiry window. Omit redirectUrl
        for the Ebioro-hosted confirmation screen. The response contains shortUrl —
        the link to share with the payer.
        """
        logger.logger.info("🔗 Creating payment link")
        data = dict(payment_data)
        data.setdefault("expiresInHours", expires_in_hours)
        return self._make_request("POST", "/payments", data)

    def get_payment(self, payment_id: str) -> Tuple[int, Dict[str, Any], float]:
        """Retrieve a specific payment"""
        logger.logger.info(f"🔍 Retrieving payment {payment_id}")
        return self._make_request("GET", f"/payments/{self._path_param(payment_id)}")

    def get_all_payments(self) -> Tuple[int, Dict[str, Any], float]:
        """Retrieve all payments"""
        logger.logger.info("📋 Retrieving all payments")
        return self._make_request("GET", "/payments")

    def create_refund(self, payment_id: str, refund_data: Dict[str, Any]) -> Tuple[int, Dict[str, Any], float]:
        """Create a refund for a payment"""
        logger.logger.info(f"💸 Creating refund for payment {payment_id}")
        return self._make_request("POST", f"/payments/{self._path_param(payment_id)}/refunds", refund_data)

    def get_refunds(self) -> Tuple[int, Dict[str, Any], float]:
        """Retrieve all refunds"""
        logger.logger.info("📋 Retrieving all refunds")
        return self._make_request("GET", "/refunds")

    def get_refund(self, refund_id: str) -> Tuple[int, Dict[str, Any], float]:
        """Retrieve a specific refund"""
        logger.logger.info(f"🔍 Retrieving refund {refund_id}")
        return self._make_request("GET", f"/refunds/{self._path_param(refund_id)}")

    def get_account_balances(self) -> Tuple[int, Dict[str, Any], float]:
        """Retrieve all account balances"""
        logger.logger.info("💰 Retrieving account balances")
        return self._make_request("GET", "/accounts/balances")

    def get_asset_balance(self, asset: str) -> Tuple[int, Dict[str, Any], float]:
        """Retrieve specific asset balance"""
        logger.logger.info(f"💰 Retrieving {asset} balance")
        return self._make_request("GET", f"/accounts/balances/{self._path_param(asset)}")

    # ------------------------------------------------------------------
    # Invoices
    # ------------------------------------------------------------------

    def create_invoice(self, invoice_data: Dict[str, Any]) -> Tuple[int, Dict[str, Any], float]:
        """
        Create an invoice (line items + optional single tax percentage).

        The response includes payment_id — fetch that payment via get_payment()
        to obtain the shareable payment link (shortUrl) for the customer.
        """
        logger.logger.info("🧾 Creating invoice")
        return self._make_request("POST", "/invoices", invoice_data)

    def get_invoices(self, page: int = 1, limit: int = 20) -> Tuple[int, Dict[str, Any], float]:
        """List invoices (paginated). The query string is part of the signed path."""
        logger.logger.info("📋 Retrieving invoices")
        query = urlencode({"page": int(page), "limit": int(limit)})
        return self._make_request("GET", f"/invoices?{query}")

    def get_invoice(self, invoice_id: str) -> Tuple[int, Dict[str, Any], float]:
        """Retrieve a specific invoice"""
        logger.logger.info(f"🔍 Retrieving invoice {invoice_id}")
        return self._make_request("GET", f"/invoices/{self._path_param(invoice_id)}")

    def cancel_invoice(self, invoice_id: str) -> Tuple[int, Dict[str, Any], float]:
        """Cancel (void) an unpaid invoice and expire its payment link"""
        logger.logger.info(f"🚫 Cancelling invoice {invoice_id}")
        return self._make_request("POST", f"/invoices/{self._path_param(invoice_id)}/cancel")

    def get_invoice_settings(self) -> Tuple[int, Dict[str, Any], float]:
        """Get invoice numbering settings (prefix + next number)"""
        logger.logger.info("⚙️ Retrieving invoice settings")
        return self._make_request("GET", "/invoices/settings")

    def update_invoice_settings(self, settings: Dict[str, Any]) -> Tuple[int, Dict[str, Any], float]:
        """Update invoice numbering settings (invoice_prefix and/or next_number)"""
        logger.logger.info("⚙️ Updating invoice settings")
        return self._make_request("POST", "/invoices/settings", settings)

    # ------------------------------------------------------------------
    # Webhooks
    # ------------------------------------------------------------------

    @staticmethod
    def verify_webhook_signature(raw_body: bytes, signature: str, api_secret: str) -> bool:
        """
        Verify the X-WEBHOOK-AUTH signature of an incoming webhook.

        Always verify before processing a webhook. Pass the RAW request body
        bytes exactly as received — re-serializing the parsed JSON can change
        the bytes and break verification. Uses a constant-time comparison.
        """
        if not signature or not api_secret:
            return False
        if isinstance(raw_body, str):
            raw_body = raw_body.encode("utf-8")
        if not isinstance(raw_body, bytes):
            raise TypeError("raw_body must be the raw request body (bytes or str), not a parsed object")
        if isinstance(signature, bytes):
            signature = signature.decode("utf-8")
        expected = hmac.new(api_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    def test_authentication(self) -> Dict[str, Any]:
        """Test authentication by making a simple request"""
        logger.logger.info("🔐 Testing authentication")
        
        status_code, response_data, elapsed_time = self.get_all_payments()
        
        auth_result = {
            "success": status_code != 401 and status_code != 403,
            "status_code": status_code,
            "response": response_data,
            "elapsed_time": elapsed_time
        }
        
        if auth_result["success"]:
            logger.logger.info("✅ Authentication successful")
        else:
            logger.logger.error("❌ Authentication failed")
            
        return auth_result
    
    def validate_signature_implementation(self, test_cases: list = None) -> Dict[str, Any]:
        """Validate HMAC signature implementation against test cases"""
        if test_cases is None:
            test_cases = [
                {
                    "method": "GET",
                    "path": "/payments",
                    "body": None,
                    "description": "Simple GET request"
                },
                {
                    "method": "POST",
                    "path": "/payments",
                    "body": {"amount": {"currency": "USD", "value": 100}},
                    "description": "POST request with JSON body"
                }
            ]
        
        results = []
        
        for test_case in test_cases:
            logger.logger.info(f"🧪 Testing signature for: {test_case['description']}")
            
            try:
                headers = self.generate_headers(
                    test_case["method"],
                    test_case["path"],
                    test_case["body"]
                )
                
                # Only confirm that signing succeeded. Never return the headers,
                # the API key, or the signature itself — this result is surfaced
                # verbatim by the web UI's /api/validate-signature endpoint.
                result = {
                    "description": test_case["description"],
                    "success": True,
                    "timestamp": headers["X-Digest-Timestamp"]
                }
                
                logger.logger.info("✅ Signature generated successfully")
                
            except Exception as e:
                result = {
                    "description": test_case["description"],
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                
                logger.logger.error(f"❌ Signature generation failed: {str(e)}")
            
            results.append(result)
        
        return {
            "total_tests": len(test_cases),
            "passed": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results
        }
    
    def get_last_request_details(self) -> Dict[str, Any]:
        """Get details of the last API request"""
        return self.last_request_details
    
    def get_last_response_details(self) -> Dict[str, Any]:
        """Get details of the last API response"""
        return self.last_response_details
