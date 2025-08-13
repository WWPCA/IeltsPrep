# Complete Mobile App Development Guide

## Project Setup and Architecture

### Initial Setup
```bash
# Create new Ionic/Capacitor project
npm install -g @ionic/cli @capacitor/cli
ionic start ielts-genai-prep tabs --type=angular --capacitor

cd ielts-genai-prep
npm install @capacitor/android @capacitor/ios @capacitor/camera @capacitor/storage @capacitor/network

# Install additional dependencies
npm install @ionic/angular @angular/common @angular/core @angular/forms
npm install @angular/router @ionic/storage-angular
npm install qrcode-generator jsqr @capacitor-community/barcode-scanner
```

### Capacitor Configuration
```typescript
// capacitor.config.ts
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.ieltsaiprep.app',
  appName: 'IELTS GenAI Prep',
  webDir: 'dist',
  bundledWebRuntime: false,
  server: {
    androidScheme: 'https'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 3000,
      backgroundColor: "#663399",
      showSpinner: false
    },
    PushNotifications: {
      presentationOptions: ["badge", "sound", "alert"]
    },
    LocalNotifications: {
      smallIcon: "ic_stat_icon_config_sample",
      iconColor: "#663399"
    },
    Camera: {
      permissions: {
        camera: "To scan QR codes for web platform access"
      }
    },
    Microphone: {
      permissions: {
        microphone: "To record speaking assessments with Maya AI"
      }
    }
  },
  android: {
    allowMixedContent: true,
    captureInput: true,
    webContentsDebuggingEnabled: false
  },
  ios: {
    scheme: "IELTS GenAI Prep",
    contentInset: "automatic"
  }
};

export default config;
```

## Core App Structure

### App Module (app.module.ts)
```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouteReuseStrategy } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { IonicModule, IonicRouteStrategy } from '@ionic/angular';
import { IonicStorageModule } from '@ionic/storage-angular';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

// Services
import { AuthService } from './services/auth.service';
import { AssessmentService } from './services/assessment.service';
import { PurchaseService } from './services/purchase.service';
import { QRService } from './services/qr.service';
import { StorageService } from './services/storage.service';

@NgModule({
  declarations: [AppComponent],
  imports: [
    BrowserModule, 
    IonicModule.forRoot(), 
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    IonicStorageModule.forRoot()
  ],
  providers: [
    { provide: RouteReuseStrategy, useClass: IonicRouteStrategy },
    AuthService,
    AssessmentService,
    PurchaseService,
    QRService,
    StorageService
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
```

### App Routing (app-routing.module.ts)
```typescript
import { NgModule } from '@angular/core';
import { PreloadAllModules, RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

const routes: Routes = [
  {
    path: '',
    redirectTo: '/welcome',
    pathMatch: 'full'
  },
  {
    path: 'welcome',
    loadChildren: () => import('./pages/welcome/welcome.module').then(m => m.WelcomePageModule)
  },
  {
    path: 'login',
    loadChildren: () => import('./pages/login/login.module').then(m => m.LoginPageModule)
  },
  {
    path: 'register',
    loadChildren: () => import('./pages/register/register.module').then(m => m.RegisterPageModule)
  },
  {
    path: 'dashboard',
    loadChildren: () => import('./pages/dashboard/dashboard.module').then(m => m.DashboardPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'assessments',
    loadChildren: () => import('./pages/assessments/assessments.module').then(m => m.AssessmentsPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'purchase',
    loadChildren: () => import('./pages/purchase/purchase.module').then(m => m.PurchasePageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'qr-login',
    loadChildren: () => import('./pages/qr-login/qr-login.module').then(m => m.QrLoginPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'profile',
    loadChildren: () => import('./pages/profile/profile.module').then(m => m.ProfilePageModule),
    canActivate: [AuthGuard]
  }
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, { preloadingStrategy: PreloadAllModules })
  ],
  exports: [RouterModule]
})
export class AppRoutingModule {}
```

## Core Services

### Authentication Service
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { Storage } from '@ionic/storage-angular';

export interface User {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  purchased_assessments: string[];
  assessment_attempts: {
    academic_writing: number;
    general_writing: number;
    academic_speaking: number;
    general_speaking: number;
  };
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'https://www.ieltsaiprep.com/api';
  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser: Observable<User | null>;

  constructor(
    private http: HttpClient,
    private storage: Storage
  ) {
    this.currentUserSubject = new BehaviorSubject<User | null>(null);
    this.currentUser = this.currentUserSubject.asObservable();
    this.initStorage();
  }

