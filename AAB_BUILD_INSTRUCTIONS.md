# AAB Build Instructions for Google Play Store

## Current Status
✅ Android Studio project loaded
✅ Project structure verified
🔄 Gradle sync in progress
⏳ Waiting for sync completion

## Next Steps After Gradle Sync Completes

### 1. Start AAB Build Process
- **Menu:** Build → Generate Signed Bundle / APK...
- **Select:** Android App Bundle (AAB)
- **Click:** Next

### 2. Create New Keystore (Digital Signature)
- **Click:** Create new...
- **Keystore path:** Choose location (e.g., Desktop/ielts-keystore.jks)
- **Keystore password:** Choose strong password (SAVE THIS!)
- **Key alias:** com.ielts.app
- **Key password:** Same as keystore password (recommended)

### 3. Certificate Information
- **First and Last Name:** Your name
- **Organizational Unit:** IELTS GenAI Prep
- **Organization:** Your company name
- **City/Locality:** Your city
- **State/Province:** Your state
- **Country Code:** Your country (e.g., US, CA, UK)

### 4. Build Configuration
- **Build Variant:** release
- **Destination Folder:** Choose where to save AAB file
- **Click:** Create

### 5. AAB File Location
After successful build, you'll find:
- **File:** app-release.aab
- **Location:** android/app/build/outputs/bundle/release/
- **Size:** Approximately 2-5 MB

### 6. Upload to Google Play Console
- **Go to:** Google Play Console
- **Navigate to:** App releases → Production
- **Click:** Create new release
- **Upload:** app-release.aab file
- **Complete:** Store listing information

## Important Notes
- **Save keystore file safely** - needed for all future updates
- **Record all passwords** - cannot be recovered if lost
- **AAB format required** - Google Play no longer accepts APK files for new apps
- **First build takes longest** - subsequent builds are faster

## Troubleshooting
- If build fails, check Build tab at bottom of Android Studio
- Ensure internet connection for dependency downloads
- Gradle sync must complete before building