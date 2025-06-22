"""Text insertion functionality to type transcribed text at cursor."""

import logging
import time
from typing import Optional
import pyautogui
from .config import config


logger = logging.getLogger(__name__)


class TextInserter:
    """Handles typing transcribed text at cursor position."""
    
    def __init__(self):
        # Configure pyautogui
        pyautogui.PAUSE = 0.01  # Small pause between actions
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    
    def insert_text(self, text: str) -> bool:
        """Insert text at current cursor position."""
        if not text or not text.strip():
            logger.warning("No text to insert")
            return False
        
        try:
            # Clean up the text
            cleaned_text = self._clean_text(text)
            
            if not cleaned_text:
                logger.warning("No text remaining after cleaning")
                return False
            
            logger.info(f"Inserting text: '{cleaned_text}'")
            
            # Small delay to ensure focus is ready
            time.sleep(0.1)
            
            # Type the text
            pyautogui.typewrite(cleaned_text, interval=0.01)
            
            logger.info("Text insertion completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert text: {e}")
            return False
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text for insertion."""
        # Strip whitespace
        cleaned = text.strip()
        
        # Remove multiple spaces
        while "  " in cleaned:
            cleaned = cleaned.replace("  ", " ")
        
        # Handle common punctuation spacing
        cleaned = cleaned.replace(" .", ".")
        cleaned = cleaned.replace(" ,", ",")
        cleaned = cleaned.replace(" !", "!")
        cleaned = cleaned.replace(" ?", "?")
        cleaned = cleaned.replace(" :", ":")
        cleaned = cleaned.replace(" ;", ";")
        
        # Capitalize first letter if it's a sentence
        if cleaned and cleaned[0].islower():
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned
    
    def test_typing(self) -> bool:
        """Test typing functionality."""
        try:
            test_text = "Voice transcriber test"
            time.sleep(2)  # Give user time to position cursor
            pyautogui.typewrite(test_text)
            return True
        except Exception as e:
            logger.error(f"Typing test failed: {e}")
            return False 