"""Web API server for mobile app integration."""

import logging
import os
import tempfile
import time
from typing import Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import threading

from .transcriber import Transcriber
from .config import config

logger = logging.getLogger(__name__)

class VoiceTranscriberAPI:
    """Web API server for voice transcription."""
    
    def __init__(self, host='0.0.0.0', port=8000):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for mobile app
        
        self.host = host
        self.port = port
        self.transcriber = Transcriber()
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'service': 'voice-transcriber-api',
                'timestamp': time.time()
            })
        
        @self.app.route('/transcribe', methods=['POST'])
        def transcribe_audio():
            """Transcribe uploaded audio file."""
            try:
                # Check if audio file is present
                if 'audio' not in request.files:
                    return jsonify({'error': 'No audio file provided'}), 400
                
                audio_file = request.files['audio']
                if audio_file.filename == '':
                    return jsonify({'error': 'No audio file selected'}), 400
                
                # Save uploaded file temporarily
                temp_file = tempfile.NamedTemporaryFile(
                    suffix='.wav', 
                    delete=False
                )
                temp_filename = temp_file.name
                temp_file.close()
                
                audio_file.save(temp_filename)
                
                logger.info(f"Received audio file for transcription: {temp_filename}")
                
                # Transcribe audio
                start_time = time.time()
                text = self.transcriber.transcribe(temp_filename)
                transcription_time = time.time() - start_time
                
                # Clean up temp file (transcriber already does this, but just in case)
                try:
                    if os.path.exists(temp_filename):
                        os.unlink(temp_filename)
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file: {e}")
                
                if text:
                    logger.info(f"Transcription successful: '{text}' (took {transcription_time:.2f}s)")
                    return jsonify({
                        'success': True,
                        'text': text,
                        'transcription_time': transcription_time,
                        'timestamp': time.time()
                    })
                else:
                    logger.warning("No text transcribed")
                    return jsonify({
                        'success': False,
                        'error': 'No speech detected or transcription failed',
                        'transcription_time': transcription_time,
                        'timestamp': time.time()
                    }), 400
                    
            except Exception as e:
                logger.error(f"Transcription API error: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': time.time()
                }), 500
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            """Get transcriber status."""
            try:
                model_info = self.transcriber.get_model_info()
                return jsonify({
                    'success': True,
                    'model_info': model_info,
                    'config': {
                        'model_name': config.model_name,
                        'sample_rate': config.sample_rate,
                        'channels': config.channels
                    },
                    'timestamp': time.time()
                })
            except Exception as e:
                logger.error(f"Status API error: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': time.time()
                }), 500
    
    def run(self, debug=False):
        """Run the API server."""
        logger.info(f"Starting Voice Transcriber API server on {self.host}:{self.port}")
        self.app.run(
            host=self.host,
            port=self.port,
            debug=debug,
            threaded=True
        )
    
    def run_threaded(self, debug=False):
        """Run the API server in a separate thread."""
        server_thread = threading.Thread(
            target=self.run,
            kwargs={'debug': debug},
            daemon=True
        )
        server_thread.start()
        return server_thread


def main():
    """Main entry point for API server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Voice Transcriber API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--model', default='base', choices=['tiny', 'base', 'small', 'medium', 'large'], 
                       help='Whisper model size')
    
    args = parser.parse_args()
    
    # Update config
    config.model_name = args.model
    config.debug = args.debug
    
    # Setup logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run API server
    api_server = VoiceTranscriberAPI(host=args.host, port=args.port)
    api_server.run(debug=args.debug)


if __name__ == '__main__':
    main()