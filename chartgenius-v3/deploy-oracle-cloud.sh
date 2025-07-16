#!/bin/bash
# ChartGenius v3 Oracle Cloud Deployment Script
# Optimized for Always Free Tier

set -e

echo "🚀 ChartGenius v3 Oracle Cloud Deployment"
echo "=========================================="

# Configuration
PROJECT_NAME="chartgenius-v3"
BACKEND_IMAGE="chartgenius-backend"
ORACLE_REGION="eu-frankfurt-1"
COMPARTMENT_NAME="chartgenius"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check OCI CLI
    if ! command -v oci &> /dev/null; then
        log_warning "OCI CLI is not installed. Please install it for full Oracle Cloud integration."
    fi
    
    # Check if .env.production exists
    if [ ! -f "backend/.env.production" ]; then
        log_error "backend/.env.production file not found"
        exit 1
    fi
    
    log_success "Prerequisites check completed"
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."
    
    cd backend
    
    # Build the image
    docker build -t $BACKEND_IMAGE:latest .
    
    # Tag for Oracle Cloud Container Registry
    docker tag $BACKEND_IMAGE:latest $ORACLE_REGION.ocir.io/$COMPARTMENT_NAME/$BACKEND_IMAGE:latest
    docker tag $BACKEND_IMAGE:latest $ORACLE_REGION.ocir.io/$COMPARTMENT_NAME/$BACKEND_IMAGE:v3.0.0
    
    cd ..
    
    log_success "Docker image built successfully"
}

# Test image locally
test_image() {
    log_info "Testing Docker image locally..."
    
    # Stop any existing container
    docker stop chartgenius-test 2>/dev/null || true
    docker rm chartgenius-test 2>/dev/null || true
    
    # Run test container
    docker run -d \
        --name chartgenius-test \
        --env-file backend/.env.production \
        -p 8001:8000 \
        $BACKEND_IMAGE:latest
    
    # Wait for container to start
    sleep 10
    
    # Test health endpoint
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        log_success "Container health check passed"
    else
        log_error "Container health check failed"
        docker logs chartgenius-test
        docker stop chartgenius-test
        docker rm chartgenius-test
        exit 1
    fi
    
    # Cleanup test container
    docker stop chartgenius-test
    docker rm chartgenius-test
    
    log_success "Local image test completed"
}

# Push to Oracle Container Registry
push_to_registry() {
    log_info "Pushing to Oracle Container Registry..."
    
    # Login to OCIR (requires OCI CLI configuration)
    if command -v oci &> /dev/null; then
        log_info "Logging into Oracle Container Registry..."
        
        # Get auth token
        AUTH_TOKEN=$(oci iam auth-token create --description "ChartGenius v3 deployment" --query 'data.token' --raw-output 2>/dev/null || echo "")
        
        if [ -n "$AUTH_TOKEN" ]; then
            echo $AUTH_TOKEN | docker login $ORACLE_REGION.ocir.io -u $(oci iam user get --user-id $(oci iam user list --query 'data[0].id' --raw-output) --query 'data.name' --raw-output) --password-stdin
        else
            log_warning "Could not get auth token. Please login manually:"
            echo "docker login $ORACLE_REGION.ocir.io"
        fi
        
        # Push images
        docker push $ORACLE_REGION.ocir.io/$COMPARTMENT_NAME/$BACKEND_IMAGE:latest
        docker push $ORACLE_REGION.ocir.io/$COMPARTMENT_NAME/$BACKEND_IMAGE:v3.0.0
        
        log_success "Images pushed to Oracle Container Registry"
    else
        log_warning "OCI CLI not available. Skipping registry push."
        log_info "To push manually:"
        echo "1. docker login $ORACLE_REGION.ocir.io"
        echo "2. docker push $ORACLE_REGION.ocir.io/$COMPARTMENT_NAME/$BACKEND_IMAGE:latest"
    fi
}

# Deploy to Oracle Cloud
deploy_to_cloud() {
    log_info "Deploying to Oracle Cloud..."
    
    if command -v kubectl &> /dev/null; then
        # Deploy using Kubernetes
        log_info "Deploying with Kubernetes..."
        kubectl apply -f oracle-cloud-deployment.yml
        
        # Wait for deployment
        kubectl rollout status deployment/chartgenius-backend --timeout=300s
        
        # Get service URL
        SERVICE_URL=$(kubectl get service chartgenius-backend-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
        
        if [ "$SERVICE_URL" != "pending" ] && [ -n "$SERVICE_URL" ]; then
            log_success "Deployment completed. Service URL: http://$SERVICE_URL"
        else
            log_info "Deployment completed. Service URL is pending. Check with: kubectl get services"
        fi
    else
        log_warning "kubectl not available. Using Docker Compose for local deployment..."
        
        # Use Docker Compose for local/VM deployment
        docker-compose -f docker-compose.yml up -d
        
        log_success "Local deployment completed. Backend available at: http://localhost:8000"
    fi
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create monitoring directory
    mkdir -p monitoring/logs
    
    # Setup log rotation
    cat > monitoring/logrotate.conf << EOF
/app/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 chartgenius chartgenius
}
EOF
    
    log_success "Monitoring setup completed"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Test health endpoint
    if command -v kubectl &> /dev/null; then
        # Get service endpoint
        SERVICE_IP=$(kubectl get service chartgenius-backend-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
        
        if [ -n "$SERVICE_IP" ]; then
            HEALTH_URL="http://$SERVICE_IP/health"
        else
            log_warning "Service IP not available yet. Using port-forward for testing..."
            kubectl port-forward service/chartgenius-backend-service 8002:80 &
            PORT_FORWARD_PID=$!
            sleep 5
            HEALTH_URL="http://localhost:8002/health"
        fi
    else
        HEALTH_URL="http://localhost:8000/health"
    fi
    
    # Test health endpoint
    if curl -f $HEALTH_URL > /dev/null 2>&1; then
        log_success "Deployment verification passed"
        
        # Test API endpoint
        if curl -f $HEALTH_URL | grep -q "healthy"; then
            log_success "API is responding correctly"
        fi
    else
        log_error "Deployment verification failed"
        
        # Show logs for debugging
        if command -v kubectl &> /dev/null; then
            kubectl logs deployment/chartgenius-backend --tail=50
        else
            docker-compose logs backend
        fi
    fi
    
    # Cleanup port-forward if used
    if [ -n "$PORT_FORWARD_PID" ]; then
        kill $PORT_FORWARD_PID 2>/dev/null || true
    fi
}

# Main deployment process
main() {
    echo
    log_info "Starting ChartGenius v3 deployment process..."
    echo
    
    check_prerequisites
    echo
    
    build_image
    echo
    
    test_image
    echo
    
    push_to_registry
    echo
    
    deploy_to_cloud
    echo
    
    setup_monitoring
    echo
    
    verify_deployment
    echo
    
    log_success "🎉 ChartGenius v3 deployment completed!"
    echo
    echo "Next steps:"
    echo "1. Configure domain DNS to point to the service IP"
    echo "2. Setup SSL certificates"
    echo "3. Configure Telegram Bot webhooks"
    echo "4. Test frontend integration"
    echo
}

# Run main function
main "$@"
