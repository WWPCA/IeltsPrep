/**
 * IELTS GenAI Prep - Mobile App Integration
 * Complete iOS/Android implementation with QR authentication and in-app purchases
 */

import { CapacitorConfig } from '@capacitor/core';
import { Device } from '@capacitor/device';
import { Network } from '@capacitor/network';
import { Toast } from '@capacitor/toast';
import { App } from '@capacitor/app';

// Regional API configuration for global deployment
class MobileAPIClient {
  private baseURL: string;
  private region: string;
  private sessionToken: string | null = null;
  private qrAuthToken: string | null = null;

  constructor() {
    this.detectRegionAndInitialize();
  }

  private async detectRegionAndInitialize() {
    try {
      const deviceInfo = await Device.getInfo();
      const networkInfo = await Network.getStatus();
      
      // Determine optimal region based on device location
      this.region = await this.detectOptimalRegion();
      this.baseURL = this.getRegionalEndpoint(this.region);
      
      console.log(`Initialized for region: ${this.region}`);
    } catch (error) {
      console.error('Failed to initialize API client:', error);
      // Fallback to US East
      this.region = 'us-east-1';
      this.baseURL = 'https://api-us.ieltsaiprep.com';
    }
  }

  private async detectOptimalRegion(): Promise<string> {
    const deviceInfo = await Device.getInfo();
    const locale = deviceInfo.locale || 'en-US';
    
    // Regional mapping based on device locale
    const regionMap: { [key: string]: string } = {
      'en-GB': 'eu-west-1',
      'de': 'eu-west-1',
      'fr': 'eu-west-1',
      'es': 'eu-west-1',
      'it': 'eu-west-1',
      'ja': 'ap-southeast-1',
      'ko': 'ap-southeast-1',
      'zh': 'ap-southeast-1',
      'th': 'ap-southeast-1',
      'vi': 'ap-southeast-1'
    };

    return regionMap[locale.split('-')[0]] || 'us-east-1';
  }

  private getRegionalEndpoint(region: string): string {
    const endpoints = {
      'us-east-1': 'https://api-us.ieltsaiprep.com',
      'eu-west-1': 'https://api-eu.ieltsaiprep.com',
      'ap-southeast-1': 'https://api-ap.ieltsaiprep.com'
    };
    return endpoints[region] || endpoints['us-east-1'];
  }

  async makeAPICall(endpoint: string, method = 'POST', data: any = null): Promise<any> {
    const url = `${this.baseURL}${endpoint}`;
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'IELTSGenAIPrepMobile/2.0.0',
        ...(this.sessionToken && { 'Authorization': `Bearer ${this.sessionToken}` })
      },
      ...(data && { body: JSON.stringify(data) })
    };

    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`API call to ${endpoint} failed:`, error);
      throw error;
    }
  }

  async registerUser(email: string, password: string): Promise<any> {
    return this.makeAPICall('/auth/register', 'POST', { email, password });
  }

  async loginUser(email: string, password: string): Promise<any> {
    const result = await this.makeAPICall('/auth/login', 'POST', { email, password });
    if (result.success) {
      this.sessionToken = result.token;
    }
    return result;
  }

  async generateQRTokenAfterPurchase(userEmail: string, productId: string): Promise<any> {
    return this.makeAPICall('/auth/generate-qr', 'POST', {
      user_email: userEmail,
      product_id: productId,
      purchase_verified: true
    });
  }

  async verifyApplePurchase(receiptData: string, productId: string): Promise<any> {
    return this.makeAPICall('/purchase/verify/apple', 'POST', {
      receipt_data: receiptData,
      product_id: productId
    });
  }

  async verifyGooglePurchase(purchaseToken: string, productId: string): Promise<any> {
    return this.makeAPICall('/purchase/verify/google', 'POST', {
      purchase_token: purchaseToken,
      product_id: productId
    });
  }

  async submitSpeechAssessment(audioData: Blob, assessmentType: string): Promise<any> {
    // Nova Sonic streaming always routes to us-east-1
    const novaSonicURL = 'https://api-us.ieltsaiprep.com/nova-sonic/stream';
    const formData = new FormData();
    formData.append('audio', audioData);
    formData.append('assessment_type', assessmentType);

    const response = await fetch(novaSonicURL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.sessionToken}`
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Speech assessment failed: ${response.statusText}`);
    }

    return response.json();
  }

  async submitWritingAssessment(essayText: string, prompt: string, assessmentType: string): Promise<any> {
    return this.makeAPICall('/assess-writing', 'POST', {
      essay_text: essayText,
      prompt,
      assessment_type: assessmentType
    });
  }
}

