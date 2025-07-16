#!/bin/bash
# ChartGenius v3 Telegram Bot Setup Script
# Configures webhooks and bot settings for Oracle Cloud deployment

set -e

# Configuration
BOT_TOKEN="7279183061:AAERodVAje0VnifJmUJWeq0EM4FxMueXrB0"
WEBHOOK_URL="https://api.chartgenius.online/api/webhooks/telegram"
WEBAPP_URL="https://chartgenius.online"
BOT_USERNAME="ChartGeniusBot"

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
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        log_error "curl is not installed"
        exit 1
    fi
    
    # Check jq for JSON parsing
    if ! command -v jq &> /dev/null; then
        log_warning "jq is not installed. JSON responses will not be formatted."
        JQ_AVAILABLE=false
    else
        JQ_AVAILABLE=true
    fi
    
    log_success "Prerequisites check completed"
}

# Get bot info
get_bot_info() {
    log_info "Getting bot information..."
    
    response=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getMe")
    
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$response" | jq '.'
        
        # Check if bot is valid
        if echo "$response" | jq -e '.ok' > /dev/null; then
            bot_username=$(echo "$response" | jq -r '.result.username')
            log_success "Bot is valid: @$bot_username"
        else
            log_error "Invalid bot token"
            exit 1
        fi
    else
        echo "$response"
    fi
}

# Set webhook
set_webhook() {
    log_info "Setting webhook URL: $WEBHOOK_URL"
    
    response=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
        -H "Content-Type: application/json" \
        -d "{
            \"url\": \"$WEBHOOK_URL\",
            \"allowed_updates\": [\"message\", \"callback_query\", \"pre_checkout_query\", \"successful_payment\"],
            \"drop_pending_updates\": true
        }")
    
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$response" | jq '.'
        
        if echo "$response" | jq -e '.ok' > /dev/null; then
            log_success "Webhook set successfully"
        else
            log_error "Failed to set webhook"
            exit 1
        fi
    else
        echo "$response"
    fi
}

# Get webhook info
get_webhook_info() {
    log_info "Getting webhook information..."
    
    response=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo")
    
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$response" | jq '.'
        
        # Check webhook status
        if echo "$response" | jq -e '.result.url' > /dev/null; then
            webhook_url=$(echo "$response" | jq -r '.result.url')
            pending_updates=$(echo "$response" | jq -r '.result.pending_update_count')
            
            if [ "$webhook_url" = "$WEBHOOK_URL" ]; then
                log_success "Webhook is correctly configured"
                log_info "Pending updates: $pending_updates"
            else
                log_warning "Webhook URL mismatch. Expected: $WEBHOOK_URL, Got: $webhook_url"
            fi
        else
            log_warning "No webhook is set"
        fi
    else
        echo "$response"
    fi
}

# Set bot commands
set_bot_commands() {
    log_info "Setting bot commands..."
    
    response=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setMyCommands" \
        -H "Content-Type: application/json" \
        -d '{
            "commands": [
                {
                    "command": "start",
                    "description": "🚀 Запустить ChartGenius"
                },
                {
                    "command": "analyze",
                    "description": "📊 Анализ криптовалюты"
                },
                {
                    "command": "subscription",
                    "description": "💎 Управление подпиской"
                },
                {
                    "command": "history",
                    "description": "📈 История анализов"
                },
                {
                    "command": "help",
                    "description": "❓ Помощь"
                }
            ]
        }')
    
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$response" | jq '.'
        
        if echo "$response" | jq -e '.ok' > /dev/null; then
            log_success "Bot commands set successfully"
        else
            log_error "Failed to set bot commands"
        fi
    else
        echo "$response"
    fi
}

# Set bot description
set_bot_description() {
    log_info "Setting bot description..."
    
    description="🤖 ChartGenius v3 - Профессиональный технический анализ криптовалют с помощью ИИ

📊 Получайте детальный анализ 24 индикаторов
💎 Telegram Stars платежи
🚀 Современный интерфейс WebApp

Нажмите /start для начала работы!"

    response=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setMyDescription" \
        -H "Content-Type: application/json" \
        -d "{\"description\": \"$description\"}")
    
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$response" | jq '.'
        
        if echo "$response" | jq -e '.ok' > /dev/null; then
            log_success "Bot description set successfully"
        else
            log_error "Failed to set bot description"
        fi
    else
        echo "$response"
    fi
}

