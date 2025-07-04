# Contributing to Ebioro API Test Suite

Thank you for your interest in contributing to the Ebioro API Test Suite! This document provides guidelines for contributing to this multi-language API client project.

## 🚀 Getting Started

### Prerequisites
- Python 3.7+ (for the test suite)
- Your preferred language runtime for client development
- Ebioro API credentials for testing

### Local Development Setup
1. Clone the repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Set up environment variables for testing (optional)
4. Run the test suite: `python main.py --test`

## 🌐 Adding New Language Clients

We welcome implementations in additional programming languages! Follow these guidelines:

### Implementation Requirements
1. **Authentication**: Use identical HMAC-SHA256 signature generation
   - Payload format: `path + timestamp + method + body`
   - Hex encoding (not base64)
   - Headers: `X-Digest-Key`, `X-Digest-Timestamp`, `X-Digest-Signature`

2. **API Coverage**: Implement core functionality
   - Payment creation and retrieval
   - Payment listing and search
   - Refund operations
   - Account balance queries
   - Authentication testing

3. **Error Handling**: Include comprehensive error management
   - HTTP status code validation
   - Network timeout handling
   - JSON parsing errors
   - Detailed error messages

### File Structure
```
clients/
└── {language}/
    ├── README.md              # Language-specific documentation
    ├── {ClientFile}           # Main client implementation
    └── example.{ext}          # Usage example
```

### Code Standards
- **Self-contained**: Minimal external dependencies
- **Production-ready**: Include proper error handling and logging
- **Documented**: Clear usage examples and API documentation
- **Tested**: Verify against live API endpoints

## 🧪 Testing

### Test Types
1. **Unit Tests**: Authentication and core functionality
2. **Integration Tests**: Real API interactions
3. **Multi-language Tests**: Cross-language signature verification

### Testing Guidelines
- Test with actual API credentials (safely stored)
- Verify HMAC signature consistency across languages
- Include both success and error scenarios
- Document any language-specific considerations

## 📝 Documentation

### Required Documentation
- Update `clients/README.md` with new language entry
- Include usage examples in the main README
- Add language-specific notes if applicable
- Update the multi-language test documentation

### Documentation Standards
- Clear, concise explanations
- Working code examples
- Installation and dependency instructions
- Security considerations

## 🔒 Security Guidelines

### API Credentials
- Never commit API keys or secrets
- Use environment variables for testing
- Include proper credential validation
- Mask sensitive data in logs

### Code Security
- Validate all inputs
- Use secure HTTP libraries
- Enable certificate validation
- Follow language-specific security best practices

## 🐛 Bug Reports

### Before Submitting
- Check existing issues for duplicates
- Test with multiple language implementations
- Verify the issue with fresh API credentials

### Bug Report Format
```markdown
**Language**: [Python/Java/PHP/Node.js/C#/Other]
**Environment**: [OS, runtime version]
**API Endpoint**: [Which endpoint is affected]
**Expected Behavior**: [What should happen]
**Actual Behavior**: [What actually happens]
**Steps to Reproduce**: [Clear steps to recreate the issue]
**Error Messages**: [Any error output]
```

## ✨ Feature Requests

### Guidelines
- Ensure the feature benefits multiple language implementations
- Consider backward compatibility
- Provide clear use cases and examples
- Check if similar functionality exists

## 📋 Pull Request Process

### Before Submitting
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-language-client`
3. Implement your changes following the guidelines above
4. Test thoroughly with real API credentials
5. Update documentation as needed

### PR Requirements
- Clear description of changes
- Evidence of testing (screenshots, logs, or test results)
- Updated documentation
- Follows existing code patterns and standards

### Review Process
1. Automated checks (if any)
2. Code review by maintainers
3. Testing verification
4. Documentation review
5. Merge after approval

## 🎯 Project Goals

### Primary Objectives
- Provide production-ready API clients for multiple languages
- Maintain consistent authentication across implementations
- Offer comprehensive testing capabilities
- Support developer onboarding with clear examples

### Quality Standards
- All clients must successfully create real payments
- HMAC signatures must be identical across languages
- Error handling must be robust and informative
- Documentation must be clear and complete

## 📞 Support

### Getting Help
- Check the main README for basic usage
- Review language-specific documentation in `clients/`
- Test using the web interface for debugging
- Open an issue for specific problems

### Community Guidelines
- Be respectful and constructive
- Help others learn and contribute
- Share knowledge and best practices
- Follow the project's code of conduct

## 📜 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for contributing to the Ebioro API Test Suite! Your efforts help developers integrate with the Ebioro API more effectively across different programming languages.