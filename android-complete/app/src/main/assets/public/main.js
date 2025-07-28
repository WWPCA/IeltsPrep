// IELTS GenAI Prep - Mobile App JavaScript Implementation
import { App } from '@capacitor/app';
import { Network } from '@capacitor/network';
import { Toast } from '@capacitor/toast';
import { Storage } from '@capacitor/storage';
import { Device } from '@capacitor/device';
import { Http } from '@capacitor-community/http';

// AWS Cognito and DynamoDB Integration
class AWSCognitoAuth {
    constructor() {
        this.cognitoConfig = {
            region: 'us-east-1',
            userPoolId: 'us-east-1_ABCDEFGHI',
            clientId: '1234567890abcdefghijklmnop'
        };
        this.apiBaseUrl = 'https://api.ieltsaiprep.com';
    }

    async signIn(email, password) {
        try {
            const response = await Http.request({
                method: 'POST',
                url: `${this.apiBaseUrl}/api/mobile-login`,
                headers: {
                    'Content-Type': 'application/json',
                },
                data: {
                    email: email,
                    password: password,
                    platform: 'android'
                }
            });

            if (response.data.success) {
                // Store authentication token
                await Storage.set({
                    key: 'authToken',
                    value: response.data.accessToken
                });
                
                await Storage.set({
                    key: 'refreshToken',
                    value: response.data.refreshToken
                });

                await Storage.set({
                    key: 'userProfile',
                    value: JSON.stringify(response.data.user)
                });

                return {
                    success: true,
                    user: response.data.user,
                    accessToken: response.data.accessToken
                };
            } else {
                throw new Error(response.data.message || 'Authentication failed');
            }
        } catch (error) {
            console.error('Sign in error:', error);
            throw error;
        }
    }

