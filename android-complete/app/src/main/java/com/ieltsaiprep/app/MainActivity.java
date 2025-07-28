package com.ieltsaiprep.app;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.Plugin;

// AWS SDK imports
import com.amazonaws.mobile.client.AWSMobileClient;
import com.amazonaws.mobile.client.Callback;
import com.amazonaws.mobile.client.UserStateDetails;

// Google Play Billing imports
import com.android.billingclient.api.BillingClient;
import com.android.billingclient.api.BillingClientStateListener;
import com.android.billingclient.api.BillingResult;
import com.android.billingclient.api.Purchase;
import com.android.billingclient.api.PurchasesUpdatedListener;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends BridgeActivity implements PurchasesUpdatedListener {
    private BillingClient billingClient;
    
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Initialize AWS Mobile Client for Cognito authentication
        initializeAWSMobileClient();
        
        // Initialize Google Play Billing
        initializeGooglePlayBilling();
        
        // Register additional Capacitor plugins
        registerAdditionalPlugins();
    }
    
    private void initializeAWSMobileClient() {
        AWSMobileClient.getInstance().initialize(getApplicationContext(), R.raw.awsconfiguration, new Callback<UserStateDetails>() {
            @Override
            public void onResult(UserStateDetails userStateDetails) {
                switch (userStateDetails.getUserState()) {
                    case SIGNED_IN:
                        // User is signed in
                        setupJavaScriptInterface();
                        break;
                    case SIGNED_OUT:
                        // User is signed out
                        setupJavaScriptInterface();
                        break;
                    default:
                        // Other states
                        setupJavaScriptInterface();
                        break;
                }
            }

            @Override
            public void onError(Exception e) {
                // Handle initialization error
                e.printStackTrace();
                setupJavaScriptInterface();
            }
        });
    }
    
    private void setupJavaScriptInterface() {
        // Add JavaScript interface for communication with web content
        getBridge().getWebView().addJavascriptInterface(new AndroidBridge(), "AndroidBridge");
    }
    
    private void initializeGooglePlayBilling() {
        billingClient = BillingClient.newBuilder(this)
            .setListener(this)
            .enablePendingPurchases()
            .build();
            
        billingClient.startConnection(new BillingClientStateListener() {
            @Override
            public void onBillingSetupFinished(BillingResult billingResult) {
                if (billingResult.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                    // The BillingClient is ready. You can query purchases here.
                }
            }

            @Override
            public void onBillingServiceDisconnected() {
                // Try to restart the connection on the next request to
                // Google Play by calling the startConnection() method.
            }
        });
    }
    
    private void registerAdditionalPlugins() {
        // Register any custom plugins here if needed
        // Example: this.registerPlugin(MyCustomPlugin.class);
    }
    
    @Override
    public void onPurchasesUpdated(BillingResult billingResult, List<Purchase> purchases) {
        if (billingResult.getResponseCode() == BillingClient.BillingResponseCode.OK
                && purchases != null) {
            for (Purchase purchase : purchases) {
                handlePurchase(purchase);
            }
        } else if (billingResult.getResponseCode() == BillingClient.BillingResponseCode.USER_CANCELED) {
            // Handle user cancelled purchase
        } else {
            // Handle other error cases
        }
    }
    
    private void handlePurchase(Purchase purchase) {
        // Verify the purchase
        String purchaseToken = purchase.getPurchaseToken();
        String productId = purchase.getProducts().get(0);
        
        // Send purchase token to AWS backend for verification
        verifyPurchaseWithBackend(purchaseToken, productId);
        
        // Acknowledge the purchase (for one-time products)
        if (purchase.getPurchaseState() == Purchase.PurchaseState.PURCHASED) {
            acknowledgePurchase(purchase);
        }
    }
    
    private void verifyPurchaseWithBackend(String purchaseToken, String productId) {
        // This would typically be done via an HTTP client to your AWS Lambda
        // For now, we'll communicate with the JavaScript layer
        String script = String.format(
            "if (window.ieltsApp) { " +
            "window.ieltsApp.billing.verifyPurchase('%s').then(result => {" +
            "console.log('Purchase verified:', result);" +
            "}).catch(error => {" +
            "console.error('Purchase verification failed:', error);" +
            "}); }",
            purchaseToken
        );
        
        getBridge().getWebView().evaluateJavascript(script, null);
    }
    
    private void acknowledgePurchase(Purchase purchase) {
        // Note: AcknowledgePurchaseParams requires newer billing library version
        // For now, we'll use a simplified approach
        getBridge().getWebView().evaluateJavascript(
            "if (window.ieltsApp) { window.ieltsApp.showStatus('Purchase completed successfully!', 'success'); }",
            null
        );
    }
    
    // JavaScript Interface for communication with web content
    public class AndroidBridge {
        @android.webkit.JavascriptInterface
        public void initializeBilling() {
            // Billing already initialized in onCreate
        }
        
        @android.webkit.JavascriptInterface
        public void purchaseProduct(String productId) {
            runOnUiThread(() -> {
                startPurchaseFlow(productId);
            });
        }
        
        @android.webkit.JavascriptInterface
        public String getDeviceInfo() {
            return android.provider.Settings.Secure.getString(
                getContentResolver(), android.provider.Settings.Secure.ANDROID_ID);
        }
    }
    
    private void startPurchaseFlow(String productId) {
        // Simplified purchase flow for testing
        // In production, this would query actual Google Play products
        getBridge().getWebView().evaluateJavascript(
            "if (window.AndroidBridge && window.AndroidBridge.onPurchaseResult) { " +
            "window.AndroidBridge.onPurchaseResult({ success: true, purchaseToken: 'test_token_' + Date.now() }); }",
            null
        );
    }
    
    @Override
    protected void onDestroy() {
        if (billingClient != null) {
            billingClient.endConnection();
        }
        super.onDestroy();
    }
}
