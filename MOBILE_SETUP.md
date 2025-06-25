# Voice Copilot Mobile App Setup Guide

This guide will help you set up the Voice Copilot mobile app companion to work with your desktop service.

## Overview

The Voice Copilot mobile app allows you to:
- Record voice remotely from your phone
- Send recordings to your desktop for transcription
- View transcribed text on your mobile device
- Work over local WiFi or internet via ngrok

## Quick Start

### 1. Start the API Server

Choose one of these options:

**Option A: API Server Only**
```bash
cd voice-copilot
poetry run voice-transcriber-api --host 0.0.0.0 --port 8000
```

**Option B: Combined Service (Desktop + API)**
```bash
cd voice-copilot
poetry run voice-transcriber-combined --api-host 0.0.0.0 --api-port 8000
```

**Option C: With ngrok for Internet Access**
```bash
cd voice-copilot
./scripts/start-with-ngrok.sh
```

### 2. Find Your Network Configuration

```bash
cd voice-copilot
python3 scripts/get-local-ip.py
```

This will show you:
- Your local IP address
- Suggested server URLs
- Network interface information

### 3. Set Up the Mobile App

```bash
cd voice-copilot/mobile-app
npm install
npm start
```

### 4. Configure and Test

1. Install Expo Go on your phone
2. Scan the QR code from the terminal
3. Enter your server URL in the app
4. Test the connection
5. Start recording!

## Network Setup Options

### Local WiFi (Recommended)

**Pros:**
- Fast and responsive
- Private and secure
- No external dependencies

**Cons:**
- Only works on same WiFi network
- Need to know your computer's IP address

**Setup:**
1. Ensure both devices are on the same WiFi
2. Find your computer's IP: `python3 scripts/get-local-ip.py`
3. Use URL like: `http://192.168.1.100:8000`

### Internet via ngrok

**Pros:**
- Works from anywhere
- Easy to share with others
- Handles firewall/NAT issues

**Cons:**
- Requires ngrok account (free tier available)
- Slightly higher latency
- Data goes through ngrok servers

**Setup:**
1. Install ngrok: https://ngrok.com/download
2. Run: `./scripts/start-with-ngrok.sh`
3. Use the ngrok URL (e.g., `https://abc123.ngrok.io`)

## Mobile App Features

### Main Interface
- **Large Microphone Button**: Tap and hold to record
- **Connection Status**: Shows if connected to server
- **Server URL Input**: Configure your server address
- **Test Connection**: Verify server is reachable

### Recording
- **Visual Feedback**: Button changes color when recording
- **Duration Display**: Shows recording time
- **Processing Indicator**: Shows when transcribing

### Results
- **Transcription Display**: Shows the transcribed text
- **Clear Button**: Remove current transcription
- **Status Messages**: Success/error notifications

## Troubleshooting

### Connection Issues

**"Cannot connect to server"**
- Check that the API server is running
- Verify the IP address and port are correct
- Ensure both devices are on the same WiFi (for local setup)
- Try using ngrok for internet access

**"Connection timeout"**
- Server might be overloaded or crashed
- Check server logs: `tail -f api_server.log`
- Restart the server

### Audio Issues

**"No speech detected"**
- Speak louder and clearer
- Ensure you're holding the record button while speaking
- Check microphone permissions on your phone
- Try recording for at least 1-2 seconds

**"Recording failed"**
- Grant microphone permissions when prompted
- Close and reopen the app
- Check if other apps are using the microphone

### Performance Issues

**Slow transcription**
- Use a smaller Whisper model (tiny/base instead of large)
- Ensure your computer has sufficient resources
- Close other resource-intensive applications

**App crashes**
- Update Expo Go app
- Clear app cache: close and reopen
- Check for JavaScript errors in Expo logs

## Advanced Configuration

### Server Options

```bash
# Different Whisper models
poetry run voice-transcriber-api --model tiny    # Fastest
poetry run voice-transcriber-api --model base    # Balanced
poetry run voice-transcriber-api --model small   # Better accuracy
poetry run voice-transcriber-api --model medium  # High accuracy
poetry run voice-transcriber-api --model large   # Best accuracy

# Custom host/port
poetry run voice-transcriber-api --host 0.0.0.0 --port 9000

# Debug mode
poetry run voice-transcriber-api --debug
```

### Mobile App Customization

The mobile app automatically adapts to your server configuration, but you can modify:

- Server URL (in the app interface)
- Recording quality (modify App.js)
- UI theme (modify App.js theme object)

### Security Considerations

**Local Network:**
- Traffic stays on your local network
- No external data transmission
- Firewall may block connections

**ngrok:**
- Data passes through ngrok servers
- Use HTTPS URLs when possible
- Consider ngrok's privacy policy

## API Reference

The mobile app uses these endpoints:

### GET /health
Check if server is running
```json
{
  "status": "healthy",
  "service": "voice-transcriber-api",
  "timestamp": 1234567890
}
```

### GET /status
Get server configuration and model info
```json
{
  "success": true,
  "config": {
    "model_name": "tiny",
    "sample_rate": 16000,
    "channels": 1
  },
  "model_info": {
    "is_loaded": false,
    "load_time": 0,
    "last_used": 0
  }
}
```

### POST /transcribe
Upload audio file for transcription
- **Content-Type**: multipart/form-data
- **Field**: audio (WAV file)

**Success Response:**
```json
{
  "success": true,
  "text": "Hello world",
  "transcription_time": 0.5,
  "timestamp": 1234567890
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "No speech detected",
  "transcription_time": 0.5,
  "timestamp": 1234567890
}
```

## Development

### Building the Mobile App

For development:
```bash
cd mobile-app
npm start
```

For production builds:
```bash
# Android
expo build:android

# iOS (requires Apple Developer account)
expo build:ios
```

### Modifying the Server

The API server code is in `voice_transcriber/api_server.py`. Key areas:

- **Routes**: Add new endpoints
- **Audio Processing**: Modify transcription logic
- **Error Handling**: Improve error messages
- **Authentication**: Add API keys if needed

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with both local and ngrok setups
5. Submit a pull request

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review server logs: `tail -f api_server.log`
3. Test with the provided test script: `python test_api.py`
4. Open an issue on GitHub with:
   - Your setup (local/ngrok)
   - Error messages
   - Server logs
   - Mobile app version