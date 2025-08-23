#!/bin/bash

# ContractQuard Development Setup Script
set -e

echo "🚀 Setting up ContractQuard development environment..."

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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Node.js is installed (for local development)
if ! command -v node &> /dev/null; then
    print_warning "Node.js is not installed. You can still use Docker for development."
else
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION is installed"
fi

# Check if Python is installed (for local development)
if ! command -v python3 &> /dev/null; then
    print_warning "Python 3 is not installed. You can still use Docker for development."
else
    PYTHON_VERSION=$(python3 --version)
    print_success "$PYTHON_VERSION is installed"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p nginx/ssl

# Set up environment files
print_status "Setting up environment files..."

# Backend environment
cat > .env.backend << EOF
# Backend Environment Variables
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Analysis Settings
MAX_FILE_SIZE_MB=10
ANALYSIS_TIMEOUT_SECONDS=300

# Redis Configuration (optional)
REDIS_URL=redis://redis:6379/0
EOF

# Frontend environment
cat > web/frontend/.env << EOF
# Frontend Environment Variables
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=ContractQuard
VITE_APP_VERSION=0.1.0
EOF

print_success "Environment files created"

# Install Python dependencies locally (optional)
if command -v python3 &> /dev/null && command -v pip &> /dev/null; then
    print_status "Installing Python dependencies locally..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment and install dependencies
    source .venv/bin/activate
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_warning "Skipping local Python setup. Using Docker instead."
fi

# Install Node.js dependencies locally (optional)
if command -v node &> /dev/null && command -v npm &> /dev/null; then
    print_status "Installing Node.js dependencies locally..."
    cd web/frontend
    npm install
    cd ../..
    print_success "Node.js dependencies installed"
else
    print_warning "Skipping local Node.js setup. Using Docker instead."
fi

# Build and start development containers
print_status "Building and starting development containers..."
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check if services are running
if curl -f http://localhost:8000/api/health &> /dev/null; then
    print_success "Backend is running at http://localhost:8000"
else
    print_error "Backend failed to start"
fi

if curl -f http://localhost:3000 &> /dev/null; then
    print_success "Frontend is running at http://localhost:3000"
else
    print_warning "Frontend may still be starting up. Check http://localhost:3000 in a few moments."
fi

# Display useful information
echo ""
echo "🎉 ContractQuard development environment is ready!"
echo ""
echo "📋 Quick Start:"
echo "  • Frontend: http://localhost:3000"
echo "  • Backend API: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/api/docs"
echo "  • Redis: localhost:6379"
echo ""
echo "🛠️  Development Commands:"
echo "  • View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "  • Stop services: docker-compose -f docker-compose.dev.yml down"
echo "  • Restart services: docker-compose -f docker-compose.dev.yml restart"
echo "  • Rebuild: docker-compose -f docker-compose.dev.yml build --no-cache"
echo ""
echo "🧪 Testing:"
echo "  • Run backend tests: docker-compose -f docker-compose.dev.yml exec backend python -m pytest"
echo "  • Run frontend tests: docker-compose -f docker-compose.dev.yml exec frontend npm test"
echo ""
echo "📁 Project Structure:"
echo "  • Backend code: src/"
echo "  • Frontend code: web/frontend/src/"
echo "  • API endpoints: web/backend/"
echo "  • Docker configs: docker-compose*.yml"
echo ""

print_success "Setup complete! Happy coding! 🚀"
