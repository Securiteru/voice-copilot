#!/usr/bin/env python3
"""Test script for the Voice Transcriber API."""

import requests
import tempfile
import numpy as np
from scipy.io import wavfile
import time

def create_test_audio():
    """Create a simple test audio file (silence)."""
    # Create 2 seconds of silence at 16kHz
    sample_rate = 16000
    duration = 2.0
    samples = int(sample_rate * duration)
    
    # Generate some simple audio (sine wave)
    t = np.linspace(0, duration, samples, False)
    frequency = 440  # A4 note
    audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
    
    # Convert to int16
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    temp_filename = temp_file.name
    temp_file.close()
    
    wavfile.write(temp_filename, sample_rate, audio_data)
    return temp_filename

def test_api():
    """Test the Voice Transcriber API."""
    base_url = "http://localhost:12001"
    
    print("🧪 Testing Voice Transcriber API")
    print("=" * 40)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data['status']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return
    
    # Test status endpoint
    print("2. Testing status endpoint...")
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status check passed")
            print(f"   📊 Model: {data['config']['model_name']}")
            print(f"   📊 Sample rate: {data['config']['sample_rate']}")
            print(f"   📊 Model loaded: {data['model_info']['is_loaded']}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
    
    # Test transcription endpoint
    print("3. Testing transcription endpoint...")
    try:
        # Create test audio file
        audio_file = create_test_audio()
        print(f"   📁 Created test audio: {audio_file}")
        
        # Upload and transcribe
        with open(audio_file, 'rb') as f:
            files = {'audio': ('test.wav', f, 'audio/wav')}
            
            print("   🔄 Uploading audio for transcription...")
            start_time = time.time()
            response = requests.post(f"{base_url}/transcribe", files=files)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"   ✅ Transcription successful!")
                    print(f"   📝 Text: '{data['text']}'")
                    print(f"   ⏱️  Processing time: {data['transcription_time']:.2f}s")
                    print(f"   ⏱️  Total time: {end_time - start_time:.2f}s")
                else:
                    print(f"   ⚠️  Transcription returned no text: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Transcription failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
        
        # Clean up
        import os
        os.unlink(audio_file)
        
    except Exception as e:
        print(f"   ❌ Transcription test error: {e}")
    
    print("\n🎉 API testing completed!")

if __name__ == "__main__":
    test_api()