  async initStorage() {
    await this.storage.create();
    const user = await this.storage.get('currentUser');
    if (user) {
      this.currentUserSubject.next(user);
    }
  }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, userData)
      .pipe(map(response => {
        if (response['success']) {
          this.setCurrentUser(response['user']);
        }
        return response;
      }));
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, { email, password })
      .pipe(map(response => {
        if (response['success']) {
          this.setCurrentUser(response['user']);
        }
        return response;
      }));
  }

  logout(): Observable<any> {
    return this.http.post(`${this.apiUrl}/logout`, {})
      .pipe(map(response => {
        this.clearCurrentUser();
        return response;
      }));
  }

  private async setCurrentUser(user: User) {
    this.currentUserSubject.next(user);
    await this.storage.set('currentUser', user);
  }

  private async clearCurrentUser() {
    this.currentUserSubject.next(null);
    await this.storage.remove('currentUser');
  }

  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  isAuthenticated(): boolean {
    return this.currentUserValue !== null;
  }
}
```

### Purchase Service (In-App Purchases)
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Platform } from '@ionic/angular';
import { Observable } from 'rxjs';

// Import Capacitor plugins for purchases
declare var cordova: any;

@Injectable({
  providedIn: 'root'
})
export class PurchaseService {
  private apiUrl = 'https://www.ieltsaiprep.com/api';
  
  constructor(
    private http: HttpClient,
    private platform: Platform
  ) {}

  async initializePurchases() {
    if (this.platform.is('cordova')) {
      if (this.platform.is('ios')) {
        await this.initializeIosPurchases();
      } else if (this.platform.is('android')) {
        await this.initializeAndroidPurchases();
      }
    }
  }

  private async initializeIosPurchases() {
    // Initialize iOS In-App Purchase
    const products = [
      'academic_writing_assessment',
      'general_writing_assessment',
      'academic_speaking_assessment',
      'general_speaking_assessment'
    ];

    // Configure store with product IDs
    cordova.plugins.purchase.store.register([
      {
        id: 'academic_writing_assessment',
        type: cordova.plugins.purchase.store.CONSUMABLE,
        alias: 'Academic Writing Assessment'
      },
      {
        id: 'general_writing_assessment', 
        type: cordova.plugins.purchase.store.CONSUMABLE,
        alias: 'General Writing Assessment'
      },
      {
        id: 'academic_speaking_assessment',
        type: cordova.plugins.purchase.store.CONSUMABLE,
        alias: 'Academic Speaking Assessment'
      },
      {
        id: 'general_speaking_assessment',
        type: cordova.plugins.purchase.store.CONSUMABLE,
        alias: 'General Speaking Assessment'
      }
    ]);

    // Set up purchase handlers
    cordova.plugins.purchase.store.when('product').updated((product) => {
      console.log('Product updated:', product);
    });

    cordova.plugins.purchase.store.when('product').approved((product) => {
      this.validatePurchase(product);
    });

    cordova.plugins.purchase.store.ready(() => {
      console.log('Store ready');
    });

    cordova.plugins.purchase.store.refresh();
  }

  private async initializeAndroidPurchases() {
    // Initialize Google Play Billing
    // Similar setup for Android purchases
  }

  purchaseAssessment(productId: string): Promise<any> {
    return new Promise((resolve, reject) => {
      if (this.platform.is('cordova')) {
        cordova.plugins.purchase.store.order(productId)
          .then(resolve)
          .catch(reject);
      } else {
        // Mock purchase for testing
        resolve({ success: true, productId });
      }
    });
  }

  private validatePurchase(product: any): Observable<any> {
    const purchaseData = {
      product_id: product.id,
      transaction_id: product.transaction.id,
      receipt_data: product.transaction.appStoreReceipt || product.transaction.purchaseToken,
      platform: this.platform.is('ios') ? 'ios' : 'android'
    };

    return this.http.post(`${this.apiUrl}/validate-purchase`, purchaseData);
  }

  getProducts(): Observable<any> {
    return this.http.get(`${this.apiUrl}/products`);
  }

  getPurchaseHistory(): Observable<any> {
    return this.http.get(`${this.apiUrl}/purchase-history`);
  }
}
```

### QR Code Service
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BarcodeScanner } from '@capacitor-community/barcode-scanner';
import { Observable } from 'rxjs';
import * as QRCode from 'qrcode-generator';

