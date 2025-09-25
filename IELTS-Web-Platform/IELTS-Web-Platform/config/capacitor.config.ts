import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.ieltsaiprep.app',
  appName: 'IELTS GenAI Prep',
  webDir: 'app/src/main/assets/public',
  server: {
    androidScheme: 'https',
    iosScheme: 'https'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#6366f1',
      showSpinner: false,
      splashFullScreen: false,
      splashImmersive: false,
      androidSplashResourceName: 'splash',
      androidScaleType: 'CENTER_CROP',
      iosSpinnerStyle: 'small',
      spinnerColor: '#ffffff'
    },
    StatusBar: {
      style: 'dark',
      backgroundColor: '#6366f1'
    },
    Keyboard: {
      resize: 'body',
      style: 'dark',
      resizeOnFullScreen: true
    },
    PushNotifications: {
      presentationOptions: [
        'badge',
        'sound',
        'alert'
      ]
    },
    LocalNotifications: {
      smallIcon: 'ic_stat_icon_config_sample',
      iconColor: '#6366f1'
    }
  },
  ios: {
    scheme: 'IELTS GenAI Prep',
    cordovaSwiftVersion: '5.0',
    minVersion: '13.0',
    webContentsDebuggingEnabled: true
  },
  android: {
    minWebViewVersion: 60,
    webContentsDebuggingEnabled: true
  }
};

export default config;