# IPC Chatbot - Full Stack Application

A comprehensive chatbot application for querying the Indian Penal Code 1860, featuring both web and mobile interfaces.

## 📁 Project Structure

```
GenAIProject/
├── app.py                 # Flask backend API
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys)
├── .gitignore            # Git ignore file
├── Procfile              # Heroku/Render deployment
├── THE-INDIAN-PENAL-CODE-1860.pdf  # Source PDF
├── templates/
│   └── index.html        # Web frontend
├── static/
│   ├── style.css         # Web styling
│   └── script.js         # Web JavaScript
└── mobile-app/           # React Native Expo app
    ├── App.js            # Main mobile app
    ├── package.json      # Node dependencies
    ├── app.json          # Expo configuration
    └── assets/           # App icons & images
```

## 🚀 Deployment Guide

### Step 1: Deploy Backend to Render

1. **Create a Render account** at [render.com](https://render.com)

2. **Create a new Web Service**:
   - Connect your GitHub repository
   - Choose the repository
   - Configure:
     - **Name**: `ipc-chatbot-api`
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
   
3. **Add Environment Variables**:
   - Go to "Environment" tab
   - Add: `GROQ_API_KEY` = `your_api_key_here`

4. **Upload the PDF**:
   - Include `THE-INDIAN-PENAL-CODE-1860.pdf` in your repository

5. **Deploy** - Render will automatically build and deploy

6. **Get your URL**: `https://ipc-chatbot-api.onrender.com`

### Step 2: Deploy Mobile App with Expo

1. **Update API URL** in `mobile-app/App.js`:
```javascript
const API_URL = 'https://ipc-chatbot-api.onrender.com';
```

2. **Install Expo CLI**:
```bash
npm install -g expo-cli eas-cli
```

3. **Navigate to mobile app**:
```bash
cd mobile-app
npm install
```

4. **Login to Expo**:
```bash
eas login
```

5. **Build the app**:
```bash
# For Android APK
eas build --platform android --profile preview

# For iOS
eas build --platform ios
```

6. **Publish to stores** or share the APK directly

## 🧪 Local Testing

### Backend
```bash
pip install -r requirements.txt
python app.py
```
Visit: http://localhost:5000

### Mobile App
```bash
cd mobile-app
npm install
npx expo start
```
Scan QR code with Expo Go app

## 🔧 Environment Variables

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

## 📱 Mobile App Features

- 💬 Real-time chat interface
- 🎨 Beautiful gradient header
- ⌨️ Keyboard-aware input
- 📱 Works on iOS & Android
- 🌐 Web support via Expo

## 🌐 Web Features

- 💻 Clean, responsive design
- 💬 Real-time chat
- 📱 Mobile-friendly web view

## 📝 License

MIT License
