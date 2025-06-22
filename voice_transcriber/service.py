"""Main service that orchestrates all voice transcription components."""

import logging
import threading
import time
from typing import Optional
from plyer import notification

from .config import config
from .audio_recorder import AudioRecorder
from .transcriber import Transcriber
from .text_inserter import TextInserter
from .hotkey_handler import HotkeyHandler
from .system_tray import SystemTray
from .text_to_speech import TextToSpeech


logger = logging.getLogger(__name__)


class VoiceTranscriberService:
    """Main service for voice transcription."""
    
    def __init__(self):
        # Initialize components
        self.audio_recorder = AudioRecorder()
        self.transcriber = Transcriber()
        self.text_inserter = TextInserter()
        self.text_to_speech = TextToSpeech()
        self.hotkey_handler = HotkeyHandler()
        self.system_tray = SystemTray() if config.show_system_tray else None
        
        # State
        self.is_running = False
        self.is_processing = False
        
    def start(self) -> bool:
        """Start the voice transcriber service."""
        if self.is_running:
            logger.warning("Service is already running")
            return False
        
        try:
            logger.info("Starting Voice Transcriber Service")
            
            # Start system tray
            if self.system_tray:
                if not self.system_tray.start(on_quit=self.stop):
                    logger.warning("Failed to start system tray, continuing without it")
                    self.system_tray = None
            
            # Start hotkey handler
            if not self.hotkey_handler.start(
                on_press=self._on_hotkey_press,
                on_release=self._on_hotkey_release,
                on_tts_press=self._on_tts_hotkey_press
            ):
                logger.error("Failed to start hotkey handler")
                return False
            
            self.is_running = True
            
            # Show startup notification
            if config.show_notifications:
                self._show_notification(
                    "Voice Transcriber Started",
                    f"Press {'+'.join(config.hotkey)} to record, {'+'.join(config.tts_hotkey)} for TTS"
                )
            
            logger.info("Voice Transcriber Service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start service: {e}")
            self.stop()
            return False
    
    def stop(self):
        """Stop the voice transcriber service."""
        if not self.is_running:
            return
        
        logger.info("Stopping Voice Transcriber Service")
        
        # Stop components
        self.hotkey_handler.stop()
        
        if self.system_tray:
            self.system_tray.stop()
        
        # Stop any ongoing recording
        if self.audio_recorder.is_recording_active():
            self.audio_recorder.stop_recording()
        
        self.is_running = False
        logger.info("Voice Transcriber Service stopped")
    
    def _on_hotkey_press(self):
        """Handle hotkey press (start recording)."""
        if not self.is_running or self.is_processing:
            return
        
        try:
            logger.info("Hotkey pressed - starting recording")
            
            if self.audio_recorder.start_recording():
                # Update system tray
                if self.system_tray:
                    self.system_tray.set_recording(True)
                
                # Show notification
                if config.show_notifications:
                    self._show_notification("Recording", "Hold key and speak...")
            else:
                logger.warning("Failed to start recording")
                
        except Exception as e:
            logger.error(f"Error on hotkey press: {e}")
    
    def _on_hotkey_release(self):
        """Handle hotkey release (stop recording and transcribe)."""
        if not self.is_running or not self.audio_recorder.is_recording_active():
            return
        
        try:
            logger.info("Hotkey released - stopping recording")
            
            # Update system tray
            if self.system_tray:
                self.system_tray.set_recording(False)
            
            # Stop recording
            audio_file = self.audio_recorder.stop_recording()
            
            if audio_file:
                # Process in background thread
                processing_thread = threading.Thread(
                    target=self._process_audio,
                    args=(audio_file,),
                    daemon=True
                )
                processing_thread.start()
            else:
                logger.info("No audio to process")
                
        except Exception as e:
            logger.error(f"Error on hotkey release: {e}")
    
    def _on_tts_hotkey_press(self):
        """Handle TTS hotkey press (read selected text)."""
        if not self.is_running:
            return
        
        try:
            logger.info("TTS hotkey pressed - reading selected text")
            
            # Speak selected text in background thread
            tts_thread = threading.Thread(
                target=self._process_tts,
                daemon=True
            )
            tts_thread.start()
            
        except Exception as e:
            logger.error(f"Error on TTS hotkey press: {e}")
    
    def _process_tts(self):
        """Process text-to-speech in background thread."""
        try:
            logger.info("Processing text-to-speech")
            
            # Speak selected text or stop current speech if none selected
            self.text_to_speech.speak_selected_text()
                    
        except Exception as e:
            logger.error(f"Error processing TTS: {e}")
    
    def _process_audio(self, audio_file: str):
        """Process audio file in background thread."""
        if self.is_processing:
            logger.warning("Already processing audio, skipping")
            return
        
        self.is_processing = True
        
        try:
            logger.info("Processing audio for transcription")
            
            # Show processing notification
            if config.show_notifications:
                self._show_notification("Processing", "Transcribing audio...")
            
            # Transcribe audio
            text = self.transcriber.transcribe(audio_file)
            
            if text:
                logger.info(f"Transcription successful: '{text}'")
                
                # Insert text
                if self.text_inserter.insert_text(text):
                    # Show success notification
                    if config.show_notifications:
                        self._show_notification("Success", f"Typed: {text[:50]}...")
                else:
                    logger.error("Failed to insert text")
                    if config.show_notifications:
                        self._show_notification("Error", "Failed to insert text")
            else:
                logger.warning("No text transcribed")
                if config.show_notifications:
                    self._show_notification("No Speech", "No speech detected or transcription failed")
                    
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            if config.show_notifications:
                self._show_notification("Error", "Processing failed")
        finally:
            self.is_processing = False
    
    def _show_notification(self, title: str, message: str):
        """Show desktop notification."""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Voice Transcriber",
                timeout=3
            )
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
    
    def get_status(self) -> dict:
        """Get service status."""
        return {
            "is_running": self.is_running,
            "is_processing": self.is_processing,
            "is_recording": self.audio_recorder.is_recording_active(),
            "is_speaking": self.text_to_speech.is_busy(),
            "hotkey_status": self.hotkey_handler.get_status(),
            "transcriber_status": self.transcriber.get_model_info(),
            "tts_voice": self.text_to_speech.voice,
            "system_tray_status": self.system_tray.get_status() if self.system_tray else None
        }
    
    def run_forever(self):
        """Run service indefinitely."""
        if not self.start():
            return
        
        try:
            logger.info("Service running. Press Ctrl+C to stop.")
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop() 