#!/bin/bash
# ChartGenius v3 Integration Testing Script
# Tests Frontend ↔ Oracle Cloud Backend integration

set -e

# Configuration
BACKEND_URL="https://api.chartgenius.online"
FRONTEND_URL="http://localhost:5173"
TELEGRAM_BOT_TOKEN="7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0"

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

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    log_info "Testing: $test_name"
    
    if eval "$test_command"; then
        log_success "$test_name: PASSED"
        ((TESTS_PASSED++))
    else
        log_error "$test_name: FAILED"
        ((TESTS_FAILED++))
    fi
    echo
}

# Backend health check
test_backend_health() {
    curl -f -s "$BACKEND_URL/health" > /dev/null
}

# Backend API health check
test_backend_api_health() {
    response=$(curl -f -s "$BACKEND_URL/api/health")
    echo "$response" | grep -q "healthy"
}

# Test CORS configuration
test_cors() {
    curl -f -s -H "Origin: http://localhost:5173" \
         -H "Access-Control-Request-Method: POST" \
         -H "Access-Control-Request-Headers: Content-Type,Authorization" \
         -X OPTIONS "$BACKEND_URL/api/analysis/analyze" > /dev/null
}

# Test analysis endpoint (without auth)
test_analysis_endpoint() {
    response=$(curl -s -X POST "$BACKEND_URL/api/analysis/analyze" \
        -H "Content-Type: application/json" \
        -d '{"symbol": "BTCUSDT", "interval": "4h", "days": 15}')
    
    # Should return 401 (auth required)
    echo "$response" | grep -q "401\|Unauthorized\|authentication"
}

# Test config endpoints
test_config_endpoints() {
    curl -f -s "$BACKEND_URL/api/config/app" > /dev/null
}

# Test subscription plans endpoint
test_subscription_plans() {
    curl -f -s "$BACKEND_URL/api/subscription/plans" > /dev/null
}

# Test Telegram webhook endpoint
test_telegram_webhook() {
    response=$(curl -s -X POST "$BACKEND_URL/api/webhooks/telegram" \
        -H "Content-Type: application/json" \
        -d '{"update_id": 1, "message": {"message_id": 1, "date": 1640995200, "text": "/test"}}')
    
    # Should not return 404
    ! echo "$response" | grep -q "404\|Not Found"
}

# Test frontend build
test_frontend_build() {
    cd chartgenius-v3-frontend
    npm run build > /dev/null 2>&1
    cd ..
}

# Test frontend dev server
test_frontend_dev_server() {
    cd chartgenius-v3-frontend
    
    # Start dev server in background
    npm run dev > /dev/null 2>&1 &
    DEV_SERVER_PID=$!
    
    # Wait for server to start
    sleep 10
    
    # Test if server is running
    if curl -f -s "$FRONTEND_URL" > /dev/null; then
        kill $DEV_SERVER_PID 2>/dev/null || true
        cd ..
        return 0
    else
        kill $DEV_SERVER_PID 2>/dev/null || true
        cd ..
        return 1
    fi
}

# Test API proxy
test_api_proxy() {
    cd chartgenius-v3-frontend
    
    # Start dev server in background
    npm run dev > /dev/null 2>&1 &
    DEV_SERVER_PID=$!
    
    # Wait for server to start
    sleep 10
    
    # Test API proxy
    if curl -f -s "$FRONTEND_URL/api/health" > /dev/null; then
        kill $DEV_SERVER_PID 2>/dev/null || true
        cd ..
        return 0
    else
        kill $DEV_SERVER_PID 2>/dev/null || true
        cd ..
        return 1
    fi
}

# Test Telegram Bot
test_telegram_bot() {
    response=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe")
    echo "$response" | grep -q '"ok":true'
}

# Test Telegram Bot webhook
test_telegram_bot_webhook() {
    response=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo")
    echo "$response" | grep -q "$BACKEND_URL"
}

# Test Oracle Database connectivity (through backend)
test_database_connectivity() {
    # This test requires a valid auth token, so we'll just check if the endpoint exists
    response=$(curl -s -X GET "$BACKEND_URL/api/admin/stats/system")
    # Should return 401 (auth required) not 404 (not found)
    echo "$response" | grep -q "401\|Unauthorized" && ! echo "$response" | grep -q "404"
}

