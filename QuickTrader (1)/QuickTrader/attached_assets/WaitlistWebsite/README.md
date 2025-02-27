# Velasa Trading - Android App
A JRP GROUPS OF INDUSTRIES Company

## Overview
Velasa Trading is a premium trading platform that offers real-time market data, sentiment analysis, and portfolio management capabilities.

## Building the Android App

### Prerequisites
1. Android Studio
2. Java Development Kit (JDK) 11 or newer
3. Node.js and npm
4. Capacitor (for wrapping Streamlit as native app)

### Build Instructions

1. Install Dependencies:
```bash
npm install @capacitor/core @capacitor/android
npx cap init
```

2. Build the Streamlit app:
```bash
streamlit build
```

3. Add Android platform:
```bash
npx cap add android
```

4. Configure Android app settings in `android/app.json`

5. Generate app icons and splash screens:
   - Place your icon in `android/app/src/main/res/mipmap`
   - Update splash screen in `android/app/src/main/res/drawable`

### Google Play Store Submission

1. Generate signed APK:
   - Open project in Android Studio
   - Build > Generate Signed Bundle/APK
   - Follow the signing wizard

2. Play Store Requirements:
   - App icon (512x512 PNG)
   - Feature graphic (1024x500 PNG)
   - Screenshots (at least 2)
   - Privacy policy
   - Content rating questionnaire
   - App description
   - Release notes

3. Required Permissions:
   - Internet access
   - Camera (for document verification)

## App Details

- Package Name: com.jrpgroups.velasa
- Min SDK: Android 5.0 (API 21)
- Target SDK: Android 13 (API 33)
- Version: 1.0.0

## Assets Required
- App Icon (multiple sizes)
- Splash Screen
- Feature Graphics
- Screenshots
- Promotional Materials

## Support
For technical support, contact JRP GROUPS OF INDUSTRIES technical team.
