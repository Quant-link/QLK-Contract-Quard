#!/bin/bash

# ContractQuard Production Deployment Script
set -e

echo "🚀 Deploying ContractQuard to production..."

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

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. Consider using a non-root user for security."
fi

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

# Parse command line arguments
ENVIRONMENT=${1:-production}
DOMAIN=${2:-localhost}
SSL_EMAIL=${3:-admin@example.com}

print_status "Deploying to environment: $ENVIRONMENT"
print_status "Domain: $DOMAIN"

# Create production environment file
print_status "Setting up production environment..."

cat > .env.production << EOF
# Production Environment Variables
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=["https://$DOMAIN", "http://$DOMAIN"]

# Analysis Settings
MAX_FILE_SIZE_MB=10
ANALYSIS_TIMEOUT_SECONDS=300

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Domain Configuration
DOMAIN=$DOMAIN
SSL_EMAIL=$SSL_EMAIL
EOF

# Create nginx configuration for production
print_status "Setting up nginx configuration..."
mkdir -p nginx

cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 10M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=upload:10m rate=2r/s;

    # Upstream servers
    upstream backend {
        server frontend:3000;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name $DOMAIN;
        return 301 https://\$server_name\$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name $DOMAIN;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Main application
        location / {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_cache_bypass \$http_upgrade;
        }

        # API rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Upload endpoint with stricter rate limiting
        location /api/analyze/ {
            limit_req zone=upload burst=5 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # WebSocket
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build production images
print_status "Building production images..."
docker-compose build --no-cache

# Start production services
print_status "Starting production services..."
docker-compose --profile production up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Health checks
print_status "Performing health checks..."

# Check backend
if curl -f http://localhost:8000/api/health &> /dev/null; then
    print_success "Backend is healthy"
else
    print_error "Backend health check failed"
    docker-compose logs backend
    exit 1
fi

# Check frontend
if curl -f http://localhost:3000 &> /dev/null; then
    print_success "Frontend is healthy"
else
    print_error "Frontend health check failed"
    docker-compose logs frontend
    exit 1
fi

# Setup SSL certificates (Let's Encrypt)
if [ "$DOMAIN" != "localhost" ]; then
    print_status "Setting up SSL certificates..."
    
    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        print_status "Installing certbot..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y certbot
        elif command -v yum &> /dev/null; then
            sudo yum install -y certbot
        else
            print_warning "Please install certbot manually"
        fi
    fi
    
    # Generate SSL certificate
    if command -v certbot &> /dev/null; then
        sudo certbot certonly --standalone \
            --email $SSL_EMAIL \
            --agree-tos \
            --no-eff-email \
            -d $DOMAIN
        
        # Copy certificates to nginx directory
        sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/
        sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/
        sudo chown $(whoami):$(whoami) nginx/ssl/*
        
        print_success "SSL certificates installed"
        
        # Restart nginx to use SSL
        docker-compose restart nginx
    fi
else
    print_warning "Skipping SSL setup for localhost"
fi

# Display deployment information
echo ""
print_success "🎉 ContractQuard deployed successfully!"
echo ""
echo "📋 Deployment Information:"
echo "  • Environment: $ENVIRONMENT"
echo "  • Domain: $DOMAIN"
if [ "$DOMAIN" != "localhost" ]; then
    echo "  • Frontend: https://$DOMAIN"
    echo "  • API: https://$DOMAIN/api"
    echo "  • API Docs: https://$DOMAIN/api/docs"
else
    echo "  • Frontend: http://localhost:3000"
    echo "  • API: http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/api/docs"
fi
echo ""
echo "🛠️  Management Commands:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart services: docker-compose restart"
echo "  • Update: git pull && ./scripts/deploy.sh"
echo ""
echo "📊 Monitoring:"
echo "  • Container status: docker-compose ps"
echo "  • Resource usage: docker stats"
echo "  • Health checks: curl -f http://localhost:8000/api/health"
echo ""

print_success "Deployment complete! 🚀"
