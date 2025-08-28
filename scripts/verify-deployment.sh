#!/bin/bash

# ContractQuard Deployment Verification Script
# This script verifies that both frontend and backend are deployed correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_URL="${FRONTEND_URL:-https://contractquard.vercel.app}"
BACKEND_URL="${BACKEND_URL:-https://contractquard-backend.railway.app}"

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

# Function to check HTTP status
check_url() {
    local url=$1
    local expected_status=${2:-200}
    local description=$3
    
    print_status "Checking $description: $url"
    
    if command -v curl &> /dev/null; then
        status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
        
        if [ "$status_code" = "$expected_status" ]; then
            print_success "$description is accessible (HTTP $status_code)"
            return 0
        else
            print_error "$description returned HTTP $status_code (expected $expected_status)"
            return 1
        fi
    else
        print_warning "curl not available, skipping $description check"
        return 0
    fi
}

# Function to check API endpoint
check_api_endpoint() {
    local endpoint=$1
    local description=$2
    
    print_status "Testing API endpoint: $endpoint"
    
    if command -v curl &> /dev/null; then
        response=$(curl -s "$BACKEND_URL$endpoint" || echo "ERROR")
        
        if [[ "$response" == *"ERROR"* ]]; then
            print_error "API endpoint $endpoint failed"
            return 1
        else
            print_success "API endpoint $endpoint is working"
            return 0
        fi
    else
        print_warning "curl not available, skipping API endpoint check"
        return 0
    fi
}

echo "🚀 ContractQuard Deployment Verification"
echo "========================================"
echo ""

# Check if URLs are provided
if [ -z "$FRONTEND_URL" ] || [ -z "$BACKEND_URL" ]; then
    print_error "Please set FRONTEND_URL and BACKEND_URL environment variables"
    echo "Example:"
    echo "  export FRONTEND_URL=https://your-domain.com"
    echo "  export BACKEND_URL=https://your-backend.railway.app"
    exit 1
fi

echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL: $BACKEND_URL"
echo ""

# Frontend checks
print_status "=== Frontend Verification ==="
check_url "$FRONTEND_URL" 200 "Frontend homepage"
check_url "$FRONTEND_URL/analyze" 200 "Analysis page"

# Backend checks
print_status "=== Backend Verification ==="
check_url "$BACKEND_URL/api/health" 200 "Backend health check"
check_url "$BACKEND_URL/api/docs" 200 "API documentation"

# API endpoint checks
print_status "=== API Endpoint Verification ==="
check_api_endpoint "/api/health" "Health endpoint"
check_api_endpoint "/api/supported-languages" "Supported languages endpoint"

# Security headers check
print_status "=== Security Headers Verification ==="
if command -v curl &> /dev/null; then
    print_status "Checking security headers for frontend..."
    headers=$(curl -s -I "$FRONTEND_URL" || echo "ERROR")
    
    if [[ "$headers" == *"X-Content-Type-Options"* ]]; then
        print_success "X-Content-Type-Options header present"
    else
        print_warning "X-Content-Type-Options header missing"
    fi
    
    if [[ "$headers" == *"X-Frame-Options"* ]]; then
        print_success "X-Frame-Options header present"
    else
        print_warning "X-Frame-Options header missing"
    fi
    
    if [[ "$headers" == *"Strict-Transport-Security"* ]]; then
        print_success "HSTS header present"
    else
        print_warning "HSTS header missing"
    fi
fi

# SSL/TLS check
print_status "=== SSL/TLS Verification ==="
if [[ "$FRONTEND_URL" == https://* ]]; then
    print_success "Frontend uses HTTPS"
else
    print_warning "Frontend not using HTTPS"
fi

if [[ "$BACKEND_URL" == https://* ]]; then
    print_success "Backend uses HTTPS"
else
    print_warning "Backend not using HTTPS"
fi

echo ""
print_success "🎉 Deployment verification completed!"
echo ""
echo "📋 Next Steps:"
echo "  1. Test file upload functionality manually"
echo "  2. Verify analysis workflow end-to-end"
echo "  3. Check error handling and edge cases"
echo "  4. Set up monitoring and alerting"
echo "  5. Configure backup procedures"
echo ""
echo "🔗 Quick Links:"
echo "  • Frontend: $FRONTEND_URL"
echo "  • Backend API: $BACKEND_URL/api/docs"
echo "  • Health Check: $BACKEND_URL/api/health"
