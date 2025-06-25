#!/usr/bin/env python3
"""Get local IP address for mobile app configuration."""

import socket
import subprocess
import sys
import platform

def get_local_ip():
    """Get the local IP address."""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to Google DNS (doesn't actually send data)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            return local_ip
    except Exception:
        return None

def get_network_interfaces():
    """Get all network interfaces and their IPs."""
    interfaces = []
    
    try:
        if platform.system() == "Linux":
            # Use ip command on Linux
            result = subprocess.run(['ip', 'addr', 'show'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_interface = None
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith(' '):
                        # Interface line
                        parts = line.split(':')
                        if len(parts) >= 2:
                            current_interface = parts[1].strip()
                    elif 'inet ' in line and current_interface:
                        # IP address line
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == 'inet' and i + 1 < len(parts):
                                ip = parts[i + 1].split('/')[0]
                                if not ip.startswith('127.'):
                                    interfaces.append((current_interface, ip))
                                break
        
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_interface = None
                for line in lines:
                    if line and not line.startswith('\t') and not line.startswith(' '):
                        # Interface line
                        current_interface = line.split(':')[0]
                    elif '\tinet ' in line and current_interface:
                        # IP address line
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            ip = parts[1]
                            if not ip.startswith('127.'):
                                interfaces.append((current_interface, ip))
        
        elif platform.system() == "Windows":
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_interface = None
                for line in lines:
                    line = line.strip()
                    if 'adapter' in line.lower():
                        current_interface = line
                    elif 'IPv4 Address' in line and current_interface:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            ip = parts[1].strip()
                            if not ip.startswith('127.'):
                                interfaces.append((current_interface, ip))
    
    except Exception as e:
        print(f"Error getting network interfaces: {e}")
    
    return interfaces

def main():
    """Main function."""
    print("🌐 Voice Copilot - Network Configuration Helper")
    print("=" * 50)
    
    # Get primary local IP
    local_ip = get_local_ip()
    if local_ip:
        print(f"📍 Primary Local IP: {local_ip}")
        print(f"🔗 Suggested Server URL: http://{local_ip}:8000")
        print()
    
    # Get all network interfaces
    print("📡 All Network Interfaces:")
    interfaces = get_network_interfaces()
    
    if interfaces:
        for interface, ip in interfaces:
            print(f"   {interface}: {ip}")
        print()
        
        # Find WiFi-like interfaces
        wifi_interfaces = [
            (iface, ip) for iface, ip in interfaces 
            if any(keyword in iface.lower() for keyword in ['wlan', 'wifi', 'wireless', 'wi-fi'])
        ]
        
        if wifi_interfaces:
            print("📶 WiFi Interfaces (recommended for mobile):")
            for interface, ip in wifi_interfaces:
                print(f"   {interface}: http://{ip}:8000")
    else:
        print("   No network interfaces found")
    
    print()
    print("📋 Setup Instructions:")
    print("1. Start the Voice Copilot API server:")
    print("   poetry run voice-transcriber-api --host 0.0.0.0 --port 8000")
    print()
    print("2. Use one of the URLs above in your mobile app")
    print()
    print("3. For internet access, use ngrok:")
    print("   ./scripts/start-with-ngrok.sh")

if __name__ == "__main__":
    main()