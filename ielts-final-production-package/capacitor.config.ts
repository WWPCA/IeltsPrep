import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.ieltsaiprep.app',
  appName: 'IELTS GenAI Prep',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
    iosScheme: 'https'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#667eea',
      showSpinner: false,
      splashFullScreen: false,
      splashImmersive: false
    },
    StatusBar: {
      style: 'dark',
      backgroundColor: '#667eea'
    },
    Keyboard: {
      resize: 'body',
      style: 'dark',
      resizeOnFullScreen: true
    },
    Storage: {
      group: 'IELTS_APP_STORAGE'
    },
    Device: {
      androidId: true
    },
    Network: {
      enabled: true
    },
    GooglePay: {
      enabled: true,
      environment: 'TEST', // Change to 'PRODUCTION' for release
      merchantId: 'com.ieltsaiprep.app',
      merchantName: 'IELTS GenAI Prep'
    }
  },
  ios: {
    scheme: 'IELTS GenAI Prep',
    cordovaSwiftVersion: '5.0'
  },
  android: {
    buildOptions: {
      keystorePath: undefined,
      keystorePassword: undefined,
      keystoreAlias: undefined,
      keystoreAliasPassword: undefined,
      releaseType: 'AAB'
    }
  }
};

export default config;