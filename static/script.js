// Ebioro API Test Suite - JavaScript Functionality

class EbioroTestSuite {
    constructor() {
        this.apiClient = null;
        this.testResults = null;
        this.isCredentialsValid = false;
        this.loadingModal = null;
        this.supportedLanguages = {};
        this.selectedLanguage = 'python';
        
        this.initializeEventListeners();
        this.initializeBootstrap();
        this.loadSupportedLanguages();
        this.checkInitialCredentials();
    }
    
    initializeBootstrap() {
        // Initialize Bootstrap modal
        const modalElement = document.getElementById('loadingModal');
        if (modalElement) {
            this.loadingModal = new bootstrap.Modal(modalElement);
        }
    }
    
    initializeEventListeners() {
        // Credentials form
        const credentialsForm = document.getElementById('credentials-form');
        if (credentialsForm) {
            credentialsForm.addEventListener('submit', this.handleCredentialsSubmit.bind(this));
        }
        
        // Test buttons
        this.addEventListenerSafe('run-all-tests', 'click', this.runAllTests.bind(this));
        this.addEventListenerSafe('export-results', 'click', this.exportResults.bind(this));
        
        // API operation buttons
        this.addEventListenerSafe('create-payment', 'click', this.createPayment.bind(this));
        this.addEventListenerSafe('get-payment', 'click', this.getPayment.bind(this));
        this.addEventListenerSafe('list-payments', 'click', this.listPayments.bind(this));
        this.addEventListenerSafe('get-balances', 'click', this.getBalances.bind(this));
        this.addEventListenerSafe('get-refunds', 'click', this.getRefunds.bind(this));
        this.addEventListenerSafe('create-refund', 'click', this.createRefund.bind(this));
        
        // Signature validation
        this.addEventListenerSafe('validate-signature', 'click', this.validateSignature.bind(this));
        
        // Debug
        this.addEventListenerSafe('get-last-request', 'click', this.getLastRequest.bind(this));
        
        // Navigation
        this.initializeNavigation();
        
        // Language selection
        this.addEventListenerSafe('language-select', 'change', this.handleLanguageChange.bind(this));
    }
    
    async loadSupportedLanguages() {
        try {
            const response = await fetch('/api/supported-languages');
            const data = await response.json();
            
            if (data.success) {
                this.supportedLanguages = data.languages;
                this.populateLanguageSelect();
            }
        } catch (error) {
            console.error('Failed to load supported languages:', error);
        }
    }
    
    populateLanguageSelect() {
        const languageSelect = document.getElementById('language-select');
        if (languageSelect && Object.keys(this.supportedLanguages).length > 0) {
            languageSelect.innerHTML = '';
            
            Object.entries(this.supportedLanguages).forEach(([lang, info]) => {
                const option = document.createElement('option');
                option.value = lang;
                option.textContent = info.name;
                option.title = info.description;
                languageSelect.appendChild(option);
            });
            
            // Set default language
            languageSelect.value = this.selectedLanguage;
        }
    }
    
    handleLanguageChange(event) {
        this.selectedLanguage = event.target.value;
        const langInfo = this.supportedLanguages[this.selectedLanguage];
        
        if (langInfo) {
            // Update UI to show selected language info
            const connectionStatus = document.getElementById('connection-status');
            const statusMessage = document.getElementById('status-message');
            
            if (connectionStatus && statusMessage) {
                connectionStatus.style.display = 'block';
                connectionStatus.className = 'alert alert-info';
                statusMessage.textContent = `Selected: ${langInfo.name} - ${langInfo.description}`;
            }
        }
        
        // Reset credentials validation if language changed
        this.isCredentialsValid = false;
        this.showCredentialResult('info', 'Language changed. Please test credentials again.');
    }
    
