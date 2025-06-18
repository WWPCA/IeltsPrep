# Apple Developer - Step by Step Deployment Guide

## Step 1: Create New App in App Store Connect

Based on your screenshot, fill out the "New App" form with these exact values:

### Platforms
✅ **Check iOS** (leave others unchecked)

### Name
```
IELTS GenAI Prep
```

### Primary Language
```
English (U.S.)
```

### Bundle ID
You need to register a new Bundle ID first. Click "Register a new bundle ID in Certificates, Identifiers & Profiles"

**Bundle ID to register:**
```
com.ieltsgenaiprep.app
```
**Description:** IELTS GenAI Prep Application

### SKU (Stock Keeping Unit)
```
ielts-genai-prep-ios-2025
```

### User Access
✅ **Select "Full Access"**

Click **"Create"** when done.

## Step 2: After App Creation

Once your app is created, you'll need to configure:

### App Information
- **Category:** Education
- **Subcategory:** Language Learning
- **Content Rights:** No, this app does not use third-party content

### Pricing and Availability
- **Price:** Free
- **Availability:** All countries/regions

### App Privacy
- **Privacy Policy URL:** 
```
https://ieltsaiprep.com/privacy-policy
```

### In-App Purchases (Create 4 products)

1. **Academic Writing Assessment**
   - Product ID: `com.ieltsgenaiprep.academic.writing`
   - Reference Name: Academic Writing Assessment
   - Type: Non-Consumable
   - Price: $36.00 USD

2. **General Writing Assessment**
   - Product ID: `com.ieltsgenaiprep.general.writing`
   - Reference Name: General Writing Assessment
   - Type: Non-Consumable
   - Price: $36.00 USD

3. **Academic Speaking Assessment**
   - Product ID: `com.ieltsgenaiprep.academic.speaking`
   - Reference Name: Academic Speaking Assessment
   - Type: Non-Consumable
   - Price: $36.00 USD

4. **General Speaking Assessment**
   - Product ID: `com.ieltsgenaiprep.general.speaking`
   - Reference Name: General Speaking Assessment
   - Type: Non-Consumable
   - Price: $36.00 USD

## Step 3: Build and Upload from Xcode

After App Store Connect setup:

1. **Run the deployment script:**
```bash
./deploy-mobile-app.sh
```

2. **In Xcode (when it opens):**
   - Select "Any iOS Device" as target
   - Go to Product → Archive
   - Wait for build to complete
   - Click "Distribute App"
   - Select "App Store Connect"
   - Upload your app

## Step 4: Submit for Review

Back in App Store Connect:
- Add app screenshots
- Write app description (provided in APP_STORE_SUBMISSION_CHECKLIST.md)
- Submit for review

**Expected review time:** 24-48 hours

Your app will then be live on the App Store!