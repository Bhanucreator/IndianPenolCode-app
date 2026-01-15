# IPC Chatbot - Mobile App

A React Native + Expo mobile application for the Indian Penal Code Chatbot.

## 📱 Features

- Beautiful, modern chat interface
- Real-time communication with the Flask backend
- Cross-platform (iOS, Android, Web)
- Keyboard-aware input
- Loading indicators
- Timestamps on messages

## 🚀 Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Expo CLI
- Expo Go app on your phone (for testing)

### Installation

1. Navigate to the mobile-app directory:
```bash
cd mobile-app
```

2. Install dependencies:
```bash
npm install
```

3. Start the Expo development server:
```bash
npx expo start
```

4. Scan the QR code with:
   - **iOS**: Camera app
   - **Android**: Expo Go app

## ⚙️ Configuration

Before running the app, update the `API_URL` in `App.js`:

```javascript
// For production (deployed backend)
const API_URL = 'https://your-backend-url.onrender.com';

// For local testing (replace with your computer's IP)
const API_URL = 'http://192.168.1.100:5000';
```

To find your local IP:
- **Windows**: Run `ipconfig` in Command Prompt
- **Mac/Linux**: Run `ifconfig` in Terminal

## 📦 Building for Production

### Using EAS Build (Recommended)

1. Install EAS CLI:
```bash
npm install -g eas-cli
```

2. Login to Expo:
```bash
eas login
```

3. Configure build:
```bash
eas build:configure
```

4. Build for Android:
```bash
eas build --platform android
```

5. Build for iOS:
```bash
eas build --platform ios
```

### Publishing to App Stores

- **Google Play Store**: Use the `.aab` file from EAS Build
- **Apple App Store**: Use EAS Submit or Transporter app

## 🎨 Customization

### Change Colors

Edit the color values in `App.js` styles:
- Primary color: `#4A90E2`
- Background: `#F5F7FA`

### Add App Icons

Replace placeholder images in `assets/` folder:
- `icon.png` - App icon (1024x1024)
- `splash.png` - Splash screen (1284x2778)
- `adaptive-icon.png` - Android adaptive icon (1024x1024)
- `favicon.png` - Web favicon (48x48)

## 🐛 Troubleshooting

### Network Error
- Ensure your phone and computer are on the same WiFi
- Check if the backend server is running
- Verify the API_URL is correct

### Build Errors
```bash
npx expo doctor
```

### Clear Cache
```bash
npx expo start --clear
```
