#!/bin/bash

# Chronodemica Start Script
# This script starts both backend and frontend services

echo "🚀 Starting Chronodemica..."
echo "=================================="

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    
    # Kill backend processes
    pkill -f "uvicorn.*main:app" 2>/dev/null
    pkill -f "uvicorn" 2>/dev/null
    
    # Kill frontend processes  
    pkill -f "vite.*dev" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    
    # Wait a moment for processes to terminate
    sleep 2
    
    echo "✅ All services stopped"
    exit 0
}

# Set up trap to catch Ctrl+C and call cleanup function
trap cleanup SIGINT SIGTERM EXIT

# Function to check if processes are already running
check_and_stop_existing() {
    echo "🔍 Checking for existing processes..."
    
    # Check for backend processes
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        echo "🛑 Stopping existing backend processes..."
        pkill -f "uvicorn.*main:app" 2>/dev/null
        pkill -f "uvicorn" 2>/dev/null
        sleep 2
    fi
    
    # Check for frontend processes
    if pgrep -f "vite.*dev" > /dev/null; then
        echo "🛑 Stopping existing frontend processes..."
        pkill -f "vite.*dev" 2>/dev/null
        pkill -f "vite" 2>/dev/null
        sleep 2
    fi
    
    echo "✅ Ready to start fresh processes"
}

# Check directories
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found"
    echo "Make sure you're running this script from the project root directory"
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found"
    echo "Make sure you're running this script from the project root directory"
    exit 1
fi

# Check virtual environment
if [ ! -d "backend/venv" ]; then
    echo "❌ Error: Python virtual environment not found"
    echo "Please create it first with: cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Stop any existing processes
check_and_stop_existing

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
fi

echo "🔧 Starting backend server..."
# Start backend in background
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

echo "🎨 Starting frontend server..."
# Start frontend in background
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

echo "=================================="
echo "✅ Services started successfully!"
echo ""
echo "📱 Frontend: http://localhost:5173"
echo "🔗 Backend API: http://localhost:8000" 
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Process IDs:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=================================="

# Keep script running in foreground
echo "📊 Services running... Press Ctrl+C to stop"

# Wait indefinitely for Ctrl+C
while true; do
    sleep 1
    
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "⚠️  Backend process stopped unexpectedly"
        cleanup
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "⚠️  Frontend process stopped unexpectedly"
        cleanup
    fi
done