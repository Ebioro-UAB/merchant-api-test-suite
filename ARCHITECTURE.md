# Ebioro API Test Suite

## Overview
This is a comprehensive multi-language testing suite for the Ebioro Merchant API with HMAC-SHA256 authentication. The project provides production-ready API client implementations in Python, Java, PHP, Node.js, and C#, along with a web-based testing interface and extensive test coverage.

## System Architecture

### Frontend Architecture
- **Web Interface**: Flask-based web application with Bootstrap UI
- **Static Assets**: Custom CSS styling and JavaScript functionality
- **Templates**: HTML templates for test results and main interface
- **Interactive Features**: Real-time API testing, credential validation, and result export

### Backend Architecture
- **Main Application**: Python-based CLI and web interface (`main.py`)
- **Multi-Language Router**: Subprocess-based execution of different language implementations
- **API Clients**: Individual client implementations for each supported language
- **Test Framework**: Comprehensive test suite with unit tests and integration tests

### Configuration Management
- **Environment Variables**: API credentials, base URLs, and runtime configuration
- **Config Module**: Centralized configuration handling with validation
- **Logging**: Structured logging with colored output and file persistence

## Key Components

### Core API Client (Python)
- **Location**: `clients/python/ebioro_client.py`
- **Features**: HMAC-SHA256 authentication, comprehensive error handling, request/response logging
- **Authentication**: Uses `path + timestamp + method + body` format for signature generation

### Multi-Language Support
- **Python**: Primary implementation using requests library
- **Java**: HttpClient-based implementation with Jackson for JSON
- **PHP**: cURL-based implementation with object-oriented design
- **Node.js**: Native https module implementation with Promise-based API
- **C#**: HttpClient implementation with async/await patterns

### Web Interface
- **Flask Application**: `web_interface.py` provides REST API endpoints
- **Bootstrap UI**: Responsive design with sidebar navigation
- **Real-time Testing**: AJAX-based API calls with live result display
- **Language Selection**: Dropdown interface for choosing implementation language

### Test Suite
- **Unit Tests**: Authentication and endpoint validation
- **Integration Tests**: Full API workflow testing
- **Signature Validation**: HMAC implementation verification
- **Performance Testing**: Response time measurement and analysis

## Data Flow

### Authentication Flow
1. Generate Unix timestamp
2. Create payload string: `path + timestamp + method + body`
3. Generate HMAC-SHA256 signature using API secret
4. Include headers: `X-Digest-Key`, `X-Digest-Timestamp`, `X-Digest-Signature`

### API Request Flow
1. User selects programming language and enters credentials
2. Multi-language router validates language support
3. Request is executed using selected language implementation
4. Response is parsed and formatted for display
5. Results are stored and can be exported

### Test Execution Flow
1. Initialize API client with credentials
2. Run authentication tests
3. Execute endpoint tests (payments, refunds, balances)
4. Validate responses and measure performance
5. Generate comprehensive test report

## External Dependencies

### Python Dependencies
- `requests`: HTTP client library
- `flask`: Web framework
- `configparser`: Configuration management
- `hmac`, `hashlib`: Cryptographic functions

### Language-Specific Dependencies
- **Java**: Jackson for JSON processing
- **PHP**: cURL extension
- **Node.js**: Built-in modules only (crypto, https, http)
- **C#**: System.Text.Json for JSON handling

### Third-Party Services
- **Ebioro API**: Primary integration target
- **Bootstrap**: Frontend CSS framework
- **Font Awesome**: Icon library

## Deployment Strategy

### Local Development
- Run `python main.py --web --port 5000` for web interface
- Use `python main.py --test-all` for comprehensive testing
- Environment variables for API credentials

### Production Considerations
- Environment variable configuration for sensitive data
- Logging configuration for production monitoring
- Error handling for network failures and API changes
- Rate limiting considerations for API calls

### Multi-Environment Support
- Configurable base URLs for test/production environments
- Environment-specific credential management
- Deployment scripts for different platforms

## Changelog
- July 04, 2025. Initial setup

## User Preferences
Preferred communication style: Simple, everyday language.