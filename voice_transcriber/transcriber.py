"""Speech-to-text transcription using OpenAI Whisper."""

import logging
import os
import threading
import time
from typing import Optional
import whisper

from .config import config


logger = logging.getLogger(__name__)


class Transcriber:
    """Handles speech-to-text transcription using OpenAI Whisper."""
    
    def __init__(self):
        self.model = None
        self.model_load_time = 0
        self.model_lock = threading.Lock()
        self.last_used = 0
        
        # Start model unloader thread
        self.unloader_thread = threading.Thread(target=self._model_unloader, daemon=True)
        self.unloader_thread.start()
    
    def transcribe(self, audio_file: str) -> Optional[str]:
        """Transcribe audio file to text."""
        try:
            # Load model if needed
            if not self._ensure_model_loaded():
                return None
            
            self.last_used = time.time()
            
            # Transcribe audio
            logger.info(f"Transcribing audio file: {audio_file}")
            start_time = time.time()
            
            result = self.model.transcribe(audio_file)
            
            transcription_time = time.time() - start_time
            text = result["text"].strip()
            
            logger.info(f"Transcription completed in {transcription_time:.2f}s: '{text}'")
            
            # Clean up temporary file
            try:
                os.unlink(audio_file)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {audio_file}: {e}")
            
            return text if text else None
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def _ensure_model_loaded(self) -> bool:
        """Ensure the Whisper model is loaded."""
        with self.model_lock:
            if self.model is None:
                try:
                    logger.info(f"Loading Whisper model: {config.model_name}")
                    start_time = time.time()
                    
                    self.model = whisper.load_model(
                        config.model_name,
                        download_root=config.model_cache_dir
                    )
                    
                    self.model_load_time = time.time() - start_time
                    logger.info(f"Model loaded in {self.model_load_time:.2f}s")
                    return True
                    
                except Exception as e:
                    logger.error(f"Failed to load Whisper model: {e}")
                    return False
            
            return True
    
    def _model_unloader(self):
        """Unload model after period of inactivity to free memory."""
        while True:
            time.sleep(30)  # Check every 30 seconds
            
            with self.model_lock:
                if (self.model is not None and 
                    self.last_used > 0 and 
                    time.time() - self.last_used > 300):  # 5 minutes of inactivity
                    
                    logger.info("Unloading Whisper model due to inactivity")
                    self.model = None
                    self.last_used = 0
    
    def is_model_loaded(self) -> bool:
        """Check if model is currently loaded."""
        with self.model_lock:
            return self.model is not None
    
    def get_model_info(self) -> dict:
        """Get information about the model."""
        return {
            "model_name": config.model_name,
            "is_loaded": self.is_model_loaded(),
            "load_time": self.model_load_time,
            "last_used": self.last_used
        } 