"""Configuration settings for the voice transcriber."""

import os
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Config:
    """Configuration settings for the voice transcriber."""
    
    # Audio settings
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    
    # Whisper settings
    model_name: str = "base"  # tiny, base, small, medium, large
    model_cache_dir: str = os.path.expanduser("~/.cache/whisper")
    
    # Hotkey settings
    hotkey: Tuple[str, ...] = ('ctrl', 'f1')
    tts_hotkey: Tuple[str, ...] = ('ctrl', 'f2')
    
    # UI settings
    show_system_tray: bool = True
    show_notifications: bool = True
    
    # Recording settings
    min_recording_duration: float = 0.5  # seconds
    max_recording_duration: float = 30.0  # seconds
    
    # Debug settings
    debug: bool = False
    save_recordings: bool = False
    recordings_dir: str = os.path.expanduser("~/voice_transcriber_recordings")


# Global config instance
config = Config() 