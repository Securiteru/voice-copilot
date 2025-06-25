"""Combined service that runs both desktop hotkeys and API server."""

import logging
import time
import threading
from .service import VoiceTranscriberService
from .api_server import VoiceTranscriberAPI
from .config import config

logger = logging.getLogger(__name__)


class CombinedVoiceService:
    """Combined service running both desktop and API functionality."""
    
    def __init__(self, api_host='0.0.0.0', api_port=8000):
        self.desktop_service = VoiceTranscriberService()
        self.api_server = VoiceTranscriberAPI(host=api_host, port=api_port)
        self.api_thread = None
        self.is_running = False
    
    def start(self):
        """Start both services."""
        try:
            logger.info("Starting Combined Voice Service")
            
            # Start desktop service
            if not self.desktop_service.start():
                logger.error("Failed to start desktop service")
                return False
            
            # Start API server in background thread
            self.api_thread = self.api_server.run_threaded(debug=config.debug)
            
            self.is_running = True
            logger.info("Combined Voice Service started successfully")
            logger.info(f"Desktop hotkeys: {'+'.join(config.hotkey)} (STT), {'+'.join(config.tts_hotkey)} (TTS)")
            logger.info(f"API server: http://{self.api_server.host}:{self.api_server.port}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start combined service: {e}")
            self.stop()
            return False
    
    def stop(self):
        """Stop both services."""
        if not self.is_running:
            return
        
        logger.info("Stopping Combined Voice Service")
        
        # Stop desktop service
        self.desktop_service.stop()
        
        # API server will stop when main thread exits
        self.is_running = False
        logger.info("Combined Voice Service stopped")
    
    def run_forever(self):
        """Run combined service indefinitely."""
        if not self.start():
            return
        
        try:
            logger.info("Combined service running. Press Ctrl+C to stop.")
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()
    
    def get_status(self):
        """Get status of both services."""
        return {
            'desktop_service': self.desktop_service.get_status(),
            'api_server': {
                'host': self.api_server.host,
                'port': self.api_server.port,
                'is_running': self.is_running
            }
        }


def main():
    """Main entry point for combined service."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Combined Voice Transcriber Service')
    parser.add_argument('--api-host', default='0.0.0.0', help='API server host')
    parser.add_argument('--api-port', type=int, default=8000, help='API server port')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--model', default='base', choices=['tiny', 'base', 'small', 'medium', 'large'], 
                       help='Whisper model size')
    parser.add_argument('--hotkey', default='ctrl+f1', help='Recording hotkey')
    parser.add_argument('--tts-hotkey', default='ctrl+f2', help='TTS hotkey')
    parser.add_argument('--no-tray', action='store_true', help='Disable system tray icon')
    parser.add_argument('--no-notifications', action='store_true', help='Disable desktop notifications')
    
    args = parser.parse_args()
    
    # Update config from arguments
    config.debug = args.debug
    config.model_name = args.model
    config.show_system_tray = not args.no_tray
    config.show_notifications = not args.no_notifications
    
    # Parse hotkeys
    if args.hotkey:
        config.hotkey = tuple(key.strip().lower() for key in args.hotkey.split('+'))
    if args.tts_hotkey:
        config.tts_hotkey = tuple(key.strip().lower() for key in args.tts_hotkey.split('+'))
    
    # Setup logging
    level = logging.DEBUG if config.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run combined service
    service = CombinedVoiceService(api_host=args.api_host, api_port=args.api_port)
    service.run_forever()


if __name__ == '__main__':
    main()