// iOS In-App Purchase Manager
class iOSPurchaseManager {
  private apiClient: MobileAPIClient;
  private products: string[] = [
    'academic_speaking_assessment',
    'academic_writing_assessment',
    'general_speaking_assessment',
    'general_writing_assessment'
  ];

  constructor(apiClient: MobileAPIClient) {
    this.apiClient = apiClient;
  }

  async initializePurchases(): Promise<void> {
    try {
      // Initialize StoreKit for iOS
      if (window.StoreKit) {
        await window.StoreKit.initialize();
        console.log('StoreKit initialized successfully');
      }
    } catch (error) {
      console.error('Failed to initialize purchases:', error);
      throw error;
    }
  }

  async loadProducts(): Promise<any[]> {
    try {
      if (!window.StoreKit) {
        throw new Error('StoreKit not available');
      }

      const products = await window.StoreKit.loadProducts(this.products);
      return products;
    } catch (error) {
      console.error('Failed to load products:', error);
      throw error;
    }
  }

  async purchaseProduct(productId: string, userEmail: string): Promise<any> {
    try {
      await this.showToast('Processing purchase...', 'bottom');

      // Start iOS purchase flow
      const transaction = await window.StoreKit.purchaseProduct(productId);

      if (transaction.transactionState === 'purchased') {
        // Verify purchase with backend
        const verification = await this.apiClient.verifyApplePurchase(
          transaction.transactionReceipt,
          productId
        );

        if (verification.success) {
          // Generate QR token for website access
          const qrData = await this.apiClient.generateQRTokenAfterPurchase(
            userEmail,
            productId
          );

          await this.showPurchaseSuccessWithQR(productId, qrData);
          return { success: true, qrData, verification };
        } else {
          throw new Error('Purchase verification failed');
        }
      } else {
        throw new Error('Purchase was not completed');
      }
    } catch (error) {
      await this.showToast(`Purchase failed: ${error.message}`, 'bottom');
      throw error;
    }
  }