@Injectable({
  providedIn: 'root'
})
export class QRService {
  private apiUrl = 'https://www.ieltsaiprep.com/api';

  constructor(private http: HttpClient) {}

  generateQRCode(userId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/generate-qr`, { user_id: userId });
  }

  createQRCodeImage(data: string): string {
    const qr = QRCode(0, 'H');
    qr.addData(data);
    qr.make();
    return qr.createDataURL(8);
  }

  async scanQRCode(): Promise<string | null> {
    try {
      // Check camera permission
      await BarcodeScanner.checkPermission({ force: true });

      // Hide background
      BarcodeScanner.hideBackground();

      const result = await BarcodeScanner.startScan();

      if (result.hasContent) {
        return result.content;
      }
      return null;
    } catch (error) {
      console.error('QR scan error:', error);
      return null;
    } finally {
      BarcodeScanner.showBackground();
      BarcodeScanner.stopScan();
    }
  }

  verifyQRCode(qrData: string, deviceFingerprint: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/verify-qr`, {
      qr_code_id: qrData,
      device_fingerprint: deviceFingerprint
    });
  }
}
```

## Key Pages Implementation

### Dashboard Page
```typescript
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService, User } from '../services/auth.service';
import { PurchaseService } from '../services/purchase.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.page.html',
  styleUrls: ['./dashboard.page.scss'],
})
export class DashboardPage implements OnInit {
  user: User | null = null;
  assessmentProducts: any[] = [];

  constructor(
    private authService: AuthService,
    private purchaseService: PurchaseService,
    private router: Router
  ) {}

  ngOnInit() {
    this.authService.currentUser.subscribe(user => {
      this.user = user;
    });
    
    this.loadProducts();
  }

  loadProducts() {
    this.purchaseService.getProducts().subscribe(
      response => {
        this.assessmentProducts = response.products;
      },
      error => {
        console.error('Error loading products:', error);
      }
    );
  }

  canAccessAssessment(assessmentType: string): boolean {
    if (!this.user) return false;
    return this.user.purchased_assessments.includes(assessmentType) &&
           this.user.assessment_attempts[assessmentType] > 0;
  }

  navigateToAssessment(assessmentType: string) {
    if (this.canAccessAssessment(assessmentType)) {
      this.router.navigate(['/assessments', assessmentType]);
    } else {
      this.router.navigate(['/purchase'], { 
        queryParams: { product: assessmentType } 
      });
    }
  }

  navigateToQRLogin() {
    this.router.navigate(['/qr-login']);
  }

  navigateToProfile() {
    this.router.navigate(['/profile']);
  }
}
```

### QR Login Page
```typescript
import { Component, OnInit } from '@angular/core';
import { LoadingController, AlertController, ToastController } from '@ionic/angular';
import { QRService } from '../services/qr.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-qr-login',
  templateUrl: './qr-login.page.html',
  styleUrls: ['./qr-login.page.scss'],
})
export class QrLoginPage implements OnInit {
  qrCodeImage: string = '';
  isGenerating: boolean = false;

  constructor(
    private qrService: QRService,
    private authService: AuthService,
    private loadingController: LoadingController,
    private alertController: AlertController,
    private toastController: ToastController
  ) {}

  ngOnInit() {
    this.generateQRCode();
  }

  async generateQRCode() {
    const user = this.authService.currentUserValue;
    if (!user) return;

    this.isGenerating = true;
    const loading = await this.loadingController.create({
      message: 'Generating QR code...'
    });
    await loading.present();

    try {
      const response = await this.qrService.generateQRCode(user.user_id).toPromise();
      if (response.success) {
        const qrData = `https://www.ieltsaiprep.com/qr-login?code=${response.qr_code_id}`;
        this.qrCodeImage = this.qrService.createQRCodeImage(qrData);
        
        const toast = await this.toastController.create({
          message: 'QR code generated! Scan with your computer browser.',
          duration: 3000,
          color: 'success'
        });
        await toast.present();
      }
    } catch (error) {
      const alert = await this.alertController.create({
        header: 'Error',
        message: 'Failed to generate QR code. Please try again.',
        buttons: ['OK']
      });
      await alert.present();
    } finally {
      this.isGenerating = false;
      await loading.dismiss();
    }
  }

