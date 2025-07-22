#!/bin/bash

# ContentForge AI - Startup Script
# This script starts MongoDB in Docker and runs frontend/backend locally

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
port_available() {
    ! lsof -i:$1 >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Stop MongoDB Docker container
    docker stop contentforge-mongo 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Main startup function
main() {
    print_status "Starting ContentForge AI Application..."
    echo "=================================="
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    if ! command_exists yarn; then
        print_warning "Yarn is not installed. Installing yarn..."
        npm install -g yarn
    fi
    
    # Check if we're in the right directory
    if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        print_error "Please run this script from the project root directory (where backend/ and frontend/ folders exist)"
        exit 1
    fi
    
    print_success "Prerequisites check passed!"
    
    # Start MongoDB in Docker
    print_status "Starting MongoDB in Docker..."
    
    # Stop existing container if running
    docker stop contentforge-mongo 2>/dev/null || true
    docker rm contentforge-mongo 2>/dev/null || true
    
    # Start MongoDB container
    docker run -d \
        --name contentforge-mongo \
        -p 27017:27017 \
        -v contentforge-mongo-data:/data/db \
        -e MONGO_INITDB_ROOT_USERNAME=admin \
        -e MONGO_INITDB_ROOT_PASSWORD=password123 \
        mongo:7.0
    
    # Wait for MongoDB to be ready
    sleep 5
    wait_for_service "http://localhost:27017" "MongoDB"
    
    print_success "MongoDB is running in Docker on port 27017"
    
    # Update backend .env file for Docker MongoDB
    print_status "Updating backend configuration..."
    
    # Backup original .env
    if [ -f "backend/.env.backup" ]; then
        cp backend/.env.backup backend/.env
    else
        cp backend/.env backend/.env.backup
    fi
    
    # Update MongoDB URL for local Docker access
    sed -i.bak 's|MONGO_URL=.*|MONGO_URL=mongodb://localhost:27017|g' backend/.env
    
    # Install backend dependencies
    print_status "Installing backend dependencies..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment and install dependencies
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Install emergent integrations
    pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
    
    cd ..
    print_success "Backend dependencies installed!"
    
    # Install frontend dependencies
    print_status "Installing frontend dependencies..."
    cd frontend
    yarn install
    cd ..
    print_success "Frontend dependencies installed!"
    
    # Start backend server
    print_status "Starting backend server..."
    cd backend
    source .venv/bin/activate
    python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to be ready
    wait_for_service "http://localhost:8001/api/health" "Backend API"
    
    # Start frontend server
    print_status "Starting frontend server..."
    cd frontend
    BROWSER=none yarn start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to be ready
    wait_for_service "http://localhost:3000" "Frontend"
    
    # Print success information
    echo ""
    echo "=================================="
    print_success "ContentForge AI is now running!"
    echo "=================================="
    echo ""
    print_success "🌐 Frontend:     http://localhost:3000"
    print_success "🔧 Backend API:  http://localhost:8001"
    print_success "🗄️  MongoDB:     localhost:27017"
    echo ""
    print_status "📋 Test Credentials:"
    echo "   👤 Admin: admin / admin123"
    echo "   👤 User:  testuser / test123"
    echo ""
    print_status "📝 Logs:"
    echo "   Backend: tail -f backend.log"
    echo "   Frontend: tail -f frontend.log"
    echo ""
    print_warning "Press Ctrl+C to stop all services"
    echo ""
    
    # Keep script running and show logs
    print_status "Showing live logs (Ctrl+C to stop):"
    echo "=================================="
    
    # Show logs in real time
    tail -f backend.log frontend.log 2>/dev/null || true
}

# Check if script is run with --stop flag
if [ "$1" = "--stop" ]; then
    print_status "Stopping all ContentForge services..."
    
    # Kill any running processes
    pkill -f "uvicorn server:app" || true
    pkill -f "react-scripts start" || true
    
    # Stop Docker container
    docker stop contentforge-mongo 2>/dev/null || true
    
    print_success "All services stopped"
    exit 0
fi

# Check if script is run with --clean flag
if [ "$1" = "--clean" ]; then
    print_status "Cleaning up ContentForge data..."
    
    # Stop services
    pkill -f "uvicorn server:app" || true
    pkill -f "react-scripts start" || true
    docker stop contentforge-mongo 2>/dev/null || true
    docker rm contentforge-mongo 2>/dev/null || true
    
    # Remove Docker volume
    docker volume rm contentforge-mongo-data 2>/dev/null || true
    
    # Remove log files
    rm -f backend.log frontend.log
    
    # Restore original .env
    if [ -f "backend/.env.backup" ]; then
        mv backend/.env.backup backend/.env
    fi
    
    print_success "Cleanup completed"
    exit 0
fi

# Show usage if unknown flag
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "ContentForge AI Startup Script"
    echo "Usage:"
    echo "  ./start.sh          Start all services"
    echo "  ./start.sh --stop   Stop all services" 
    echo "  ./start.sh --clean  Clean up data and stop services"
    echo "  ./start.sh --help   Show this help"
    exit 0
fi

# Run main function
main