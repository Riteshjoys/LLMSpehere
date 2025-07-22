#!/bin/bash

# Simple Docker Compose startup script
# Alternative to the full start.sh script

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if docker-compose exists
if ! command -v docker-compose >/dev/null 2>&1; then
    print_warning "docker-compose not found, trying docker compose..."
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

case "$1" in
    "start")
        print_info "Starting MongoDB with Docker Compose..."
        $DOCKER_COMPOSE up -d mongodb
        
        print_info "Starting backend manually..."
        cd backend
        source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate
        pip install -r requirements.txt >/dev/null 2>&1
        python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
        BACKEND_PID=$!
        cd ..
        
        print_info "Starting frontend manually..."
        cd frontend
        yarn install >/dev/null 2>&1
        BROWSER=none yarn start &
        FRONTEND_PID=$!
        cd ..
        
        print_success "Services started!"
        print_success "🌐 Frontend: http://localhost:3000"
        print_success "🔧 Backend:  http://localhost:8001"
        print_success "🗄️  MongoDB:  localhost:27017"
        print_warning "Press Ctrl+C to stop"
        
        wait
        ;;
        
    "stop")
        print_info "Stopping all services..."
        $DOCKER_COMPOSE down
        pkill -f "uvicorn server:app" 2>/dev/null || true
        pkill -f "react-scripts start" 2>/dev/null || true
        print_success "All services stopped"
        ;;
        
    "clean")
        print_info "Cleaning up..."
        $DOCKER_COMPOSE down -v
        pkill -f "uvicorn server:app" 2>/dev/null || true
        pkill -f "react-scripts start" 2>/dev/null || true
        print_success "Cleanup completed"
        ;;
        
    *)
        echo "Usage: $0 {start|stop|clean}"
        echo ""
        echo "Commands:"
        echo "  start  - Start MongoDB in Docker, backend and frontend locally"
        echo "  stop   - Stop all services"
        echo "  clean  - Stop services and clean up volumes"
        exit 1
        ;;
esac