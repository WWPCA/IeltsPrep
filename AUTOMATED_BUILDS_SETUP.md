# Automated APK/IPA Generation Setup

This repository is configured for automated Android APK and iOS IPA generation using GitHub Actions workflows.

## 🚀 Quick Start

1. **Set up repository secrets** (see below)
2. **Push to main branch** or **manually trigger workflows**
3. **Download built APK/IPA** from Actions artifacts or releases

## 📱 Build Triggers

### Automatic Builds
- **Push to `main`**: Creates release builds with signed APK/IPA
- **Push to `develop`**: Creates debug builds
- **Pull Requests**: Creates debug builds for testing

### Manual Builds
- Go to **Actions** → **Build Android APK** or **Build iOS IPA**
- Click **Run workflow**
- Choose **debug** or **release** build type

## 🔐 Repository Secrets Setup

### Required Android Secrets

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `ANDROID_KEYSTORE_BASE64` | Base64 encoded keystore file | `base64 -i your-release-key.keystore` |
| `ANDROID_KEYSTORE_PASSWORD` | Keystore password | From your keystore creation |
| `ANDROID_KEY_ALIAS` | Key alias name | From your keystore creation |
| `ANDROID_KEY_PASSWORD` | Key password | From your keystore creation |

### Required iOS Secrets

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `IOS_CERTIFICATE_BASE64` | Base64 encoded .p12 certificate | `base64 -i certificate.p12` |
| `IOS_CERTIFICATE_PASSWORD` | Certificate password | From certificate export |
| `IOS_PROVISIONING_PROFILE_BASE64` | Base64 encoded provisioning profile | `base64 -i profile.mobileprovision` |
| `IOS_PROVISIONING_PROFILE_NAME` | Provisioning profile name | From Apple Developer Console |
| `IOS_CODE_SIGN_IDENTITY` | Code signing identity | Usually "iPhone Distribution: [Company Name]" |
| `IOS_TEAM_ID` | Apple Developer Team ID | From Apple Developer Console |

## 📋 How to Add Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name from the tables above

## 🔨 Android Keystore Generation

If you don't have an Android keystore:

```bash
keytool -genkey -v -keystore release-key.keystore -alias release -keyalg RSA -keysize 2048 -validity 10000
```

Then convert to base64:
```bash
base64 -i release-key.keystore
```

## 🍎 iOS Certificate Setup

### 1. Create App ID
- Go to Apple Developer Console
- Create App ID: `com.ieltsgenaiprep.app`

### 2. Create Distribution Certificate
- Generate Certificate Signing Request (CSR)
- Create iOS Distribution certificate
- Download and install in Keychain

### 3. Create Provisioning Profile
- Create App Store provisioning profile
- Link to your App ID and certificate
- Download the `.mobileprovision` file

### 4. Export Certificate
```bash
# Export from Keychain as .p12 file
# Convert to base64
base64 -i certificate.p12
```

## 📁 Build Outputs

### Android APK Locations
- **Debug**: `android/app/build/outputs/apk/debug/app-debug.apk`
- **Release**: `android/app/build/outputs/apk/release/app-release.apk`

### iOS IPA Locations
- **Debug**: `ios/App.xcarchive` (Xcode archive)
- **Release**: `ios/export/*.ipa`

## 📦 Downloads

### From Artifacts (All builds)
1. Go to **Actions** → **Recent workflow run**
2. Scroll down to **Artifacts**
3. Download APK/IPA zip files

### From Releases (Main branch only)
1. Go to **Releases** section
2. Download attached APK/IPA files
3. Automatic versioning: `v{run_number}`

## 🔧 Troubleshooting

### Android Build Fails
- Check keystore secrets are correctly base64 encoded
- Verify keystore passwords match
- Ensure Android SDK versions are compatible

### iOS Build Fails
- Verify certificate is valid and not expired
- Check provisioning profile matches the App ID
- Ensure Team ID is correct
- Confirm certificate and profile are properly base64 encoded

### Web Assets Missing
- Workflows automatically copy from `templates/` to `static/`
- Ensure your web assets are in the correct directories

## 🎯 Workflow Features

- ✅ **Multi-platform**: Android APK + iOS IPA
- ✅ **Flexible triggers**: Push, PR, manual
- ✅ **Debug/Release builds**: Configurable build types
- ✅ **Artifact storage**: 30 days (debug), 90 days (release)
- ✅ **Automatic releases**: Tagged releases for main branch
- ✅ **Secure signing**: Encrypted certificates and keys
- ✅ **Build caching**: Faster subsequent builds

## 🚀 Next Steps

1. **Set up secrets** using the tables above
2. **Test build** by pushing to `develop` branch
3. **Create release** by pushing to `main` branch
4. **Configure app stores** for distribution

Your IELTS GenAI Prep app is now ready for automated builds! 🎉