  async refreshQRCode() {
    await this.generateQRCode();
  }
}
```

### Purchase Page
```typescript
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { LoadingController, AlertController, ToastController } from '@ionic/angular';
import { PurchaseService } from '../services/purchase.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-purchase',
  templateUrl: './purchase.page.html',
  styleUrls: ['./purchase.page.scss'],
})
export class PurchasePage implements OnInit {
  products: any[] = [];
  selectedProduct: string = '';
  isLoading: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private purchaseService: PurchaseService,
    private authService: AuthService,
    private loadingController: LoadingController,
    private alertController: AlertController,
    private toastController: ToastController
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.selectedProduct = params['product'] || '';
    });
    
    this.loadProducts();
  }

  loadProducts() {
    this.purchaseService.getProducts().subscribe(
      response => {
        this.products = response.products;
      },
      error => {
        console.error('Error loading products:', error);
      }
    );
  }

  async purchaseProduct(productId: string) {
    this.isLoading = true;
    const loading = await this.loadingController.create({
      message: 'Processing purchase...'
    });
    await loading.present();

    try {
      const result = await this.purchaseService.purchaseAssessment(productId);
      
      if (result.success) {
        const toast = await this.toastController.create({
          message: 'Purchase successful! You can now access your assessment.',
          duration: 3000,
          color: 'success'
        });
        await toast.present();
        
        // Refresh user data
        this.authService.refreshUserData();
      }
    } catch (error) {
      const alert = await this.alertController.create({
        header: 'Purchase Failed',
        message: 'Unable to complete purchase. Please try again.',
        buttons: ['OK']
      });
      await alert.present();
    } finally {
      this.isLoading = false;
      await loading.dismiss();
    }
  }

  getProductPrice(product: any): string {
    // Return localized price based on user's region
    return product.price || '$36.49';
  }

  getProductDescription(productId: string): string {
    const descriptions = {
      'academic_writing_assessment': 'AI-powered Academic Writing assessment with TrueScore® technology',
      'general_writing_assessment': 'AI-powered General Training Writing assessment with detailed feedback',
      'academic_speaking_assessment': 'Interactive Academic Speaking assessment with Maya AI examiner',
      'general_speaking_assessment': 'Real-time General Training Speaking practice with AI evaluation'
    };
    return descriptions[productId] || 'IELTS assessment with AI-powered feedback';
  }
}
```

## Build and Deployment

### Android Build Configuration
```gradle
// android/app/build.gradle
android {
    compileSdkVersion 34
    defaultConfig {
        applicationId "com.ieltsaiprep.app"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
    }
    
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
    
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}

dependencies {
    implementation 'com.android.billingclient:billing:5.0.0'
    implementation 'androidx.appcompat:appcompat:1.4.0'
    implementation 'com.google.android.material:material:1.4.0'
}
```

### iOS Build Configuration
```xml
<!-- ios/App/App/Info.plist -->
<dict>
    <key>CFBundleIdentifier</key>
    <string>com.ieltsaiprep.app</string>
    <key>CFBundleName</key>
    <string>IELTS GenAI Prep</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>NSCameraUsageDescription</key>
    <string>This app needs camera access to scan QR codes for web platform login</string>
    <key>NSMicrophoneUsageDescription</key>
    <string>This app needs microphone access for AI-powered speaking assessments</string>
    <key>ITSAppUsesNonExemptEncryption</key>
    <false/>
</dict>
```

### Build Commands
```bash
# Build web assets
npm run build

# Sync with native platforms
npx cap sync

# Build Android APK
npx cap build android

# Build iOS (requires Xcode)
npx cap build ios

# Open in Android Studio for final build/signing
npx cap open android

# Open in Xcode for App Store submission
npx cap open ios
```

### App Store Submission Checklist

#### Android (Google Play)
- [ ] App signed with release key
- [ ] Target SDK version 34
- [ ] All required permissions declared
- [ ] In-app billing products configured
- [ ] App Bundle (.aab) generated
- [ ] Store listing completed with screenshots
- [ ] Content rating completed
- [ ] Privacy policy published
- [ ] Data safety form completed

#### iOS (App Store)
- [ ] App signed with distribution certificate
- [ ] Target iOS 14.0+
- [ ] App icons in all required sizes
- [ ] Launch screen configured
- [ ] In-app purchase products configured
- [ ] App Store Connect metadata completed
- [ ] Screenshots for all device sizes
- [ ] App Review information provided
- [ ] Export compliance information completed

This complete guide provides everything needed to build, configure, and deploy the IELTS GenAI Prep mobile application for both iOS and Android platforms.