  private async showPurchaseSuccessWithQR(productId: string, qrData: any): Promise<void> {
    const productNames = {
      'academic_speaking_assessment': 'Academic Speaking Assessment',
      'academic_writing_assessment': 'Academic Writing Assessment',
      'general_speaking_assessment': 'General Speaking Assessment',
      'general_writing_assessment': 'General Writing Assessment'
    };

    const productName = productNames[productId] || 'Assessment';

    // Create modal with QR code
    const modal = document.createElement('div');
    modal.className = 'purchase-success-modal';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="success-header">
          <i class="fas fa-check-circle"></i>
          <h2>Purchase Successful!</h2>
          <p>${productName} is now available</p>
        </div>
        
        <div class="qr-section">
          <h3>Access on Website</h3>
          <div class="qr-container">
            <img src="${qrData.qr_code_image}" alt="QR Code" class="qr-image">
          </div>
          <p class="qr-instructions">
            Scan this QR code on <strong>ieltsaiprep.com</strong> to access your assessment
          </p>
          <p class="qr-expiry">Code expires in 10 minutes</p>
        </div>
        
        <div class="modal-actions">
          <button class="btn-primary" onclick="this.closest('.purchase-success-modal').remove()">
            Continue in App
          </button>
          <button class="btn-secondary" onclick="this.shareQRCode('${qrData.qr_code_image}')">
            Share QR Code
          </button>
        </div>
      </div>
    `;

    // Add modal styles
    const styles = `
      <style>
        .purchase-success-modal {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0,0,0,0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10000;
        }
        .modal-content {
          background: white;
          border-radius: 16px;
          padding: 24px;
          max-width: 350px;
          width: 90%;
          text-align: center;
        }
        .success-header i {
          font-size: 48px;
          color: #28a745;
          margin-bottom: 16px;
        }
        .qr-container {
          background: #f8f9fa;
          padding: 16px;
          border-radius: 12px;
          margin: 16px 0;
        }
        .qr-image {
          width: 200px;
          height: 200px;
          border-radius: 8px;
        }
        .qr-instructions {
          font-size: 14px;
          color: #6c757d;
          margin: 8px 0;
        }
        .qr-expiry {
          font-size: 12px;
          color: #dc3545;
          font-weight: 500;
        }
        .modal-actions {
          margin-top: 24px;
        }
        .btn-primary, .btn-secondary {
          padding: 12px 24px;
          border: none;
          border-radius: 8px;
          font-weight: 500;
          margin: 4px;
          cursor: pointer;
        }
        .btn-primary {
          background: #007bff;
          color: white;
        }
        .btn-secondary {
          background: #6c757d;
          color: white;
        }
      </style>
    `;

    document.head.insertAdjacentHTML('beforeend', styles);
    document.body.appendChild(modal);

    // Auto-close after 2 minutes
    setTimeout(() => {
      if (modal.parentNode) {
        modal.remove();
      }
    }, 120000);
  }

  async restorePurchases(): Promise<any[]> {
    try {
      if (!window.StoreKit) {
        throw new Error('StoreKit not available');
      }

      const transactions = await window.StoreKit.restoreTransactions();
      return transactions;
    } catch (error) {
      console.error('Failed to restore purchases:', error);
      throw error;
    }
  }

  private async showToast(message: string, position: 'top' | 'center' | 'bottom' = 'bottom'): Promise<void> {
    try {
      await Toast.show({
        text: message,
        duration: 'short',
        position
      });
    } catch (error) {
      console.log(message); // Fallback to console
    }
  }
}

// QR Code Scanner for website authentication
class QRCodeScanner {
  private apiClient: MobileAPIClient;
  private isScanning = false;

  constructor(apiClient: MobileAPIClient) {
    this.apiClient = apiClient;
  }

  async startScanning(): Promise<string> {
    if (this.isScanning) {
      throw new Error('Already scanning');
    }

    this.isScanning = true;

    try {
      // Use Capacitor Camera plugin for QR scanning
      if (!window.BarcodeScanner) {
        throw new Error('QR Scanner not available');
      }

      const result = await window.BarcodeScanner.startScan();
      
      if (result.hasContent) {
        return result.content; // Return raw QR content for processing
      } else {
        throw new Error('No QR code detected');
      }
    } finally {
      this.isScanning = false;
    }
  }

  async authenticateWithWebsite(qrData: string, userEmail: string, userProducts: string[]): Promise<boolean> {
    try {
      const response = await this.apiClient.makeAPICall('/api/mobile/scan-qr', 'POST', {
        qr_data: qrData,
        user_email: userEmail,
        user_products: userProducts
      });

      if (response.success) {
        await this.showToast(`Website authenticated for ${userEmail}`, 'center');
        return true;
      } else {
        await this.showToast(response.error || 'Authentication failed', 'center');
        return false;
      }
    } catch (error) {
      console.error('Website authentication failed:', error);
      await this.showToast('Network error during authentication', 'center');
      return false;
    }
  }

  private async showToast(message: string, position: 'top' | 'center' | 'bottom' = 'bottom'): Promise<void> {
    try {
      if (window.Capacitor && window.Capacitor.Plugins.Toast) {
        await window.Capacitor.Plugins.Toast.show({
          text: message,
          duration: 'short',
          position: position
        });
      } else {
        console.log(`Toast: ${message}`);
      }
    } catch (error) {
      console.log(`Toast fallback: ${message}`);
    }
  }
}

// Main Application Class
class IELTSGenAIPrepApp {
  private apiClient: MobileAPIClient;
  private purchaseManager: iOSPurchaseManager;
  private qrScanner: QRCodeScanner;
  private currentUser: any = null;

  constructor() {
    this.apiClient = new MobileAPIClient();
    this.purchaseManager = new iOSPurchaseManager(this.apiClient);
    this.qrScanner = new QRCodeScanner(this.apiClient);
  }

  async initialize(): Promise<void> {
    try {
      // Initialize all components
      await this.purchaseManager.initializePurchases();
      
      // Set up the home screen UI
      this.setupHomeScreen();
      
      // Set up app state listeners
      App.addListener('appStateChange', ({ isActive }) => {
        if (isActive) {
          this.handleAppResume();
        }
      });

      // Set up network listeners
      Network.addListener('networkStatusChange', (status) => {
        if (!status.connected) {
          this.showOfflineMessage();
        }
      });

      console.log('IELTS GenAI Prep app initialized successfully');
    } catch (error) {
      console.error('App initialization failed:', error);
      throw error;
    }
  }

  private setupHomeScreen(): void {
    const homeContainer = document.getElementById('home-screen') || document.body;
    
    const homeScreenHTML = `
      <div id="ielts-home-screen" style="padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <!-- Top Half: Web Version Access Information -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 16px; margin-bottom: 20px; text-align: center;">
          <div style="font-size: 24px; font-weight: bold; margin-bottom: 12px;">
            📱 ➜ 💻 Access Anywhere
          </div>
          <div style="font-size: 16px; line-height: 1.5; margin-bottom: 16px;">
            Use your mobile purchases on desktop and laptop too!
          </div>
          <div style="background: rgba(255,255,255,0.2); padding: 16px; border-radius: 12px; margin-bottom: 16px;">
            <div style="font-size: 14px; margin-bottom: 8px;">
              <strong>After purchasing assessments:</strong>
            </div>
            <div style="font-size: 14px; line-height: 1.4;">
              1. Get your QR code from the purchase confirmation<br>
              2. Visit <strong>ieltsaiprep.com</strong> on your computer<br>
              3. Scan the QR code to access your assessments
            </div>
          </div>
          <button id="learn-more-web-access" style="background: white; color: #667eea; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; font-size: 14px;">
            Learn More About Web Access
          </button>
        </div>

        <!-- Assessment Products Section -->
        <div style="margin-bottom: 20px;">
          <h2 style="font-size: 20px; font-weight: bold; color: #333; margin-bottom: 16px;">
            IELTS Assessment Products
          </h2>
          <div style="display: grid; gap: 12px;">
            ${this.generateProductCards()}
          </div>
        </div>

        <!-- QR Scanner Section -->
        <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; text-align: center;">
          <h3 style="font-size: 18px; color: #333; margin-bottom: 12px;">
            Already have web access?
          </h3>
          <p style="font-size: 14px; color: #666; margin-bottom: 16px;">
            Scan QR codes from ieltsaiprep.com to authenticate
          </p>
          <button id="qr-scan-button" style="background: #28a745; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;">
            Scan QR Code
          </button>
        </div>
      </div>
    `;
    
    homeContainer.innerHTML = homeScreenHTML;
    
    // Set up event listeners
    this.setupHomeScreenListeners();
  }

  private generateProductCards(): string {
    const products = [
      {
        id: 'academic_speaking_assessment',
        title: 'Academic Speaking',
        description: 'AI-powered speaking assessment with Maya examiner',
        price: '$36.00'
      },
      {
        id: 'academic_writing_assessment', 
        title: 'Academic Writing',
        description: 'Comprehensive writing evaluation and feedback',
        price: '$36.00'
      },
      {
        id: 'general_speaking_assessment',
        title: 'General Speaking',
        description: 'General IELTS speaking practice and assessment',
        price: '$36.00'
      },
      {
        id: 'general_writing_assessment',
        title: 'General Writing',
        description: 'General IELTS writing tasks and evaluation',
        price: '$36.00'
      }
    ];

    return products.map(product => `
      <div style="background: white; border: 1px solid #e9ecef; border-radius: 12px; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <div style="flex: 1;">
            <h4 style="font-size: 16px; font-weight: 600; color: #333; margin: 0 0 8px 0;">
              ${product.title}
            </h4>
            <p style="font-size: 14px; color: #666; margin: 0 0 12px 0;">
              ${product.description}
            </p>
            <div style="font-size: 18px; font-weight: bold; color: #007bff;">
              ${product.price}
            </div>
          </div>
          <button class="purchase-btn" data-product="${product.id}" style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 14px; font-weight: 500; margin-left: 12px;">
            Purchase
          </button>
        </div>
      </div>
    `).join('');
  }

  private setupHomeScreenListeners(): void {
    // Learn more about web access
    const learnMoreBtn = document.getElementById('learn-more-web-access');
    if (learnMoreBtn) {
      learnMoreBtn.addEventListener('click', () => {
        this.showWebAccessInfo();
      });
    }

    // QR scanner button
    const qrScanBtn = document.getElementById('qr-scan-button');
    if (qrScanBtn) {
      qrScanBtn.addEventListener('click', () => {
        this.handleQRScan();
      });
    }

    // Purchase buttons
    const purchaseBtns = document.querySelectorAll('.purchase-btn');
    purchaseBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const productId = (e.target as HTMLElement).getAttribute('data-product');
        if (productId) {
          this.handlePurchase(productId);
        }
      });
    });
  }

  private async showWebAccessInfo(): Promise<void> {
    const modal = document.createElement('div');
    modal.innerHTML = `
      <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 20px;">
        <div style="background: white; border-radius: 16px; padding: 24px; max-width: 400px; width: 100%; max-height: 80vh; overflow-y: auto;">
          <h3 style="font-size: 20px; font-weight: bold; color: #333; margin: 0 0 16px 0; text-align: center;">
            🖥️ Web Access Guide
          </h3>
          
          <div style="margin-bottom: 20px;">
            <h4 style="font-size: 16px; font-weight: 600; color: #333; margin: 0 0 8px 0;">
              How it works:
            </h4>
            <ol style="font-size: 14px; line-height: 1.6; color: #666; padding-left: 20px;">
              <li>Purchase any assessment product in this mobile app</li>
              <li>After successful purchase, you'll receive a QR code</li>
              <li>Go to <strong>ieltsaiprep.com</strong> on your desktop or laptop</li>
              <li>Scan the QR code with this mobile app</li>
              <li>Access your purchased assessments on the web platform</li>
            </ol>
          </div>

          <div style="background: #e3f2fd; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
            <h4 style="font-size: 14px; font-weight: 600; color: #1976d2; margin: 0 0 8px 0;">
              ✨ Benefits of Web Access:
            </h4>
            <ul style="font-size: 13px; line-height: 1.5; color: #1976d2; margin: 0; padding-left: 16px;">
              <li>Larger screen for writing assessments</li>
              <li>Full keyboard support</li>
              <li>Better audio quality for speaking tests</li>
              <li>Seamless sync between mobile and web</li>
            </ul>
          </div>

          <div style="text-align: center;">
            <button id="close-web-info" style="background: #007bff; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;">
              Got it!
            </button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    const closeBtn = modal.querySelector('#close-web-info');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        modal.remove();
      });
    }

    // Close on backdrop click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
  }

  async handlePurchase(productId: string): Promise<void> {
    if (!this.currentUser) {
      throw new Error('User must be logged in to make purchases');
    }

    try {
      const result = await this.purchaseManager.purchaseProduct(
        productId,
        this.currentUser.email
      );

      if (result.success) {
        // Update user's purchased products
        this.currentUser.purchasedProducts = this.currentUser.purchasedProducts || [];
        this.currentUser.purchasedProducts.push(productId);
        
        // Store updated user data
        await this.saveUserData();
      }
    } catch (error) {
      console.error('Purchase handling failed:', error);
      throw error;
    }
  }

  async handleQRScan(): Promise<void> {
    try {
      // Check if user is logged in and has purchases
      if (!this.currentUser?.email) {
        await Toast.show({
          text: 'Please log in first to authenticate with website',
          duration: 'long',
          position: 'center'
        });
        return;
      }

      // Get user's purchased products
      const userProducts = this.currentUser.products || [];
      if (userProducts.length === 0) {
        await Toast.show({
          text: 'No purchased products found. Please make a purchase first.',
          duration: 'long',
          position: 'center'
        });
        return;
      }

      // Start scanning
      const qrData = await this.qrScanner.startScanning();
      
      // Authenticate with website using user's products
      const success = await this.qrScanner.authenticateWithWebsite(
        qrData,
        this.currentUser.email,
        userProducts
      );

      if (success) {
        await Toast.show({
          text: 'Website authenticated! You can now access your assessments on ieltsaiprep.com',
          duration: 'long',
          position: 'center'
        });
      } else {
        throw new Error('Authentication failed');
      }
    } catch (error) {
      await Toast.show({
        text: `QR authentication failed: ${error.message}`,
        duration: 'long',
        position: 'center'
      });
    }
  }

  private async handleAppResume(): Promise<void> {
    // Check for restored purchases
    try {
      const restoredTransactions = await this.purchaseManager.restorePurchases();
      if (restoredTransactions.length > 0) {
        console.log(`Restored ${restoredTransactions.length} purchases`);
      }
    } catch (error) {
      console.error('Failed to restore purchases:', error);
    }
  }

  private async showOfflineMessage(): Promise<void> {
    await Toast.show({
      text: 'You are offline. Some features may not be available.',
      duration: 'long',
      position: 'top'
    });
  }

  private async saveUserData(): Promise<void> {
    try {
      localStorage.setItem('ielts_user_data', JSON.stringify(this.currentUser));
    } catch (error) {
      console.error('Failed to save user data:', error);
    }
  }

  async loadUserData(): Promise<void> {
    try {
      const userData = localStorage.getItem('ielts_user_data');
      if (userData) {
        this.currentUser = JSON.parse(userData);
      }
    } catch (error) {
      console.error('Failed to load user data:', error);
    }
  }
}

// Export for global use
declare global {
  interface Window {
    IELTSGenAIPrepApp: typeof IELTSGenAIPrepApp;
    StoreKit: any;
    BarcodeScanner: any;
  }
}

window.IELTSGenAIPrepApp = IELTSGenAIPrepApp;

export { IELTSGenAIPrepApp, MobileAPIClient, iOSPurchaseManager, QRCodeScanner };