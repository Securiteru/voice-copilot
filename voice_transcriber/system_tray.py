"""System tray integration for visual feedback."""

import logging
import threading
from typing import Callable, Optional
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem, Menu
from .config import config


logger = logging.getLogger(__name__)


class SystemTray:
    """System tray integration for recording status."""
    
    def __init__(self):
        self.icon: Optional[pystray.Icon] = None
        self.is_running = False
        self.is_recording = False
        self.tray_thread: Optional[threading.Thread] = None
        self.on_quit_callback: Optional[Callable] = None
        
    def start(self, on_quit: Optional[Callable] = None) -> bool:
        """Start system tray icon."""
        if self.is_running:
            return False
            
        self.on_quit_callback = on_quit
        
        try:
            # Create icons
            idle_icon = self._create_icon(color='gray', recording=False)
            recording_icon = self._create_icon(color='red', recording=True)
            
            # Create menu
            menu = Menu(
                MenuItem("Voice Transcriber", None, enabled=False),
                MenuItem("Status: Idle", None, enabled=False),
                Menu.SEPARATOR,
                MenuItem("Quit", self._quit_handler)
            )
            
            # Create tray icon
            self.icon = pystray.Icon(
                "voice-transcriber",
                idle_icon,
                "Voice Transcriber",
                menu
            )
            
            # Start in separate thread
            self.tray_thread = threading.Thread(target=self._run_tray, daemon=True)
            self.tray_thread.start()
            
            self.is_running = True
            logger.info("System tray started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start system tray: {e}")
            return False
    
    def stop(self):
        """Stop system tray icon."""
        if self.icon:
            self.icon.stop()
            
        self.is_running = False
        logger.info("System tray stopped")
    
    def set_recording(self, recording: bool):
        """Update recording status in system tray."""
        if not self.icon or not self.is_running:
            return
            
        self.is_recording = recording
        
        try:
            if recording:
                icon = self._create_icon(color='red', recording=True)
                menu = Menu(
                    MenuItem("Voice Transcriber", None, enabled=False),
                    MenuItem("Status: Recording...", None, enabled=False),
                    Menu.SEPARATOR,
                    MenuItem("Quit", self._quit_handler)
                )
            else:
                icon = self._create_icon(color='gray', recording=False)
                menu = Menu(
                    MenuItem("Voice Transcriber", None, enabled=False),
                    MenuItem("Status: Idle", None, enabled=False),
                    Menu.SEPARATOR,
                    MenuItem("Quit", self._quit_handler)
                )
            
            self.icon.icon = icon
            self.icon.menu = menu
            
        except Exception as e:
            logger.error(f"Failed to update system tray: {e}")
    
    def _create_icon(self, color: str = 'gray', recording: bool = False) -> Image.Image:
        """Create system tray icon."""
        # Create a simple icon
        size = 64
        image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw microphone shape
        mic_color = color
        
        # Microphone body (rectangle with rounded top)
        body_width = size // 3
        body_height = size // 2
        body_x = (size - body_width) // 2
        body_y = size // 4
        
        draw.rounded_rectangle([
            body_x, body_y,
            body_x + body_width, body_y + body_height
        ], radius=body_width//4, fill=mic_color)
        
        # Microphone stand
        stand_width = 4
        stand_height = size // 6
        stand_x = (size - stand_width) // 2
        stand_y = body_y + body_height
        
        draw.rectangle([
            stand_x, stand_y,
            stand_x + stand_width, stand_y + stand_height
        ], fill=mic_color)
        
        # Base
        base_width = size // 2
        base_height = 4
        base_x = (size - base_width) // 2
        base_y = stand_y + stand_height
        
        draw.rectangle([
            base_x, base_y,
            base_x + base_width, base_y + base_height
        ], fill=mic_color)
        
        # Recording indicator (circle)
        if recording:
            indicator_size = 8
            indicator_x = body_x + body_width - indicator_size // 2
            indicator_y = body_y - indicator_size // 2
            
            draw.ellipse([
                indicator_x, indicator_y,
                indicator_x + indicator_size, indicator_y + indicator_size
            ], fill='red')
        
        return image
    
    def _run_tray(self):
        """Run system tray in separate thread."""
        try:
            self.icon.run()
        except Exception as e:
            logger.error(f"System tray error: {e}")
    
    def _quit_handler(self, icon, item):
        """Handle quit menu item."""
        if self.on_quit_callback:
            self.on_quit_callback()
        else:
            self.stop()
    
    def get_status(self) -> dict:
        """Get system tray status."""
        return {
            "is_running": self.is_running,
            "is_recording": self.is_recording
        } 