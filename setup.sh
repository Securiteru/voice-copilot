#!/bin/bash

# Voice Transcriber Setup Script
# This script configures and installs the voice transcriber service

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/voice_transcriber.env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load environment variables
load_env() {
    if [[ ! -f "$ENV_FILE" ]]; then
        print_error "Environment file not found: $ENV_FILE"
        
        # Check if example file exists
        local example_file="$SCRIPT_DIR/voice_transcriber.env.example"
        if [[ -f "$example_file" ]]; then
            print_status "Example configuration found at: $example_file"
            print_status "Creating your configuration file..."
            
            # Copy example to actual config and set PROJECT_PATH automatically
            cp "$example_file" "$ENV_FILE"
            sed -i "s|PROJECT_PATH=/path/to/your/voice_experiment|PROJECT_PATH=$SCRIPT_DIR|g" "$ENV_FILE"
            
            print_success "Configuration file created at: $ENV_FILE"
            print_status "You can edit this file to customize your settings:"
            echo "  nano $ENV_FILE"
            echo
        else
            print_error "No example configuration found either"
            exit 1
        fi
    fi
    
    print_status "Loading configuration from $ENV_FILE"
    source "$ENV_FILE"
    
    # Set default PROJECT_PATH to current directory if not set
    if [[ -z "$PROJECT_PATH" ]]; then
        PROJECT_PATH="$SCRIPT_DIR"
        print_warning "PROJECT_PATH not set, using current directory: $PROJECT_PATH"
    fi
    
    print_status "Configuration loaded:"
    echo "  Project Path: $PROJECT_PATH"
    echo "  Whisper Model: ${WHISPER_MODEL:-tiny}"
    echo "  Hotkey: ${HOTKEY:-ctrl+f1}"
    echo "  TTS Hotkey: ${TTS_HOTKEY:-ctrl+f2}"
    echo "  System Tray: ${ENABLE_SYSTEM_TRAY:-false}"
    echo "  Debug Mode: ${DEBUG_MODE:-false}"
    echo "  Autostart Method: ${AUTOSTART_METHOD:-systemd}"
}

# Configure service file
configure_service() {
    print_status "Configuring systemd service file..."
    
    local service_template="$SCRIPT_DIR/voice-transcriber.service"
    local service_file="$SCRIPT_DIR/voice-transcriber.service.configured"
    
    if [[ ! -f "$service_template" ]]; then
        print_error "Service template not found: $service_template"
        exit 1
    fi
    
    # Build ExecStart command
    local exec_cmd="$PROJECT_PATH/.venv/bin/python -m voice_transcriber"
    exec_cmd="$exec_cmd --model ${WHISPER_MODEL:-tiny}"
    exec_cmd="$exec_cmd --hotkey '${HOTKEY:-ctrl+f1}'"
    exec_cmd="$exec_cmd --tts-hotkey '${TTS_HOTKEY:-ctrl+f2}'"
    
    if [[ "${ENABLE_SYSTEM_TRAY:-false}" == "false" ]]; then
        exec_cmd="$exec_cmd --no-tray"
    fi
    
    if [[ "${DEBUG_MODE:-false}" == "true" ]]; then
        exec_cmd="$exec_cmd --debug"
    fi
    
    # Replace placeholders in service file
    sed "s|PLACEHOLDER_PROJECT_PATH|$PROJECT_PATH|g" "$service_template" > "$service_file"
    sed -i "s|ExecStart=.*|ExecStart=$exec_cmd|g" "$service_file"
    
    print_success "Service file configured: $service_file"
}

# Configure desktop file
configure_desktop() {
    print_status "Configuring desktop autostart file..."
    
    local desktop_template="$SCRIPT_DIR/voice-transcriber.desktop"
    local desktop_file="$SCRIPT_DIR/voice-transcriber.desktop.configured"
    
    if [[ ! -f "$desktop_template" ]]; then
        print_warning "Desktop template not found: $desktop_template"
        return 1
    fi
    
    # Replace placeholders in desktop file
    sed "s|PLACEHOLDER_PROJECT_PATH|$PROJECT_PATH|g" "$desktop_template" > "$desktop_file"
    
    print_success "Desktop file configured: $desktop_file"
}