    addEventListenerSafe(id, event, handler) {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener(event, handler);
        }
    }
    
    initializeNavigation() {
        // Handle tab navigation
        const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove active class from all links
                navLinks.forEach(l => l.classList.remove('active'));
                
                // Add active class to clicked link
                link.classList.add('active');
                
                // Show corresponding tab
                const target = link.getAttribute('href');
                if (target) {
                    this.showTab(target.replace('#', ''));
                }
            });
        });
    }
    
    showTab(tabId) {
        // Hide all tabs
        const tabs = document.querySelectorAll('.tab-pane');
        tabs.forEach(tab => {
            tab.classList.remove('show', 'active');
        });
        
        // Show selected tab
        const targetTab = document.getElementById(tabId);
        if (targetTab) {
            targetTab.classList.add('show', 'active', 'fade-in');
        }
    }
    
    checkInitialCredentials() {
        const apiKey = document.getElementById('api-key').value;
        const apiSecret = document.getElementById('api-secret').value;
        
        if (apiKey && apiSecret) {
            this.showConnectionStatus('info', 'Credentials found. Click "Test Credentials" to validate.');
        } else {
            this.showConnectionStatus('warning', 'Please enter your API credentials to begin testing.');
        }
    }
    
    showConnectionStatus(type, message) {
        const statusElement = document.getElementById('connection-status');
        const messageElement = document.getElementById('status-message');
        
        if (statusElement && messageElement) {
            statusElement.className = `alert alert-${type}`;
            messageElement.textContent = message;
            statusElement.style.display = 'block';
        }
    }
    
    showLoading(message = 'Processing...') {
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.textContent = message;
        }
        
        if (this.loadingModal) {
            this.loadingModal.show();
        }
    }
    
    hideLoading() {
        if (this.loadingModal) {
            this.loadingModal.hide();
        }
    }
    
    async handleCredentialsSubmit(event) {
        event.preventDefault();
        
        const apiKey = document.getElementById('api-key').value.trim();
        const apiSecret = document.getElementById('api-secret').value.trim();
        const baseUrl = document.getElementById('base-url').value.trim();
        const language = document.getElementById('language-select').value;
        
        if (!apiKey || !apiSecret) {
            this.showCredentialResult('danger', 'Please enter both API key and secret.');
            return;
        }
        
        this.showLoading('Testing credentials...');
        
        try {
            const response = await fetch('/api/test-credentials', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_key: apiKey,
                    api_secret: apiSecret,
                    base_url: baseUrl,
                    language: language
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.isCredentialsValid = true;
                const languageName = this.supportedLanguages[language]?.name || language;
                this.showCredentialResult('success', 
                    `✅ Credentials validated successfully using ${languageName}! (${data.elapsed_time.toFixed(2)}s)`);
                this.showConnectionStatus('success', `Connected to Ebioro API via ${languageName}`);
                
                // Enable test buttons
                this.enableTestButtons();
            } else {
                this.isCredentialsValid = false;
                const languageName = this.supportedLanguages[language]?.name || language;
                this.showCredentialResult('danger', 
                    `❌ ${data.error} (${languageName} - Status: ${data.status_code || 'Unknown'})`);
                this.showConnectionStatus('danger', 'Connection failed');
            }
        } catch (error) {
            this.isCredentialsValid = false;
            this.showCredentialResult('danger', `❌ Network error: ${error.message}`);
            this.showConnectionStatus('danger', 'Connection error');
        } finally {
            this.hideLoading();
        }
    }
    
    showCredentialResult(type, message) {
        const resultElement = document.getElementById('credential-result');
        const alertElement = document.getElementById('credential-alert');
        const messageElement = document.getElementById('credential-message');
        
        if (resultElement && alertElement && messageElement) {
            alertElement.className = `alert alert-${type}`;
            messageElement.innerHTML = message;
            resultElement.style.display = 'block';
            resultElement.classList.add('fade-in');
        }
    }
    
    enableTestButtons() {
        const buttons = [
            'run-all-tests', 'create-payment', 'get-payment', 'list-payments',
            'get-balances', 'get-refunds', 'validate-signature', 'get-last-request'
        ];
        
        buttons.forEach(buttonId => {
            const button = document.getElementById(buttonId);
            if (button) {
                button.disabled = false;
                button.classList.remove('btn-outline-secondary');
                button.classList.add('btn-primary');
            }
        });
    }
    
    async runAllTests() {
        if (!this.isCredentialsValid) {
            alert('Please test and validate your credentials first.');
            return;
        }
        
        this.showLoading('Running comprehensive tests...');
        this.showTestProgress();
        
        try {
            const response = await fetch('/api/run-tests', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.testResults = data.results;
                this.displayTestResults(data.results);
                this.showConnectionStatus('success', 'All tests completed successfully!');
            } else {
                this.showConnectionStatus('danger', `Test execution failed: ${data.error}`);
            }
        } catch (error) {
            this.showConnectionStatus('danger', `Network error: ${error.message}`);
        } finally {
            this.hideLoading();
            this.hideTestProgress();
        }
    }
    
    showTestProgress() {
        const progressElement = document.getElementById('test-progress');
        if (progressElement) {
            progressElement.style.display = 'block';
            
            // Simulate progress
            const progressBar = progressElement.querySelector('.progress-bar');
            if (progressBar) {
                let progress = 0;
                const interval = setInterval(() => {
                    progress += Math.random() * 15;
                    if (progress >= 95) {
                        progress = 95;
                        clearInterval(interval);
                    }
                    progressBar.style.width = `${progress}%`;
                }, 500);
            }
        }
    }
    
    hideTestProgress() {
        const progressElement = document.getElementById('test-progress');
        if (progressElement) {
            progressElement.style.display = 'none';
            
            const progressBar = progressElement.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = '0%';
            }
        }
    }
    
    displayTestResults(results) {
        const resultsElement = document.getElementById('test-results');
        if (!resultsElement) return;
        
        resultsElement.style.display = 'block';
        resultsElement.classList.add('fade-in');
        
        // Update summary statistics
        this.updateTestSummary(results);
        
        // Update detailed results
        this.updateTestDetails(results);
    }
    
    updateTestSummary(results) {
        const unitTests = results.unit_tests || {};
        const integrationTests = results.integration_tests || {};
        const signatureTests = results.signature_tests || {};
        
        // Calculate totals
        const totalTests = (unitTests.total_tests || 0) + 
                          (integrationTests.total_tests || 0) + 
                          (signatureTests.total_tests || 0);
        
        const passedTests = (unitTests.total_tests || 0) - (unitTests.failures || 0) - (unitTests.errors || 0) +
                           (integrationTests.successful || 0) +
                           (signatureTests.passed || 0);
        
        const failedTests = totalTests - passedTests;
        
        // Update DOM
        this.updateElementText('total-tests', totalTests);
        this.updateElementText('passed-tests', passedTests);
        this.updateElementText('failed-tests', failedTests);
    }
    
    updateTestDetails(results) {
        const detailsContent = document.getElementById('test-details-content');
        if (!detailsContent) return;
        
        let html = '';
        
        // Unit tests
        if (results.unit_tests) {
            html += this.generateTestSection('Unit Tests', results.unit_tests, 'unit');
        }
        
        // Integration tests
        if (results.integration_tests && !results.integration_tests.skipped) {
            html += this.generateTestSection('Integration Tests', results.integration_tests, 'integration');
        }
        
        // Signature tests
        if (results.signature_tests && !results.signature_tests.skipped) {
            html += this.generateTestSection('Signature Tests', results.signature_tests, 'signature');
        }
        
        detailsContent.innerHTML = html;
    }
    
    generateTestSection(title, testData, type) {
        const success = type === 'unit' ? testData.success : 
                       type === 'integration' ? testData.successful > 0 :
                       testData.failed === 0;
        
        const statusClass = success ? 'success' : 'danger';
        const statusIcon = success ? 'check-circle' : 'times-circle';
        
        return `
            <div class="card mb-3">
                <div class="card-header">
                    <h6><i class="fas fa-${statusIcon} text-${statusClass}"></i> ${title}</h6>
                </div>
                <div class="card-body">
                    ${this.generateTestStats(testData, type)}
                    ${this.generateTestDetails(testData, type)}
                </div>
            </div>
        `;
    }
    
    generateTestStats(testData, type) {
        if (type === 'unit') {
            return `
                <div class="row mb-3">
                    <div class="col-md-4">
                        <small class="text-muted">Total:</small>
                        <div class="h5">${testData.total_tests || 0}</div>
                    </div>
                    <div class="col-md-4">
                        <small class="text-muted">Failures:</small>
                        <div class="h5 text-danger">${testData.failures || 0}</div>
                    </div>
                    <div class="col-md-4">
                        <small class="text-muted">Errors:</small>
                        <div class="h5 text-warning">${testData.errors || 0}</div>
                    </div>
                </div>
            `;
        } else if (type === 'integration') {
            return `
                <div class="row mb-3">
                    <div class="col-md-4">
                        <small class="text-muted">Total:</small>
                        <div class="h5">${testData.total_tests || 0}</div>
                    </div>
                    <div class="col-md-4">
                        <small class="text-muted">Successful:</small>
                        <div class="h5 text-success">${testData.successful || 0}</div>
                    </div>
                    <div class="col-md-4">
                        <small class="text-muted">Failed:</small>
                        <div class="h5 text-danger">${testData.failed || 0}</div>
                    </div>
                </div>
            `;
        } else if (type === 'signature') {
            return `
                <div class="row mb-3">
                    <div class="col-md-4">
                        <small class="text-muted">Total:</small>
                        <div class="h5">${testData.total_tests || 0}</div>
                    </div>
                    <div class="col-md-4">
                        <small class="text-muted">Passed:</small>
                        <div class="h5 text-success">${testData.passed || 0}</div>
                    </div>
                    <div class="col-md-4">
                        <small class="text-muted">Failed:</small>
                        <div class="h5 text-danger">${testData.failed || 0}</div>
                    </div>
                </div>
            `;
        }
        return '';
    }
    
    generateTestDetails(testData, type) {
        if (type === 'integration' && testData.results) {
            let html = '<h6>Test Details:</h6>';
            testData.results.forEach(test => {
                const statusClass = test.success ? 'success' : 'danger';
                const statusIcon = test.success ? 'check' : 'times';
                html += `
                    <div class="alert alert-${statusClass} py-2">
                        <i class="fas fa-${statusIcon}"></i> 
                        <strong>${test.test_name}</strong>
                        <div><small>${test.details}</small></div>
                        ${test.error ? `<div><small class="text-muted">Error: ${test.error}</small></div>` : ''}
                    </div>
                `;
            });
            return html;
        } else if (type === 'signature' && testData.results) {
            let html = '<h6>Signature Test Details:</h6>';
            testData.results.forEach(test => {
                const statusClass = test.success ? 'success' : 'danger';
                const statusIcon = test.success ? 'check' : 'times';
                html += `
                    <div class="alert alert-${statusClass} py-2">
                        <i class="fas fa-${statusIcon}"></i> 
                        <strong>${test.description}</strong>
                        ${test.error ? `<div><small class="text-muted">Error: ${test.error}</small></div>` : ''}
                    </div>
                `;
            });
            return html;
        }
        return '';
    }
    
    updateElementText(id, text) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = text;
        }
    }
    
    async createPayment() {
        if (!this.isCredentialsValid) {
            alert('Please test and validate your credentials first.');
            return;
        }
        
        const amount = parseInt(document.getElementById('payment-amount').value) || 1000;
        const currency = document.getElementById('payment-currency').value || 'USD';
        const description = document.getElementById('payment-description').value || 'Test payment from web interface';
        
        this.showLoading('Creating payment...');
        
        try {
            const response = await fetch('/api/create-payment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ amount, currency, description })
            });
            
            const data = await response.json();
            this.displayApiResponse(data);
            
            if (data.success) {
                this.showConnectionStatus('success', 
                    `Payment created successfully! ID: ${data.response.id}`);
            } else {
                this.showConnectionStatus('danger', 
                    `Payment creation failed (Status: ${data.status_code})`);
            }
        } catch (error) {
            this.showConnectionStatus('danger', `Network error: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    async getPayment() {
        if (!this.isCredentialsValid) {
            alert('Please test and validate your credentials first.');
            return;
        }
        
        const paymentId = document.getElementById('payment-id').value.trim();
        
        if (!paymentId) {
            alert('Please enter a payment ID.');
            return;
        }
        
        this.showLoading('Retrieving payment...');
        
        try {
            const response = await fetch(`/api/get-payment/${paymentId}`);
            const data = await response.json();
            this.displayApiResponse(data);
            
            if (data.success) {
                this.showConnectionStatus('success', 'Payment retrieved successfully!');
            } else {
                this.showConnectionStatus('danger', 
                    `Payment retrieval failed (Status: ${data.status_code})`);
            }
        } catch (error) {
            this.showConnectionStatus('danger', `Network error: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    async listPayments() {
        if (!this.isCredentialsValid) {
            alert('Please test and validate your credentials first.');
            return;
        }
        
        this.showLoading('Listing payments...');
        
        try {
            const response = await fetch('/api/list-payments');
            const data = await response.json();
            this.displayApiResponse(data);
            
            if (data.success) {
                const total = data.response.total || data.response.payments?.length || 0;
                this.showConnectionStatus('success', `Retrieved ${total} payments`);
            } else {
                this.showConnectionStatus('danger', 
                    `Payment listing failed (Status: ${data.status_code})`);
            }
        } catch (error) {
            this.showConnectionStatus('danger', `Network error: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    async getBalances() {
        if (!this.isCredentialsValid) {
            alert('Please test and validate your credentials first.');
            return;
        }
        
        this.showLoading('Retrieving balances...');
        
        try {
            const response = await fetch('/api/get-balances');
            const data = await response.json();
            this.displayApiResponse(data);
            
            if (data.success) {
                const balances = data.response.balances?.length || 0;
                this.showConnectionStatus('success', `Retrieved ${balances} account balances`);
            } else {
                this.showConnectionStatus('danger', 
                    `Balance retrieval failed (Status: ${data.status_code})`);
            }
        } catch (error) {
            this.showConnectionStatus('danger', `Network error: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    async getRefunds() {
        if (!this.isCredentialsValid) {
            alert('Please test and validate your credentials first.');
            return;
        }
        
        this.showLoading('Retrieving refunds...');
        
        try {
            const response = await fetch('/api/get-refunds');
            const data = await response.json();
            this.displayApiResponse(data);
            
            if (data.success) {
                this.showConnectionStatus('success', 'Refunds retrieved successfully!');
            } else {
                this.showConnectionStatus('danger', 
                    `Refund retrieval failed (Status: ${data.status_code})`);
            }
        } catch (error) {
            this.showConnectionStatus('danger', `Network error: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    async createRefund() {
        if (!this.isCredentialsValid) {
            alert('Please test and validate your credentials first.');
            return;
        }
        
        const paymentId = document.getElementById('refund-payment-id').value.trim();
        const amount = document.getElementById('refund-amount').value.trim();
        
        if (!paymentId) {
            alert('Please enter a Payment ID to refund.');
            return;
        }
        
        this.showLoading('Creating refund...');
        
        try {
            const requestBody = { payment_id: paymentId };
            if (amount) {
                requestBody.amount = parseInt(amount);
            }
            
            const response = await fetch('/api/create-refund', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            const data = await response.json();
            this.displayApiResponse(data);
            
            if (data.success) {
                this.showConnectionStatus('success', 
                    `Refund created successfully! Refund ID: ${data.response?.id || 'N/A'}`);
            } else {
                this.showConnectionStatus('danger', 
                    `Refund creation failed (Status: ${data.status_code})`);
            }
        } catch (error) {
            this.showConnectionStatus('danger', `Network error: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    async validateSignature() {
        if (!this.isCredentialsValid) {
            alert('Please test and validate your credentials first.');
            return;
        }
        
        this.showLoading('Validating signature implementation...');
        
        try {
            const response = await fetch('/api/validate-signature');
            const data = await response.json();
            
            if (data.success) {
                this.displaySignatureResults(data.results);
                this.showConnectionStatus('success', 'Signature validation completed!');
            } else {
                this.showConnectionStatus('danger', `Signature validation failed: ${data.error}`);
            }
        } catch (error) {
            this.showConnectionStatus('danger', `Network error: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    displaySignatureResults(results) {
        const resultsElement = document.getElementById('signature-results');
        const detailsElement = document.getElementById('signature-details');
        
        if (!resultsElement || !detailsElement) return;
        
        resultsElement.style.display = 'block';
        resultsElement.classList.add('fade-in');
        
        let html = `
            <div class="row mb-3">
                <div class="col-md-4">
                    <small class="text-muted">Total Tests:</small>
                    <div class="h5">${results.total_tests}</div>
                </div>
                <div class="col-md-4">
                    <small class="text-muted">Passed:</small>
                    <div class="h5 text-success">${results.passed}</div>
                </div>
                <div class="col-md-4">
                    <small class="text-muted">Failed:</small>
                    <div class="h5 text-danger">${results.failed}</div>
                </div>
            </div>
        `;
        
        if (results.results) {
            html += '<h6>Test Details:</h6>';
            results.results.forEach(test => {
                const statusClass = test.success ? 'success' : 'danger';
                const statusIcon = test.success ? 'check' : 'times';
                html += `
                    <div class="alert alert-${statusClass} py-2">
                        <i class="fas fa-${statusIcon}"></i> 
                        <strong>${test.description}</strong>
                        ${test.error ? `<div><small class="text-muted">Error: ${test.error}</small></div>` : ''}
                    </div>
                `;
            });
        }
        
        detailsElement.innerHTML = html;
    }
    
    async getLastRequest() {
        if (!this.isCredentialsValid) {
            alert('Please test and validate your credentials first.');
            return;
        }
        
        this.showLoading('Retrieving request details...');
        
        try {
            const response = await fetch('/api/get-last-request');
            const data = await response.json();
            
            if (data.success) {
                this.displayDebugInfo(data.request, data.response);
                this.showConnectionStatus('success', 'Debug information retrieved!');
            } else {
                this.showConnectionStatus('danger', `Debug retrieval failed: ${data.error}`);
            }
        } catch (error) {
            this.showConnectionStatus('danger', `Network error: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    displayDebugInfo(requestData, responseData) {
        const requestElement = document.getElementById('debug-request');
        const responseElement = document.getElementById('debug-response');
        
        if (requestElement) {
            requestElement.textContent = JSON.stringify(requestData, null, 2);
        }
        
        if (responseElement) {
            responseElement.textContent = JSON.stringify(responseData, null, 2);
        }
    }
    
    displayApiResponse(data) {
        const responseElement = document.getElementById('api-response');
        if (responseElement) {
            responseElement.textContent = JSON.stringify(data, null, 2);
            responseElement.classList.add('fade-in');
        }
    }
    
    async exportResults() {
        if (!this.testResults) {
            alert('No test results available. Please run tests first.');
            return;
        }
        
        try {
            const response = await fetch('/api/export-results');
            const data = await response.json();
            
            if (data.success) {
                const blob = new Blob([JSON.stringify(data.results, null, 2)], {
                    type: 'application/json'
                });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `ebioro_api_test_results_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                this.showConnectionStatus('success', 'Test results exported successfully!');
            } else {
                this.showConnectionStatus('danger', `Export failed: ${data.error}`);
            }
        } catch (error) {
            this.showConnectionStatus('danger', `Export error: ${error.message}`);
        }
    }
    
    // Utility methods
    formatTimestamp(timestamp) {
        return new Date(timestamp * 1000).toLocaleString();
    }
    
    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount / 100);
    }
    
    formatElapsedTime(seconds) {
        if (seconds < 1) {
            return `${Math.round(seconds * 1000)}ms`;
        }
        return `${seconds.toFixed(2)}s`;
    }
    
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showConnectionStatus('success', 'Copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }
    
    // Mobile responsive handlers
    handleMobileNavigation() {
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');
        
        if (window.innerWidth <= 768) {
            sidebar.addEventListener('click', (e) => {
                e.stopPropagation();
            });
            
            mainContent.addEventListener('click', () => {
                sidebar.classList.remove('show');
            });
        }
    }
    
    // Initialize mobile handlers
    initializeMobile() {
        this.handleMobileNavigation();
        
        window.addEventListener('resize', () => {
            this.handleMobileNavigation();
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const testSuite = new EbioroTestSuite();
    testSuite.initializeMobile();
    
    // Global error handler
    window.addEventListener('error', (event) => {
        console.error('Global error:', event.error);
    });
    
    // Global unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
    });
});

// Export for potential external use
window.EbioroTestSuite = EbioroTestSuite;
