"""Text-to-speech functionality for reading selected text aloud."""

import logging
import asyncio
import tempfile
import os
import threading
import time
from typing import Optional
import pyperclip
import edge_tts
import pygame
import pyautogui
import signal


logger = logging.getLogger(__name__)


class TextToSpeech:
    """Handles text-to-speech functionality."""
    
    def __init__(self):
        """Initialize Text-to-Speech engine with Edge-TTS"""
        self.current_speech_task = None
        self.speech_thread = None
        self.is_speaking = False
        self.stop_requested = False
        
        try:
            # Initialize pygame mixer for audio playback
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
            logger.info("Pygame mixer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")
            raise
        
        # Default voice (can be customized)
        self.voice = "en-US-AriaNeural"  # High-quality female voice
        
        logger.info("Edge-TTS engine initialized successfully")
    
    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for speech synthesis"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Replace common symbols with spoken equivalents
        replacements = {
            "&": "and",
            "@": "at",
            "#": "hash",
            "$": "dollar",
            "%": "percent",
            "^": "caret",
            "*": "asterisk",
            "+": "plus",
            "=": "equals",
            "<": "less than",
            ">": "greater than",
            "|": "pipe",
            "\\": "backslash",
            "/": "slash",
            "~": "tilde",
            "`": "backtick",
            "©": "copyright",
            "®": "registered",
            "™": "trademark",
            "°": "degrees",
            "€": "euro",
            "£": "pound",
            "¥": "yen",
            "₹": "rupee",
            "—": " ",
            "–": " ",
            "…": " dot dot dot ",
            "→": "arrow",
            "←": "left arrow",
            "↑": "up arrow",
            "↓": "down arrow",
            "✓": "checkmark",
            "✗": "x mark",
            "★": "star",
            "♥": "heart",
            "♦": "diamond",
            "♣": "club",
            "♠": "spade"
        }
        
        for symbol, replacement in replacements.items():
            text = text.replace(symbol, replacement)
        
        # Handle URLs
        if "http" in text.lower():
            text = text.replace("https://", "").replace("http://", "")
            text = text.replace("www.", "")
        
        # Handle email addresses
        if "@" in text and "." in text:
            words = text.split()
            for i, word in enumerate(words):
                if "@" in word and "." in word:
                    words[i] = word.replace("@", " at ").replace(".", " dot ")
            text = " ".join(words)
        
        # Remove markdown formatting
        text = text.replace("**", "").replace("*", "").replace("__", "").replace("_", "")
        text = text.replace("```", "").replace("`", "").replace("##", "").replace("#", "")
        
        # Clean up multiple spaces
        text = " ".join(text.split())
        
        return text.strip()
    
    def get_selected_text(self) -> Optional[str]:
        """Get selected text from clipboard by simulating Ctrl+C"""
        try:
            logger.info("=== STARTING get_selected_text ===")
            
            # Store current clipboard content
            original_clipboard = ""
            try:
                original_clipboard = pyperclip.paste()
                logger.info(f"Original clipboard content: '{original_clipboard}'")
            except Exception as e:
                logger.warning(f"Could not get original clipboard: {e}")
                original_clipboard = ""
            
            # Try different approaches to get selected text
            
            # METHOD 1: Try using xclip to get selection directly (Linux-specific)
            try:
                import subprocess
                logger.info("Trying Method 1: xclip selection")
                result = subprocess.run(['xclip', '-selection', 'primary', '-o'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and result.stdout.strip():
                    selected_text = result.stdout.strip()
                    logger.info(f"✓ SUCCESS (xclip): Got selected text: '{selected_text[:50]}...'")
                    return selected_text
                else:
                    logger.info("xclip returned empty or failed")
            except Exception as e:
                logger.info(f"xclip method failed: {e}")
            
            # METHOD 2: Traditional clipboard copy with better timing
            logger.info("Trying Method 2: Traditional clipboard copy")
            
            # Clear clipboard to detect changes
            try:
                pyperclip.copy("")
                logger.info("Clipboard cleared successfully")
                
                # Wait longer to ensure selection is stable
                time.sleep(0.2)
                
                # Try copying with different approaches
                logger.info("Attempting to copy selected text...")
                
                # Approach A: Multiple attempts with delays
                for attempt in range(3):
                    logger.info(f"Copy attempt {attempt + 1}/3")
                    
                    try:
                        # Use keyDown/keyUp for more control
                        pyautogui.keyDown('ctrl')
                        time.sleep(0.05)
                        pyautogui.press('c')
                        time.sleep(0.05)
                        pyautogui.keyUp('ctrl')
                        
                        # Wait and check if something was copied
                        time.sleep(0.3)
                        
                        current_clipboard = pyperclip.paste()
                        logger.info(f"Attempt {attempt + 1} result: '{current_clipboard}'")
                        
                        if current_clipboard and current_clipboard != original_clipboard and current_clipboard.strip():
                            logger.info(f"✓ SUCCESS (attempt {attempt + 1}): Selected text copied")
                            return current_clipboard.strip()
                            
                    except Exception as e:
                        logger.warning(f"Copy attempt {attempt + 1} failed: {e}")
                        time.sleep(0.1)
                
                logger.info("✗ All copy attempts failed")
                
            except Exception as e:
                logger.error(f"Traditional copy method failed: {e}")
            
            # Restore original clipboard
            if original_clipboard:
                try:
                    pyperclip.copy(original_clipboard)
                    logger.info("Original clipboard restored")
                except:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error in get_selected_text: {e}")
            return None
        finally:
            logger.info("=== ENDING get_selected_text ===\n")
    
    async def _generate_speech(self, text: str) -> Optional[str]:
        """Generate speech audio file using Edge-TTS"""
        try:
            logger.debug(f"Generating speech for text: '{text[:50]}...'")
            
            # Import here to handle potential import errors
            import edge_tts
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            logger.debug(f"Generating audio to: {temp_path}")
            
            # Generate speech
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(temp_path)
            
            file_size = os.path.getsize(temp_path)
            logger.info(f"Generated audio file: {file_size} bytes")
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    def _play_audio(self, audio_path: str):
        """Play audio file using pygame"""
        try:
            logger.debug(f"Playing audio file: {audio_path}")
            
            import pygame
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            logger.info("Audio playback started")
            
            # Wait for playback to complete or stop to be requested
            while pygame.mixer.music.get_busy() and not self.stop_requested:
                time.sleep(0.1)
                
            if self.stop_requested:
                logger.info("Audio playback stopped by request")
            else:
                logger.info("Audio playback completed")
                
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
        finally:
            # Clean up
            try:
                import pygame
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    logger.debug("Stopped pygame mixer")
            except:
                pass
            try:
                os.unlink(audio_path)
                logger.debug(f"Cleaned up audio file: {audio_path}")
            except:
                pass
    
    def _speech_worker(self, text: str):
        """Background worker for speech synthesis and playback"""
        try:
            self.is_speaking = True
            self.stop_requested = False
            
            logger.debug("Starting speech worker thread")
            
            # Run async speech generation with timeout
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Set a reasonable timeout for speech generation (30 seconds)
                audio_path = loop.run_until_complete(
                    asyncio.wait_for(self._generate_speech(text), timeout=30.0)
                )
                
                if audio_path and not self.stop_requested:
                    logger.debug("Speech generated successfully, starting playback")
                    self._play_audio(audio_path)
                else:
                    logger.warning("Speech generation failed or was cancelled")
                    
            except asyncio.TimeoutError:
                logger.error("Speech generation timed out after 30 seconds")
            except Exception as e:
                logger.error(f"Error in speech generation: {e}")
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Error in speech worker: {e}")
        finally:
            self.is_speaking = False
            self.stop_requested = False
            logger.debug("Speech worker thread finished")
    
    def speak_text(self, text: str):
        """Speak the given text using Edge-TTS"""
        if not text or not text.strip():
            logger.warning("No text provided for speech")
            return
        
        # Stop any current speech
        self.stop_speech()
        
        # Clean the text
        cleaned_text = self._clean_text(text)
        if not cleaned_text:
            logger.warning("Text became empty after cleaning")
            return
        
        # Truncate very long text
        if len(cleaned_text) > 500:
            cleaned_text = cleaned_text[:497] + "..."
            logger.info(f"Text truncated to 500 characters")
        
        logger.info(f"Speaking text: '{cleaned_text[:50]}{'...' if len(cleaned_text) > 50 else ''}'")
        
        # Start speech in background thread
        self.speech_thread = threading.Thread(target=self._speech_worker, args=(cleaned_text,))
        self.speech_thread.daemon = True
        self.speech_thread.start()
    
    def speak_selected_text(self):
        """Speak currently selected text or stop current speech if none selected."""
        try:
            logger.info("TTS hotkey triggered - checking for selected text")
            
            # Get selected text using our improved method
            selected_text = self.get_selected_text()
            
            if selected_text:
                logger.info(f"Found selected text, starting TTS: '{selected_text[:50]}...'")
                
                # If we're already speaking the same text, stop instead of restarting
                if self.is_speaking:
                    logger.info("Already speaking - stopping current speech instead of restarting")
                    self.stop_speech()
                    return
                
                cleaned_text = self._clean_text(selected_text)
                if cleaned_text:
                    self.speak_text(cleaned_text)
                else:
                    logger.warning("Selected text was empty after cleaning")
            else:
                # No text selected - stop current speech
                logger.info("No text selected, stopping current speech")
                self.stop_speech()
                
        except Exception as e:
            logger.error(f"Error in speak_selected_text: {e}")
            # Fallback: just stop any current speech
            try:
                self.stop_speech()
            except:
                pass
    
    def stop_speech(self):
        """Stop current speech synthesis and playback"""
        if self.is_speaking:
            logger.info("Stopping current speech")
            self.stop_requested = True
            
            # Stop pygame mixer
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            # Wait for speech thread to finish
            if self.speech_thread and self.speech_thread.is_alive():
                self.speech_thread.join(timeout=1.0)
    
    def is_busy(self) -> bool:
        """Check if TTS is currently speaking"""
        return self.is_speaking
    
    def set_voice(self, voice: str):
        """Set the voice for speech synthesis"""
        self.voice = voice
        logger.info(f"Voice changed to: {voice}")
    
    def list_voices(self):
        """List available voices (for future enhancement)"""
        # Some popular Edge-TTS voices
        voices = [
            "en-US-AriaNeural",      # Female, friendly
            "en-US-JennyNeural",     # Female, professional
            "en-US-GuyNeural",       # Male, warm
            "en-US-DavisNeural",     # Male, confident
            "en-GB-SoniaNeural",     # British Female
            "en-GB-RyanNeural",      # British Male
            "en-AU-NatashaNeural",   # Australian Female
            "en-AU-WilliamNeural",   # Australian Male
        ]
        return voices
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_speech()
        try:
            pygame.mixer.quit()
        except:
            pass
        logger.info("TTS engine cleaned up") 