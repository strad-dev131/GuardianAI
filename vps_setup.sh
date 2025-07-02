
#!/bin/bash

# GuardianAI VPS Setup Script
# Automated installation script for Ubuntu 22.04+

set -e

echo "🛡️ GuardianAI VPS Setup Script"
echo "==============================="

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
    print_error "Please run this script as a regular user, not root"
    exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+ and pip
print_status "Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y git curl wget unzip

# Install additional dependencies for image processing
print_status "Installing image processing libraries..."
sudo apt install -y libmagic1 libmagic-dev
sudo apt install -y libopencv-dev python3-opencv

# Install PM2 for process management
print_status "Installing PM2 for process management..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2

# Create application directory
APP_DIR="$HOME/GuardianAI"
print_status "Setting up application directory at $APP_DIR..."

if [ -d "$APP_DIR" ]; then
    print_warning "Directory $APP_DIR already exists. Backing up..."
    mv "$APP_DIR" "$APP_DIR.backup.$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Clone repository (if not already present)
if [ ! -f "main.py" ]; then
    print_status "Downloading GuardianAI source code..."
    # In a real scenario, clone from actual repository
    # git clone https://github.com/yourusername/GuardianAI.git .
    
    # For now, assume files are already present or copied
    print_warning "Please ensure GuardianAI source files are in $APP_DIR"
fi

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
else
    print_error "requirements.txt not found. Please ensure it exists in $APP_DIR"
    exit 1
fi

# Create necessary directories
print_status "Creating application directories..."
mkdir -p data logs temp models

# Set up configuration
print_status "Setting up configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Created .env from example. Please edit it with your credentials:"
        print_warning "  BOT_TOKEN - Get from @BotFather"
        print_warning "  API_ID and API_HASH - Get from my.telegram.org"
        print_warning "  Other settings as needed"
    else
        print_error ".env.example not found. Please create .env manually"
    fi
fi

# Create systemd service file
print_status "Creating systemd service..."
SERVICE_FILE="/tmp/guardian-ai.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=GuardianAI Telegram Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo mv "$SERVICE_FILE" /etc/systemd/system/guardian-ai.service
sudo systemctl daemon-reload

# Create PM2 ecosystem file
print_status "Creating PM2 configuration..."
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'guardian-ai',
    script: '$APP_DIR/venv/bin/python',
    args: 'main.py',
    cwd: '$APP_DIR',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production'
    },
    error_file: '$APP_DIR/logs/pm2-error.log',
    out_file: '$APP_DIR/logs/pm2-out.log',
    log_file: '$APP_DIR/logs/pm2-combined.log',
    time: true
  }]
};
EOF

# Set up log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/guardian-ai > /dev/null << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        systemctl reload guardian-ai || true
    endscript
}
EOF

# Create startup script
print_status "Creating startup script..."
cat > start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python main.py
EOF

chmod +x start.sh

# Create backup script
print_status "Creating backup script..."
cat > backup.sh << EOF
#!/bin/bash
# GuardianAI Backup Script

BACKUP_DIR="$HOME/guardian-ai-backups"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="guardian-ai-backup-\$DATE.tar.gz"

mkdir -p "\$BACKUP_DIR"

echo "Creating backup..."
tar -czf "\$BACKUP_DIR/\$BACKUP_FILE" \\
    --exclude='venv' \\
    --exclude='temp/*' \\
    --exclude='*.pyc' \\
    --exclude='__pycache__' \\
    -C "$HOME" GuardianAI/

echo "Backup created: \$BACKUP_DIR/\$BACKUP_FILE"

# Keep only last 7 backups
cd "\$BACKUP_DIR"
ls -t guardian-ai-backup-*.tar.gz | tail -n +8 | xargs -r rm --

echo "Backup completed successfully"
EOF

chmod +x backup.sh

# Set up cron for automatic backups
print_status "Setting up automatic backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh >> $APP_DIR/logs/backup.log 2>&1") | crontab -

# Configure firewall (if ufw is available)
if command -v ufw >/dev/null 2>&1; then
    print_status "Configuring firewall..."
    sudo ufw allow ssh
    sudo ufw allow 5000/tcp comment "GuardianAI Dashboard"
    sudo ufw --force enable
fi

# Final setup instructions
print_success "✅ GuardianAI VPS setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit the configuration file:"
echo "   nano $APP_DIR/.env"
echo ""
echo "2. Start the bot using one of these methods:"
echo ""
echo "   🔸 Using systemd (recommended for production):"
echo "   sudo systemctl enable guardian-ai"
echo "   sudo systemctl start guardian-ai"
echo "   sudo systemctl status guardian-ai"
echo ""
echo "   🔸 Using PM2:"
echo "   pm2 start ecosystem.config.js"
echo "   pm2 save"
echo "   pm2 startup"
echo ""
echo "   🔸 Manual start (for testing):"
echo "   cd $APP_DIR && ./start.sh"
echo ""
echo "3. Monitor logs:"
echo "   tail -f $APP_DIR/logs/guardian.log"
echo "   sudo journalctl -u guardian-ai -f"
echo "   pm2 logs guardian-ai"
echo ""
echo "4. Access dashboard (if enabled):"
echo "   http://your-server-ip:5000"
echo ""
echo "🔧 Useful commands:"
echo "   - Check bot status: sudo systemctl status guardian-ai"
echo "   - Restart bot: sudo systemctl restart guardian-ai"
echo "   - View logs: sudo journalctl -u guardian-ai -f"
echo "   - Create backup: $APP_DIR/backup.sh"
echo ""
print_success "GuardianAI is ready to protect your Telegram groups! 🛡️"