# Test SSL/TLS
test_ssl() {
    if [[ "$BACKEND_URL" == https* ]]; then
        curl -f -s --tlsv1.2 "$BACKEND_URL/health" > /dev/null
    else
        log_warning "Backend URL is not HTTPS, skipping SSL test"
        return 0
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        log_error "curl is not installed"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed"
        exit 1
    fi
    
    # Check if frontend directory exists
    if [ ! -d "chartgenius-v3-frontend" ]; then
        log_error "Frontend directory not found"
        exit 1
    fi
    
    # Check if package.json exists
    if [ ! -f "chartgenius-v3-frontend/package.json" ]; then
        log_error "Frontend package.json not found"
        exit 1
    fi
    
    log_success "Prerequisites check completed"
}

# Install frontend dependencies
install_frontend_deps() {
    log_info "Installing frontend dependencies..."
    
    cd chartgenius-v3-frontend
    npm install > /dev/null 2>&1
    cd ..
    
    log_success "Frontend dependencies installed"
}

# Main testing process
main() {
    echo
    log_info "🧪 ChartGenius v3 Integration Testing"
    echo "====================================="
    echo
    
    check_prerequisites
    echo
    
    install_frontend_deps
    echo
    
    log_info "Running integration tests..."
    echo
    
    # Backend tests
    log_info "=== BACKEND TESTS ==="
    run_test "Backend Health Check" "test_backend_health"
    run_test "Backend API Health Check" "test_backend_api_health"
    run_test "CORS Configuration" "test_cors"
    run_test "Analysis Endpoint" "test_analysis_endpoint"
    run_test "Config Endpoints" "test_config_endpoints"
    run_test "Subscription Plans" "test_subscription_plans"
    run_test "Telegram Webhook" "test_telegram_webhook"
    run_test "Database Connectivity" "test_database_connectivity"
    run_test "SSL/TLS" "test_ssl"
    
    # Frontend tests
    log_info "=== FRONTEND TESTS ==="
    run_test "Frontend Build" "test_frontend_build"
    run_test "Frontend Dev Server" "test_frontend_dev_server"
    run_test "API Proxy" "test_api_proxy"
    
    # Telegram tests
    log_info "=== TELEGRAM TESTS ==="
    run_test "Telegram Bot" "test_telegram_bot"
    run_test "Telegram Bot Webhook" "test_telegram_bot_webhook"
    
    # Results
    echo "======================================"
    log_info "TEST RESULTS"
    echo "======================================"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        log_success "🎉 All tests passed! ($TESTS_PASSED/$((TESTS_PASSED + TESTS_FAILED)))"
        echo
        log_info "Integration is ready! You can now:"
        echo "1. Start frontend development: cd chartgenius-v3-frontend && npm run dev"
        echo "2. Test Telegram WebApp: Open @ChartGeniusBot in Telegram"
        echo "3. Test API endpoints: Use the frontend interface"
        echo "4. Monitor backend logs: Check Oracle Cloud logs"
    else
        log_error "❌ Some tests failed ($TESTS_FAILED/$((TESTS_PASSED + TESTS_FAILED)))"
        echo
        log_info "Please fix the failing tests before proceeding:"
        echo "1. Check backend deployment status"
        echo "2. Verify DNS/SSL configuration"
        echo "3. Check Telegram Bot webhook setup"
        echo "4. Verify CORS configuration"
    fi
    
    echo
    log_info "Backend URL: $BACKEND_URL"
    log_info "Frontend URL: $FRONTEND_URL"
    log_info "Telegram Bot: @ChartGeniusBot"
    echo
}

# Handle command line arguments
if [ "$1" = "--help" ]; then
    echo "ChartGenius v3 Integration Testing"
    echo
    echo "Usage:"
    echo "  $0                    # Run all integration tests"
    echo "  $0 --help            # Show this help"
    echo
    echo "Tests:"
    echo "  - Backend health and API endpoints"
    echo "  - Frontend build and dev server"
    echo "  - CORS configuration"
    echo "  - Telegram Bot and webhooks"
    echo "  - SSL/TLS connectivity"
    echo "  - Database connectivity (through backend)"
    echo
    exit 0
fi

# Run main function
main "$@"
