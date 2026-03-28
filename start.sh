#!/bin/bash
# Waypoint 360 -- Development Server Startup
# Starts both backend (FastAPI) and frontend (Vite) dev servers

set -e

echo "Starting Waypoint 360..."

# Backend
echo "  Starting backend on :8000..."
cd backend
rm -f /tmp/waypoint360.db
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

sleep 3

# Seed database
echo "  Seeding database..."
curl -s -X POST http://localhost:8000/api/v1/program/seed > /dev/null

# Frontend
echo "  Starting frontend on :5173..."
cd frontend
npx vite --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
cd ..

echo ""
echo "Waypoint 360 is running:"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