    async validateToken(token) {
        try {
            const response = await Http.request({
                method: 'POST',
                url: `${this.apiBaseUrl}/api/validate-token`,
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            return response.data.valid;
        } catch (error) {
            console.error('Token validation error:', error);
            return false;
        }
    }

    async signOut() {
        await Storage.remove({ key: 'authToken' });
        await Storage.remove({ key: 'refreshToken' });
        await Storage.remove({ key: 'userProfile' });
    }
}

// Google Play Billing Integration
class GooglePlayBilling {
    constructor() {
        this.productIds = {
            assessments_4pack: 'com.ieltsaiprep.app.assessments_4pack'
        };
        this.apiBaseUrl = 'https://api.ieltsaiprep.com';
    }

    async initializeBilling() {
        // This would be called from native Android code
        return new Promise((resolve, reject) => {
            if (window.AndroidBridge) {
                window.AndroidBridge.initializeBilling((result) => {
                    if (result.success) {
                        resolve(result);
                    } else {
                        reject(new Error(result.error));
                    }
                });
            } else {
                // Fallback for testing
                resolve({ success: true, message: 'Billing client ready' });
            }
        });
    }

    async purchaseAssessments() {
        try {
            // Trigger native billing flow
            return new Promise((resolve, reject) => {
                if (window.AndroidBridge) {
                    window.AndroidBridge.purchaseProduct(
                        this.productIds.assessments_4pack,
                        (result) => {
                            if (result.success) {
                                this.verifyPurchase(result.purchaseToken)
                                    .then(resolve)
                                    .catch(reject);
                            } else {
                                reject(new Error(result.error));
                            }
                        }
                    );
                } else {
                    // Simulate purchase for testing
                    setTimeout(() => {
                        this.simulatePurchase().then(resolve).catch(reject);
                    }, 1000);
                }
            });
        } catch (error) {
            console.error('Purchase error:', error);
            throw error;
        }
    }

    async verifyPurchase(purchaseToken) {
        try {
            const deviceId = await this.getDeviceId();
            
            const response = await Http.request({
                method: 'POST',
                url: `${this.apiBaseUrl}/api/verify-purchase`,
                headers: {
                    'Content-Type': 'application/json',
                },
                data: {
                    purchaseToken: purchaseToken,
                    productId: this.productIds.assessments_4pack,
                    platform: 'android',
                    deviceId: deviceId
                }
            });

            if (response.data.success) {
                return {
                    success: true,
                    user: response.data.user,
                    assessments: response.data.assessments
                };
            } else {
                throw new Error('Purchase verification failed');
            }
        } catch (error) {
            console.error('Purchase verification error:', error);
            throw error;
        }
    }

    async simulatePurchase() {
        // Simulate purchase for development/testing
        const mockPurchaseToken = `mock_token_${Date.now()}`;
        return this.verifyPurchase(mockPurchaseToken);
    }

    async getDeviceId() {
        try {
            const info = await Device.getId();
            return info.uuid;
        } catch (error) {
            return `unknown_${Date.now()}`;
        }
    }
}

// AWS Services Integration
class AWSServices {
    constructor() {
        this.apiBaseUrl = 'https://api.ieltsaiprep.com';
    }

    async callNovaSonic(audioData, assessmentType = 'speaking') {
        try {
            const authToken = await Storage.get({ key: 'authToken' });
            
            const response = await Http.request({
                method: 'POST',
                url: `${this.apiBaseUrl}/api/nova-sonic-stream`,
                headers: {
                    'Authorization': `Bearer ${authToken.value}`,
                    'Content-Type': 'application/json'
                },
                data: {
                    audioData: audioData,
                    assessmentType: assessmentType,
                    voice: 'en-GB-feminine'
                }
            });

            return response.data;
        } catch (error) {
            console.error('Nova Sonic error:', error);
            throw error;
        }
    }

    async callNovaMicro(textData, assessmentType = 'writing') {
        try {
            const authToken = await Storage.get({ key: 'authToken' });
            
            const response = await Http.request({
                method: 'POST',
                url: `${this.apiBaseUrl}/api/nova-micro-assessment`,
                headers: {
                    'Authorization': `Bearer ${authToken.value}`,
                    'Content-Type': 'application/json'
                },
                data: {
                    text: textData,
                    assessmentType: assessmentType
                }
            });

            return response.data;
        } catch (error) {
            console.error('Nova Micro error:', error);
            throw error;
        }
    }

    async syncUserData() {
        try {
            const authToken = await Storage.get({ key: 'authToken' });
            
            const response = await Http.request({
                method: 'GET',
                url: `${this.apiBaseUrl}/api/user-profile`,
                headers: {
                    'Authorization': `Bearer ${authToken.value}`
                }
            });

            if (response.data.success) {
                await Storage.set({
                    key: 'userProfile',
                    value: JSON.stringify(response.data.user)
                });
            }

            return response.data;
        } catch (error) {
            console.error('User data sync error:', error);
            throw error;
        }
    }
}

// Main App Controller
class IELTSMobileApp {
    constructor() {
        this.auth = new AWSCognitoAuth();
        this.billing = new GooglePlayBilling();
        this.aws = new AWSServices();
        this.currentUser = null;
        this.isAuthenticated = false;
    }

    async initialize() {
        try {
            // Check for stored authentication
            await this.checkStoredAuth();
            
            // Initialize billing
            await this.billing.initializeBilling();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Show welcome message
            this.showStatus('Welcome to IELTS GenAI Prep', 'info');
            
            console.log('IELTS Mobile App initialized successfully');
        } catch (error) {
            console.error('App initialization error:', error);
            this.showStatus('App initialization failed', 'error');
        }
    }

    async checkStoredAuth() {
        try {
            const authToken = await Storage.get({ key: 'authToken' });
            
            if (authToken.value) {
                const isValid = await this.auth.validateToken(authToken.value);
                
                if (isValid) {
                    const userProfile = await Storage.get({ key: 'userProfile' });
                    this.currentUser = JSON.parse(userProfile.value || '{}');
                    this.isAuthenticated = true;
                    this.showFeaturesSection();
                    return;
                }
            }
            
            this.showAuthSection();
        } catch (error) {
            console.log('No valid stored auth found');
            this.showAuthSection();
        }
    }

    setupEventListeners() {
        // Login form submission
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        // Register button
        const registerBtn = document.getElementById('registerBtn');
        if (registerBtn) {
            registerBtn.addEventListener('click', () => {
                this.showPaymentSection();
            });
        }

        // Google Pay button
        const googlePayBtn = document.getElementById('googlePayBtn');
        if (googlePayBtn) {
            googlePayBtn.addEventListener('click', () => {
                this.handlePayment();
            });
        }

        // Navigation buttons
        const backToLoginBtn = document.getElementById('backToLoginBtn');
        if (backToLoginBtn) {
            backToLoginBtn.addEventListener('click', () => {
                this.showAuthSection();
            });
        }

        const startAssessmentBtn = document.getElementById('startAssessmentBtn');
        if (startAssessmentBtn) {
            startAssessmentBtn.addEventListener('click', () => {
                this.openWebsiteAssessment();
            });
        }

        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                this.handleLogout();
            });
        }
    }

    async handleLogin() {
        const email = document.getElementById('email')?.value;
        const password = document.getElementById('password')?.value;

        if (!email || !password) {
            this.showStatus('Please enter email and password', 'error');
            return;
        }

        this.showStatus('Signing in...', 'info');

        try {
            const result = await this.auth.signIn(email, password);
            
            this.currentUser = result.user;
            this.isAuthenticated = true;
            
            // Sync user data
            await this.aws.syncUserData();
            
            this.showStatus('Login successful!', 'success');
            this.showFeaturesSection();
            
        } catch (error) {
            this.showStatus(error.message || 'Login failed', 'error');
        }
    }

    async handlePayment() {
        this.showStatus('Processing payment...', 'info');

        try {
            const result = await this.billing.purchaseAssessments();
            
            if (result.success) {
                this.currentUser = result.user;
                this.showStatus('Payment successful! Please login with your new account.', 'success');
                this.showAuthSection();
            } else {
                throw new Error('Payment processing failed');
            }
            
        } catch (error) {
            this.showStatus(error.message || 'Payment failed', 'error');
        }
    }

    async openWebsiteAssessment() {
        try {
            const authToken = await Storage.get({ key: 'authToken' });
            
            if (authToken.value) {
                // Open ieltsaiprep.com with authentication token
                const url = `https://www.ieltsaiprep.com?mobile_token=${authToken.value}&platform=android`;
                
                // Use Capacitor Browser or system browser
                if (window.Capacitor?.Plugins?.Browser) {
                    await window.Capacitor.Plugins.Browser.open({ url });
                } else {
                    window.open(url, '_system');
                }
                
                await Toast.show({
                    text: 'Opening assessments on ieltsaiprep.com...'
                });
            } else {
                this.showStatus('Please login first', 'error');
            }
        } catch (error) {
            this.showStatus('Failed to open website', 'error');
        }
    }

    async handleLogout() {
        try {
            await this.auth.signOut();
            this.currentUser = null;
            this.isAuthenticated = false;
            this.showStatus('Logged out successfully', 'info');
            this.showAuthSection();
        } catch (error) {
            this.showStatus('Logout failed', 'error');
        }
    }

    showAuthSection() {
        this.toggleSection('authSection', true);
        this.toggleSection('paymentSection', false);
        this.toggleSection('featuresSection', false);
    }

    showPaymentSection() {
        this.toggleSection('authSection', false);
        this.toggleSection('paymentSection', true);
        this.toggleSection('featuresSection', false);
    }

    showFeaturesSection() {
        this.toggleSection('authSection', false);
        this.toggleSection('paymentSection', false);
        this.toggleSection('featuresSection', true);
    }

    toggleSection(sectionId, show) {
        const section = document.getElementById(sectionId);
        if (section) {
            if (show) {
                section.style.display = 'block';
                section.classList.add('show');
            } else {
                section.style.display = 'none';
                section.classList.remove('show');
            }
        }
    }

    showStatus(message, type) {
        const statusEl = document.getElementById('statusMessage');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = `status ${type}`;
            statusEl.classList.remove('hidden');

            if (type === 'success' || type === 'info') {
                setTimeout(() => {
                    statusEl.classList.add('hidden');
                }, 3000);
            }
        }

        // Also show toast for important messages
        if (type === 'error' || type === 'success') {
            Toast.show({ text: message });
        }
    }
}

// Android Bridge for native calls
window.AndroidBridge = {
    initializeBilling: function(callback) {
        // This will be implemented in MainActivity.java
        console.log('Billing initialization requested');
        callback({ success: true, message: 'Billing client ready' });
    },
    
    purchaseProduct: function(productId, callback) {
        // This will trigger the native billing flow
        console.log('Purchase requested for:', productId);
        // Simulate success for development
        setTimeout(() => {
            callback({ 
                success: true, 
                purchaseToken: `mock_token_${Date.now()}`
            });
        }, 1000);
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.ieltsApp = new IELTSMobileApp();
    window.ieltsApp.initialize();
});

// Handle app state changes
App.addListener('appStateChange', ({ isActive }) => {
    if (isActive && window.ieltsApp) {
        // Refresh user data when app becomes active
        window.ieltsApp.aws.syncUserData().catch(console.error);
    }
});

// Handle network changes
Network.addListener('networkStatusChange', status => {
    if (!status.connected) {
        document.getElementById('statusMessage').textContent = 'No internet connection';
        document.getElementById('statusMessage').className = 'status error';
        document.getElementById('statusMessage').classList.remove('hidden');
    }
});

// Export for global access
window.IELTSMobileApp = IELTSMobileApp;