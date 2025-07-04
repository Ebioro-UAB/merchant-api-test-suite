import os
import configparser
from typing import Dict, Any

class Config:
    """Configuration management for Ebioro API testing"""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load configuration from environment variables and config file"""
        # API Configuration
        self.API_KEY = os.getenv("EBIORO_API_KEY", "")
        self.API_SECRET_KEY = os.getenv("EBIORO_API_SECRET", "")
        self.BASE_URL = os.getenv("EBIORO_BASE_URL", "https://test-merchant.ebioro.com")
        
        # Test Configuration
        self.TEST_MODE = os.getenv("TEST_MODE", "development").lower()
        self.VERBOSE_LOGGING = os.getenv("VERBOSE_LOGGING", "true").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Web Interface Configuration
        self.WEB_PORT = int(os.getenv("WEB_PORT", "5000"))
        self.WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
        
        # Validation
        self.validate_config()
    
    def validate_config(self):
        """Validate required configuration parameters"""
        required_configs = {
            "API_KEY": self.API_KEY,
            "API_SECRET_KEY": self.API_SECRET_KEY,
            "BASE_URL": self.BASE_URL
        }
        
        missing_configs = [key for key, value in required_configs.items() if not value]
        
        if missing_configs:
            print(f"⚠️  Warning: Missing configuration for: {', '.join(missing_configs)}")
            print("   Please set the following environment variables:")
            for config in missing_configs:
                print(f"   - {config}")
            print("   Or provide them through the web interface when testing.")
    
    def get_api_config(self) -> Dict[str, str]:
        """Get API configuration as dictionary"""
        return {
            "api_key": self.API_KEY,
            "api_secret": self.API_SECRET_KEY,
            "base_url": self.BASE_URL
        }
    
    def is_configured(self) -> bool:
        """Check if API is properly configured"""
        return bool(self.API_KEY and self.API_SECRET_KEY and self.BASE_URL)
    
    def get_test_config(self) -> Dict[str, Any]:
        """Get test configuration"""
        return {
            "test_mode": self.TEST_MODE,
            "verbose_logging": self.VERBOSE_LOGGING,
            "log_level": self.LOG_LEVEL
        }
    
    def get_web_config(self) -> Dict[str, Any]:
        """Get web interface configuration"""
        return {
            "port": self.WEB_PORT,
            "host": self.WEB_HOST
        }

# Global configuration instance
config = Config()
