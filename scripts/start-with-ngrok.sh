#!/bin/bash

# Start Voice Copilot with ngrok tunnel for mobile access
# This script starts both the API server and creates an ngrok tunnel

set -e

# Default values
PORT=8000
MODEL="base"
NGROK_REGION="us"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --region)
            NGROK_REGION="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --port PORT       Port to run API server on (default: 8000)"
            echo "  --model MODEL     Whisper model to use (default: base)"
            echo "  --region REGION   ngrok region (default: us)"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🎤 Starting Voice Copilot with ngrok tunnel..."
echo "Port: $PORT"
echo "Model: $MODEL"
echo "Region: $NGROK_REGION"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed. Please install it from https://ngrok.com/download"
    exit 1
fi

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install it first."
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    if [[ -n $API_PID ]]; then
        kill $API_PID 2>/dev/null || true
    fi
    if [[ -n $NGROK_PID ]]; then
        kill $NGROK_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the API server in background
echo "🚀 Starting Voice Copilot API server..."
poetry run voice-transcriber-api --host 0.0.0.0 --port $PORT --model $MODEL &
API_PID=$!

# Wait a moment for the server to start
sleep 3

# Check if API server is running
if ! kill -0 $API_PID 2>/dev/null; then
    echo "❌ Failed to start API server"
    exit 1
fi

echo "✅ API server started (PID: $API_PID)"

# Start ngrok tunnel
echo "🌐 Starting ngrok tunnel..."
ngrok http $PORT --region $NGROK_REGION &
NGROK_PID=$!

# Wait a moment for ngrok to start
sleep 3

# Check if ngrok is running
if ! kill -0 $NGROK_PID 2>/dev/null; then
    echo "❌ Failed to start ngrok tunnel"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

echo "✅ ngrok tunnel started (PID: $NGROK_PID)"
echo ""

# Try to get the ngrok URL
sleep 2
NGROK_URL=""
for i in {1..10}; do
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o 'https://[^"]*\.ngrok\.io' | head -1 || true)
    if [[ -n $NGROK_URL ]]; then
        break
    fi
    sleep 1
done

if [[ -n $NGROK_URL ]]; then
    echo "🎉 Voice Copilot is now accessible at:"
    echo "   $NGROK_URL"
    echo ""
    echo "📱 Use this URL in your mobile app!"
    echo ""
    echo "🔗 ngrok dashboard: http://localhost:4040"
else
    echo "⚠️  Could not retrieve ngrok URL automatically."
    echo "   Check the ngrok dashboard at: http://localhost:4040"
fi

echo ""
echo "📋 Service Status:"
echo "   API Server: http://localhost:$PORT (PID: $API_PID)"
echo "   ngrok Tunnel: Running (PID: $NGROK_PID)"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
wait