# Install systemd service
install_systemd_service() {
    print_status "Installing systemd user service..."
    
    local service_file="$SCRIPT_DIR/voice-transcriber.service.configured"
    local user_service_dir="$HOME/.config/systemd/user"
    
    # Create user service directory
    mkdir -p "$user_service_dir"
    
    # Copy configured service file
    cp "$service_file" "$user_service_dir/voice-transcriber.service"
    
    # Reload systemd and enable service
    systemctl --user daemon-reload
    systemctl --user enable voice-transcriber.service
    
    print_success "Systemd service installed and enabled"
}

# Install desktop autostart
install_desktop_autostart() {
    print_status "Installing desktop autostart..."
    
    local desktop_file="$SCRIPT_DIR/voice-transcriber.desktop.configured"
    local autostart_dir="$HOME/.config/autostart"
    
    if [[ ! -f "$desktop_file" ]]; then
        print_error "Configured desktop file not found: $desktop_file"
        return 1
    fi
    
    # Create autostart directory
    mkdir -p "$autostart_dir"
    
    # Copy configured desktop file
    cp "$desktop_file" "$autostart_dir/voice-transcriber.desktop"
    
    print_success "Desktop autostart installed"
}

# Start service
start_service() {
    if [[ "$AUTOSTART_METHOD" == "systemd" ]]; then
        print_status "Starting systemd service..."
        systemctl --user start voice-transcriber.service
        
        # Check status
        if systemctl --user is-active --quiet voice-transcriber.service; then
            print_success "Service started successfully"
            print_status "Service status:"
            systemctl --user status voice-transcriber.service --no-pager -l
        else
            print_error "Service failed to start"
            print_status "Service logs:"
            journalctl --user -u voice-transcriber.service --no-pager -l
            return 1
        fi
    else
        print_status "Autostart method is '$AUTOSTART_METHOD', not starting service now"
        print_status "Service will start on next login"
    fi
}

# Stop existing service
stop_existing_service() {
    print_status "Stopping any existing voice transcriber processes..."
    
    # Stop systemd service if running
    if systemctl --user is-active --quiet voice-transcriber.service 2>/dev/null; then
        print_status "Stopping existing systemd service..."
        systemctl --user stop voice-transcriber.service
    fi
    
    # Kill any running processes
    pkill -f "python -m voice_transcriber" 2>/dev/null || true
    
    print_success "Existing processes stopped"
}

# Main setup function
main() {
    echo "============================================"
    echo "         Voice Transcriber Setup"
    echo "============================================"
    echo
    
    # Check if we're in the right directory
    if [[ ! -f "$SCRIPT_DIR/pyproject.toml" ]]; then
        print_error "This script must be run from the voice transcriber project directory"
        exit 1
    fi
    
    # Load configuration
    load_env
    echo
    
    # Stop existing services
    stop_existing_service
    echo
    
    # Configure files
    configure_service
    
    if [[ "$AUTOSTART_METHOD" == "desktop" ]]; then
        configure_desktop
    fi
    echo
    
    # Install based on autostart method
    case "$AUTOSTART_METHOD" in
        "systemd")
            install_systemd_service
            echo
            start_service
            ;;
        "desktop")
            install_desktop_autostart
            print_success "Desktop autostart configured. Service will start on next login."
            ;;
        "none")
            print_success "Configuration complete. No autostart method selected."
            print_status "You can manually start the service with:"
            echo "  poetry run voice-transcriber"
            ;;
        *)
            print_warning "Unknown autostart method: $AUTOSTART_METHOD"
            print_status "Available methods: systemd, desktop, none"
            ;;
    esac
    
    echo
    echo "============================================"
    print_success "Setup complete!"
    echo "============================================"
    echo
    print_status "Hotkeys:"
    echo "  Speech-to-Text: ${HOTKEY:-ctrl+f1}"
    echo "  Text-to-Speech: ${TTS_HOTKEY:-ctrl+f2}"
    echo
    print_status "To check service status:"
    echo "  systemctl --user status voice-transcriber.service"
    echo
    print_status "To view logs:"
    echo "  journalctl --user -u voice-transcriber.service -f"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --stop)
            stop_existing_service
            exit 0
            ;;
        --status)
            systemctl --user status voice-transcriber.service
            exit 0
            ;;
        --logs)
            journalctl --user -u voice-transcriber.service -f
            exit 0
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --stop    Stop existing service"
            echo "  --status  Show service status"
            echo "  --logs    Show service logs"
            echo "  --help    Show this help"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# Run main setup
main 