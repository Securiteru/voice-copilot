# Voice Transcriber

A fast, local, privacy-focused speech-to-text and text-to-speech application for Linux. Uses OpenAI Whisper for transcription and Microsoft Edge TTS for high-quality speech synthesis.

## Features

🎤 **Speech-to-Text (STT)**
- Press `Ctrl+F1`, speak, release to transcribe and type at cursor
- Uses OpenAI Whisper models locally (no internet required for STT)
- Fast transcription with model memory management
- Support for multiple Whisper model sizes (tiny, base, small, medium, large)

🔊 **Text-to-Speech (TTS)**
- Press `Ctrl+F2` to read selected text aloud
- Press `Ctrl+F2` again (with no text selected) to stop current speech
- High-quality Microsoft Edge TTS voices
- Works offline after initial voice download

🔒 **Privacy & Local Processing**
- All speech processing happens locally
- No data sent to external services
- Temporary audio files are automatically cleaned up

⚡ **Performance**
- Fast transcription (0.3-0.4s with tiny model)
- Low memory usage with automatic model unloading
- Minimal system resource impact

## Installation

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt install portaudio19-dev python3-tk python3-dev

# Arch Linux  
sudo pacman -S portaudio tk

# Fedora
sudo dnf install portaudio-devel tkinter python3-devel
```

### Install Voice Transcriber

```bash
# Clone the repository
git clone https://github.com/your-username/voice-transcriber.git
cd voice-transcriber

# Install with Poetry
pip install poetry
poetry install

# Or install with pip
pip install -e .
```

## Usage

### Basic Usage

```bash
# Run with default settings (tiny model, system tray enabled)
poetry run voice-transcriber

# Run with specific model and debug logging
poetry run voice-transcriber --model base --debug

# Run without system tray (headless)
poetry run voice-transcriber --no-tray

# Custom hotkeys
poetry run voice-transcriber --hotkey ctrl+shift+space --tts-hotkey ctrl+shift+r
```

### Hotkeys

- **Speech-to-Text**: `Ctrl+F1` (hold to record, release to transcribe)
- **Text-to-Speech**: `Ctrl+F2` (read selected text or stop current speech)

### Command Line Options

```bash
usage: voice-transcriber [-h] [--model {tiny,base,small,medium,large}] 
                        [--hotkey HOTKEY] [--tts-hotkey TTS_HOTKEY] 
                        [--no-tray] [--debug]

Local Speech-to-Text and Text-to-Speech Service

options:
  -h, --help            show this help message and exit
  --model {tiny,base,small,medium,large}
                        Whisper model size (default: tiny)
  --hotkey HOTKEY       Recording hotkey (default: ctrl+f1)
  --tts-hotkey TTS_HOTKEY
                        Text-to-speech hotkey (default: ctrl+f2)
  --no-tray             Disable system tray icon
  --debug               Enable debug logging
```

## Autostart Setup

The voice transcriber includes an automated setup script that handles configuration and installation.

### Quick Setup (Recommended)

```bash
# Clone and enter the project directory
git clone https://github.com/your-username/voice-transcriber.git
cd voice-transcriber

# Install dependencies
poetry install

# Run automated setup
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Create a configuration file from the example template
2. Configure service files with your project path
3. Install and start the systemd service
4. Verify everything is working

### Configuration

The setup script automatically creates `voice_transcriber.env` from the example template. You can customize it:

```bash
# Edit configuration before running setup
nano voice_transcriber.env
```

Available options:
- `PROJECT_PATH`: Absolute path to your installation (auto-detected)
- `WHISPER_MODEL`: Model size (tiny, base, small, medium, large)
- `HOTKEY`: Speech-to-text hotkey (default: ctrl+f1)
- `TTS_HOTKEY`: Text-to-speech hotkey (default: ctrl+f2)  
- `ENABLE_SYSTEM_TRAY`: Show system tray icon (true/false)
- `DEBUG_MODE`: Enable debug logging (true/false)
- `AUTOSTART_METHOD`: Installation method (systemd, desktop, none)

### Setup Script Commands

```bash
./setup.sh          # Full setup and installation
./setup.sh --status  # Check service status
./setup.sh --logs    # View service logs  
./setup.sh --stop    # Stop service
./setup.sh --help    # Show help
```

### Manual Setup (Advanced)

Both autostart methods require updating the configuration files with your actual project path.

#### Step 1: Configure Environment

```bash
# Copy example configuration
cp voice_transcriber.env.example voice_transcriber.env

# Edit with your settings
nano voice_transcriber.env
```

## Configuration

The application uses sensible defaults but can be customized:

### Model Sizes
- **tiny**: Fastest, ~39 MB, good for simple speech
- **base**: Balanced, ~74 MB, better accuracy  
- **small**: Higher accuracy, ~244 MB
- **medium**: Professional quality, ~769 MB
- **large**: Best accuracy, ~1550 MB

### TTS Voices
The application uses high-quality Microsoft Edge TTS voices:
- Default: `en-US-AriaNeural` (Female)
- Available: Multiple English variants (US, UK, AU) and other languages

## Development

### Project Structure

```
voice_transcriber/
├── __init__.py
├── main.py              # CLI entry point
├── service.py           # Main orchestrator
├── config.py            # Configuration management
├── audio_recorder.py    # Audio recording with sounddevice
├── transcriber.py       # OpenAI Whisper integration
├── text_inserter.py     # Text insertion at cursor
├── text_to_speech.py    # Edge-TTS integration
├── hotkey_handler.py    # Global hotkey detection
└── system_tray.py       # System tray integration
```

### Dependencies

- **openai-whisper**: Local speech recognition
- **edge-tts**: High-quality text-to-speech
- **sounddevice**: Audio recording
- **pygame**: Audio playback
- **pynput**: Global hotkey detection
- **pyautogui**: Text insertion and clipboard handling
- **pystray**: System tray integration

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit with semantic commits: `git commit -m "feat: add new feature"`
5. Push and create a Pull Request

## Privacy & Security

- **Local Processing**: All speech recognition happens on your machine
- **No Cloud Dependencies**: STT works completely offline
- **Minimal Data**: Only temporary audio files (auto-deleted)
- **No Telemetry**: No usage data collection or external communication

## Troubleshooting

### Audio Issues
```bash
# List audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test microphone
poetry run python -c "import sounddevice as sd; import numpy as np; print('Recording...'); audio = sd.rec(int(3 * 44100), samplerate=44100, channels=1); sd.wait(); print('Playback...'); sd.play(audio, 44100); sd.wait()"
```

### Permission Issues
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Log out and back in
```

### Hotkey Not Working
- Ensure no other applications are using the same hotkeys
- Try different hotkey combinations
- Check if running with sufficient permissions

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for excellent local STT
- [Edge-TTS](https://github.com/rany2/edge-tts) for high-quality TTS
- Inspired by various open-source voice automation tools 