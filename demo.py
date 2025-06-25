#!/usr/bin/env python3
"""Demo script showing Voice Copilot mobile app integration."""

import subprocess
import time
import requests
import sys
import os

def check_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    # Check if poetry is available
    try:
        subprocess.run(['poetry', '--version'], capture_output=True, check=True)
        print("   ✅ Poetry found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ❌ Poetry not found. Please install Poetry first.")
        return False
    
    # Check if npm is available (for mobile app)
    try:
        subprocess.run(['npm', '--version'], capture_output=True, check=True)
        print("   ✅ npm found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ⚠️  npm not found. Mobile app setup will be skipped.")
    
    return True

def start_api_server():
    """Start the API server."""
    print("🚀 Starting Voice Copilot API server...")
    
    # Start server in background
    process = subprocess.Popen([
        'poetry', 'run', 'voice-transcriber-api',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--model', 'tiny'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    for i in range(10):
        try:
            response = requests.get('http://localhost:8000/health', timeout=2)
            if response.status_code == 200:
                print("   ✅ API server started successfully")
                return process
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        print(f"   ⏳ Waiting for server to start... ({i+1}/10)")
    
    print("   ❌ Failed to start API server")
    process.terminate()
    return None

def show_network_info():
    """Show network configuration information."""
    print("🌐 Network Configuration:")
    
    try:
        result = subprocess.run(['python3', 'scripts/get-local-ip.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("   ❌ Failed to get network info")
    except Exception as e:
        print(f"   ❌ Error getting network info: {e}")

def test_api():
    """Test the API endpoints."""
    print("🧪 Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health endpoint working")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health endpoint error: {e}")
    
    # Test status
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status endpoint working (model: {data['config']['model_name']})")
        else:
            print(f"   ❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status endpoint error: {e}")

def show_mobile_setup():
    """Show mobile app setup instructions."""
    print("📱 Mobile App Setup:")
    print("   1. Open a new terminal")
    print("   2. cd voice-copilot/mobile-app")
    print("   3. npm install")
    print("   4. npm start")
    print("   5. Install Expo Go on your phone")
    print("   6. Scan the QR code")
    print("   7. Enter server URL: http://YOUR_IP:8000")
    print("")

def show_ngrok_setup():
    """Show ngrok setup instructions."""
    print("🌍 For Internet Access (ngrok):")
    print("   1. Install ngrok: https://ngrok.com/download")
    print("   2. Run: ./scripts/start-with-ngrok.sh")
    print("   3. Use the ngrok URL in your mobile app")
    print("")

def main():
    """Main demo function."""
    print("🎤 Voice Copilot Mobile App Demo")
    print("=" * 50)
    print("")
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    print("")
    
    # Start API server
    server_process = start_api_server()
    if not server_process:
        return 1
    
    print("")
    
    try:
        # Test API
        test_api()
        print("")
        
        # Show network info
        show_network_info()
        print("")
        
        # Show setup instructions
        show_mobile_setup()
        show_ngrok_setup()
        
        print("🎉 Demo setup complete!")
        print("")
        print("The API server is running at: http://localhost:8000")
        print("You can now set up the mobile app following the instructions above.")
        print("")
        print("Press Ctrl+C to stop the server...")
        
        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
    
    finally:
        # Clean up
        if server_process:
            server_process.terminate()
            server_process.wait()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())