"""Global hotkey handling for recording activation."""

import logging
import time
from typing import Callable, Optional
from pynput import keyboard
from .config import config


logger = logging.getLogger(__name__)


class HotkeyHandler:
    """Handles global hotkey detection for recording activation."""
    
    def __init__(self):
        self.listener: Optional[keyboard.Listener] = None
        self.on_press_callback: Optional[Callable] = None
        self.on_release_callback: Optional[Callable] = None
        self.on_tts_press_callback: Optional[Callable] = None
        self.is_listening = False
        self.pressed_keys = set()
        self.hotkey_states = {
            'record': False,  # Ctrl+F1 state
            'tts': False      # Ctrl+F2 state
        }
        self.last_tts_trigger = 0  # Debouncing for TTS
        self.tts_debounce_time = 0.5  # 500ms debounce
        
    def start(self, on_press: Callable, on_release: Callable, on_tts_press: Optional[Callable] = None) -> bool:
        """Start listening for hotkeys."""
        if self.is_listening:
            return False
            
        self.on_press_callback = on_press
        self.on_release_callback = on_release
        self.on_tts_press_callback = on_tts_press
        
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.listener.start()
            self.is_listening = True
            
            hotkey_str = "+".join(config.hotkey)
            logger.info(f"Started hotkey listener for: {hotkey_str}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}")
            return False
    
    def stop(self):
        """Stop listening for hotkeys."""
        if self.listener:
            self.listener.stop()
            self.listener = None
        
        self.is_listening = False
        self.pressed_keys.clear()
        logger.info("Stopped hotkey listener")
    
    def _on_key_press(self, key):
        """Handle key press events."""
        try:
            key_name = self._get_key_name(key)
            if key_name:
                self.pressed_keys.add(key_name)
                
                # Check if recording hotkey combination is pressed
                if self._is_record_hotkey_pressed() and not self.hotkey_states['record']:
                    self.hotkey_states['record'] = True
                    if self.on_press_callback:
                        self.on_press_callback()
                
                # Check if TTS hotkey combination is pressed  
                elif self._is_tts_hotkey_pressed() and not self.hotkey_states['tts']:
                    current_time = time.time()
                    if current_time - self.last_tts_trigger > self.tts_debounce_time:
                        self.hotkey_states['tts'] = True
                        self.last_tts_trigger = current_time
                        if self.on_tts_press_callback:
                            self.on_tts_press_callback()
                        
        except Exception as e:
            logger.error(f"Error in key press handler: {e}")
    
    def _on_key_release(self, key):
        """Handle key release events."""
        try:
            key_name = self._get_key_name(key)
            if key_name:
                # Check current states before removing key
                was_record_pressed = self.hotkey_states['record']
                was_tts_pressed = self.hotkey_states['tts']
                
                self.pressed_keys.discard(key_name)
                
                # Update hotkey states
                self.hotkey_states['record'] = self._is_record_hotkey_pressed()
                self.hotkey_states['tts'] = self._is_tts_hotkey_pressed()
                
                # If recording hotkey was pressed and now released, trigger callback
                if was_record_pressed and not self.hotkey_states['record']:
                    if self.on_release_callback:
                        self.on_release_callback()
                        
        except Exception as e:
            logger.error(f"Error in key release handler: {e}")
    
    def _get_key_name(self, key) -> Optional[str]:
        """Get normalized key name."""
        try:
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            elif hasattr(key, 'name'):
                # Map special keys
                key_name = key.name.lower()
                if key_name == 'ctrl_l' or key_name == 'ctrl_r':
                    return 'ctrl'
                elif key_name == 'alt_l' or key_name == 'alt_r':
                    return 'alt'
                elif key_name == 'shift_l' or key_name == 'shift_r':
                    return 'shift'
                elif key_name == 'cmd_l' or key_name == 'cmd_r':
                    return 'cmd'
                else:
                    return key_name
            return None
        except Exception:
            return None
    
    def _is_record_hotkey_pressed(self) -> bool:
        """Check if the recording hotkey combination is currently pressed."""
        hotkey_set = set(config.hotkey)
        return hotkey_set.issubset(self.pressed_keys)
    
    def _is_tts_hotkey_pressed(self) -> bool:
        """Check if the TTS hotkey combination is currently pressed."""
        hotkey_set = set(config.tts_hotkey)
        return hotkey_set.issubset(self.pressed_keys)
    
    def get_status(self) -> dict:
        """Get current status of hotkey handler."""
        return {
            "is_listening": self.is_listening,
            "hotkey": config.hotkey,
            "pressed_keys": list(self.pressed_keys)
        } 