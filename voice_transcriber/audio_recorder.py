"""Audio recording functionality using sounddevice."""

import logging
import threading
import time
from typing import Optional
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
import tempfile
import os

from .config import config


logger = logging.getLogger(__name__)


class AudioRecorder:
    """Handles audio recording from microphone."""
    
    def __init__(self):
        self.is_recording = False
        self.audio_data = []
        self.recording_thread: Optional[threading.Thread] = None
        self.start_time = 0
        
    def start_recording(self) -> bool:
        """Start audio recording."""
        if self.is_recording:
            return False
            
        try:
            self.is_recording = True
            self.audio_data = []
            self.start_time = time.time()
            
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            logger.info("Started audio recording")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.is_recording = False
            return False
    
    def stop_recording(self) -> Optional[str]:
        """Stop audio recording and save to temporary file."""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=1.0)
        
        recording_duration = time.time() - self.start_time
        
        # Check minimum duration
        if recording_duration < config.min_recording_duration:
            logger.info(f"Recording too short: {recording_duration:.2f}s")
            return None
            
        if not self.audio_data:
            logger.warning("No audio data recorded")
            return None
            
        try:
            # Convert to numpy array
            audio_array = np.concatenate(self.audio_data, axis=0)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_filename = temp_file.name
            temp_file.close()
            
            # Write WAV file
            wavfile.write(temp_filename, config.sample_rate, audio_array)
            
            # Optionally save to recordings directory
            if config.save_recordings:
                self._save_recording_copy(audio_array)
            
            logger.info(f"Saved recording: {recording_duration:.2f}s, {temp_filename}")
            return temp_filename
            
        except Exception as e:
            logger.error(f"Failed to save recording: {e}")
            return None
    
    def _record_audio(self):
        """Record audio in chunks."""
        try:
            def audio_callback(indata, frames, time, status):
                """Callback for audio recording."""
                if status:
                    logger.warning(f"Audio recording status: {status}")
                if self.is_recording:
                    self.audio_data.append(indata.copy())
            
            with sd.InputStream(
                callback=audio_callback,
                channels=config.channels,
                samplerate=config.sample_rate,
                blocksize=config.chunk_size,
                dtype=np.float32
            ):
                while self.is_recording:
                    sd.sleep(100)  # Sleep for 100ms
                    
                    # Check for maximum duration
                    if time.time() - self.start_time > config.max_recording_duration:
                        logger.info("Maximum recording duration reached")
                        break
                        
        except Exception as e:
            logger.error(f"Recording error: {e}")
            self.is_recording = False
    
    def _save_recording_copy(self, audio_array: np.ndarray):
        """Save a copy of the recording for debugging."""
        try:
            os.makedirs(config.recordings_dir, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(config.recordings_dir, f"recording_{timestamp}.wav")
            wavfile.write(filename, config.sample_rate, audio_array)
            logger.debug(f"Saved recording copy: {filename}")
        except Exception as e:
            logger.error(f"Failed to save recording copy: {e}")
    
    def is_recording_active(self) -> bool:
        """Check if recording is currently active."""
        return self.is_recording 