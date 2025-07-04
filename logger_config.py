import logging
import sys
from datetime import datetime
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Add color to levelname
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)

class ApiLogger:
    """Specialized logger for API testing"""
    
    def __init__(self, name: str = "ebioro_api", level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level))
        
        # Custom formatter
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for detailed logs
        file_handler = logging.FileHandler('ebioro_api_tests.log')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def log_request(self, method: str, url: str, headers: dict, body: Optional[str] = None):
        """Log API request details"""
        self.logger.info(f"🔄 {method} {url}")
        self.logger.debug(f"Headers: {headers}")
        if body:
            self.logger.debug(f"Body: {body}")
    
    def log_response(self, status_code: int, response_body: str, elapsed_time: float):
        """Log API response details"""
        if status_code < 400:
            self.logger.info(f"✅ Response {status_code} ({elapsed_time:.2f}s)")
        else:
            self.logger.error(f"❌ Response {status_code} ({elapsed_time:.2f}s)")
        
        self.logger.debug(f"Response body: {response_body}")
    
    def log_signature_debug(self, payload_string: str, signature: str, timestamp: str):
        """Log signature generation details for debugging"""
        self.logger.debug(f"Signature payload: {payload_string}")
        self.logger.debug(f"Generated signature: {signature}")
        self.logger.debug(f"Timestamp: {timestamp}")
    
    def log_test_start(self, test_name: str):
        """Log test start"""
        self.logger.info(f"🧪 Starting test: {test_name}")
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        if success:
            self.logger.info(f"✅ Test passed: {test_name}")
        else:
            self.logger.error(f"❌ Test failed: {test_name}")
        
        if details:
            self.logger.info(f"Details: {details}")
    
    def log_validation_error(self, field: str, expected: str, actual: str):
        """Log validation errors"""
        self.logger.error(f"Validation failed for {field}: expected '{expected}', got '{actual}'")

# Global logger instance
logger = ApiLogger()
