"""Main entry point for the Voice Transcriber application."""

import argparse
import logging
import sys
from .config import config
from .service import VoiceTranscriberService


def setup_logging(debug: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('voice_transcriber.log')
        ]
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Voice Transcriber - Local speech-to-text with keybind activation')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--model', default='base', choices=['tiny', 'base', 'small', 'medium', 'large'], 
                       help='Whisper model size (default: base)')
    parser.add_argument('--hotkey', default='ctrl+f1', help='Hotkey combination (default: ctrl+f1)')
    parser.add_argument('--tts-hotkey', default='ctrl+f2', help='TTS hotkey combination (default: ctrl+f2)')
    parser.add_argument('--no-tray', action='store_true', help='Disable system tray icon')
    parser.add_argument('--no-notifications', action='store_true', help='Disable desktop notifications')
    parser.add_argument('--save-recordings', action='store_true', help='Save recordings for debugging')
    parser.add_argument('--test-typing', action='store_true', help='Test typing functionality and exit')
    
    args = parser.parse_args()
    
    # Update config from arguments
    config.debug = args.debug
    config.model_name = args.model
    config.show_system_tray = not args.no_tray
    config.show_notifications = not args.no_notifications
    config.save_recordings = args.save_recordings
    
    # Parse hotkeys
    if args.hotkey:
        config.hotkey = tuple(key.strip().lower() for key in args.hotkey.split('+'))
    if args.tts_hotkey:
        config.tts_hotkey = tuple(key.strip().lower() for key in args.tts_hotkey.split('+'))
    
    # Setup logging
    setup_logging(config.debug)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Voice Transcriber")
    logger.info(f"Configuration: model={config.model_name}, hotkey={'+'.join(config.hotkey)}, tts_hotkey={'+'.join(config.tts_hotkey)}")
    
    # Test typing functionality if requested
    if args.test_typing:
        from .text_inserter import TextInserter
        inserter = TextInserter()
        print("Position your cursor where you want test text to appear...")
        print("Test will start in 3 seconds...")
        if inserter.test_typing():
            print("Typing test completed successfully!")
            return 0
        else:
            print("Typing test failed!")
            return 1
    
    # Create and run service
    service = VoiceTranscriberService()
    
    try:
        service.run_forever()
        return 0
    except Exception as e:
        logger.error(f"Service failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 