# Set bot short description
set_bot_short_description() {
    log_info "Setting bot short description..."
    
    short_description="🤖 Профессиональный технический анализ криптовалют с ИИ"
    
    response=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setMyShortDescription" \
        -H "Content-Type: application/json" \
        -d "{\"short_description\": \"$short_description\"}")
    
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$response" | jq '.'
        
        if echo "$response" | jq -e '.ok' > /dev/null; then
            log_success "Bot short description set successfully"
        else
            log_error "Failed to set bot short description"
        fi
    else
        echo "$response"
    fi
}

# Test webhook
test_webhook() {
    log_info "Testing webhook connectivity..."
    
    # Test if webhook URL is accessible
    if curl -f -s "$WEBHOOK_URL" > /dev/null; then
        log_success "Webhook URL is accessible"
    else
        log_warning "Webhook URL is not accessible. Make sure the backend is deployed and running."
    fi
    
    # Send test update
    log_info "You can test the bot by sending a message to @$BOT_USERNAME"
}

# Create bot menu button
set_menu_button() {
    log_info "Setting bot menu button..."
    
    response=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setChatMenuButton" \
        -H "Content-Type: application/json" \
        -d "{
            \"menu_button\": {
                \"type\": \"web_app\",
                \"text\": \"📊 Открыть ChartGenius\",
                \"web_app\": {
                    \"url\": \"$WEBAPP_URL\"
                }
            }
        }")
    
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$response" | jq '.'
        
        if echo "$response" | jq -e '.ok' > /dev/null; then
            log_success "Bot menu button set successfully"
        else
            log_error "Failed to set bot menu button"
        fi
    else
        echo "$response"
    fi
}

# Delete webhook (for testing)
delete_webhook() {
    log_warning "Deleting webhook..."
    
    response=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook" \
        -H "Content-Type: application/json" \
        -d '{"drop_pending_updates": true}')
    
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$response" | jq '.'
        
        if echo "$response" | jq -e '.ok' > /dev/null; then
            log_success "Webhook deleted successfully"
        else
            log_error "Failed to delete webhook"
        fi
    else
        echo "$response"
    fi
}

# Main setup process
main() {
    echo
    log_info "🤖 ChartGenius v3 Telegram Bot Setup"
    echo "======================================"
    echo
    
    check_prerequisites
    echo
    
    get_bot_info
    echo
    
    if [ "$1" = "--delete-webhook" ]; then
        delete_webhook
        echo
        log_info "Webhook deleted. You can now use polling mode for testing."
        exit 0
    fi
    
    set_webhook
    echo
    
    get_webhook_info
    echo
    
    set_bot_commands
    echo
    
    set_bot_description
    echo
    
    set_bot_short_description
    echo
    
    set_menu_button
    echo
    
    test_webhook
    echo
    
    log_success "🎉 Telegram Bot setup completed!"
    echo
    echo "Bot Information:"
    echo "- Username: @$BOT_USERNAME"
    echo "- Webhook URL: $WEBHOOK_URL"
    echo "- WebApp URL: $WEBAPP_URL"
    echo
    echo "Next steps:"
    echo "1. Test the bot by sending /start to @$BOT_USERNAME"
    echo "2. Verify webhook is receiving updates"
    echo "3. Test WebApp functionality"
    echo "4. Configure payment provider for Telegram Stars"
    echo
}

# Handle command line arguments
if [ "$1" = "--help" ]; then
    echo "ChartGenius v3 Telegram Bot Setup"
    echo
    echo "Usage:"
    echo "  $0                    # Setup bot with webhook"
    echo "  $0 --delete-webhook   # Delete webhook (for testing)"
    echo "  $0 --help            # Show this help"
    echo
    exit 0
fi

# Run main function
main "$@"
