# Chronodemica - Start Guide

## Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed
- Terminal/Command line

## Starting the Backend

### 1. Navigate to the backend directory
```bash
cd backend
```

### 2. Activate virtual environment
```bash
source venv/bin/activate
```

### 3. Start backend server
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Backend runs on:** http://localhost:8000  
**API Documentation:** http://localhost:8000/docs

---

## Starting the Frontend

### 1. Navigate to the frontend directory (new terminal)
```bash
cd frontend
```

### 2. Install dependencies (only first time)
```bash
npm install
```

### 3. Start frontend server
```bash
npm run dev
```

**Frontend runs on:** http://localhost:5173 (or next available port)

---

## Quick Start (Recommended)

### Using the start script
```bash
./start.sh
```

This script will:
- Start both backend and frontend automatically
- Show live logs from both services
- Clean up all processes when you press Ctrl+C

**Note:** Make sure you're in the project root directory

---

## Manual Start (Alternative)

### Option 1: Two separate terminals
1. **Terminal 1:** Run backend commands
2. **Terminal 2:** Run frontend commands

### Option 2: Using background processes
```bash
# Start backend in background
cd backend && source venv/bin/activate && uvicorn main:app --reload --host 127.0.0.1 --port 8000 &

# Start frontend in background  
cd frontend && npm run dev &
```

---

## Stopping Services

### Kill all processes
```bash
# Stop backend
pkill -f "uvicorn"

# Stop frontend
pkill -f "vite"
```

### Or use Ctrl+C in respective terminals

---

## Troubleshooting

### Port already in use
- Backend: Change port in uvicorn command: `--port 8001`
- Frontend: Vite automatically selects next available port

### Virtual Environment issues
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node Modules issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## URLs after startup
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **SQLite DB:** `backend/chronodemica.db`