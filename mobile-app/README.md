# Voice Copilot Mobile App

A React Native mobile companion app for the Voice Copilot service that allows you to record voice and get transcriptions from your desktop service.

## Features

- 🎤 **Large Microphone Button**: Easy-to-use recording interface
- 🌐 **Network Connectivity**: Works over local WiFi or internet via ngrok
- 📱 **Cross-Platform**: Built with React Native/Expo for iOS and Android
- 🔄 **Real-time Status**: Shows connection status and processing feedback
- 📝 **Transcription Display**: Shows transcribed text with clear formatting

## Setup

### Prerequisites

- Node.js (v16 or later)
- Expo CLI: `npm install -g expo-cli`
- Expo Go app on your mobile device (for testing)

### Installation

1. Navigate to the mobile app directory:
   ```bash
   cd mobile-app
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Scan the QR code with Expo Go app on your phone

## Configuration

### Local Network Setup

1. Find your computer's IP address:
   ```bash
   # On Linux/Mac
   ip addr show | grep inet
   # or
   ifconfig | grep inet
   
   # On Windows
   ipconfig
   ```

2. Start the Voice Copilot API server on your desktop:
   ```bash
   # In the main voice-copilot directory
   poetry run voice-transcriber-api --host 0.0.0.0 --port 8000
   
   # Or run the combined service (desktop + API)
   poetry run voice-transcriber-combined --api-host 0.0.0.0 --api-port 8000
   ```

3. In the mobile app, set the server URL to:
   ```
   http://YOUR_COMPUTER_IP:8000
   ```
   Example: `http://192.168.1.100:8000`

### Internet Access via ngrok

1. Install ngrok: https://ngrok.com/download

2. Start the API server:
   ```bash
   poetry run voice-transcriber-api --host 0.0.0.0 --port 8000
   ```

3. In another terminal, expose the port via ngrok:
   ```bash
   ngrok http 8000
   ```

4. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`) and use it in the mobile app

## Usage

1. **Connect to Server**: Enter your server URL and tap "Test Connection"
2. **Record Audio**: Tap and hold the microphone button while speaking
3. **View Transcription**: The transcribed text will appear below the recording area
4. **Clear Results**: Tap "Clear" to remove the transcription

## API Endpoints

The mobile app communicates with these endpoints:

- `GET /health` - Check server health
- `POST /transcribe` - Upload audio file for transcription
- `GET /status` - Get transcriber status

## Troubleshooting

### Connection Issues

- Ensure your phone and computer are on the same WiFi network (for local setup)
- Check that the API server is running and accessible
- Verify the IP address and port are correct
- Try using ngrok for internet access if local network doesn't work

### Audio Issues

- Grant microphone permissions when prompted
- Ensure you're holding the record button while speaking
- Check that audio recording works in other apps on your device

### Build Issues

- Make sure you have the latest Expo CLI
- Clear cache: `expo r -c`
- Reinstall dependencies: `rm -rf node_modules && npm install`

## Development

### Project Structure

```
mobile-app/
├── App.js              # Main app component
├── package.json        # Dependencies and scripts
├── app.json           # Expo configuration
├── babel.config.js    # Babel configuration
└── assets/            # App icons and images
```

### Key Dependencies

- **Expo**: React Native framework
- **expo-av**: Audio recording and playback
- **react-native-paper**: Material Design components
- **expo-file-system**: File system operations

## Building for Production

### Android

```bash
expo build:android
```

### iOS

```bash
expo build:ios
```

Note: You'll need an Apple Developer account for iOS builds.

## License

Same as the main Voice Copilot project (MIT License).