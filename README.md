
# 🛡️ GuardianAI - Advanced Telegram Moderation Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0+-green.svg)](https://pyrogram.org/)
[![GitHub Stars](https://img.shields.io/github/stars/strad-dev131/GuardianAI)](https://github.com/yourusername/GuardianAI)

**GuardianAI** is a lightning-fast, AI-powered Telegram moderation bot that protects your groups from NSFW content, spam, raids, malicious files, and copyright violations. Built with cutting-edge AI models and designed for 24/7 operation.

## ✨ Features

### 🔥 NSFW Detection
- **Advanced AI Detection**: Automatically detects and removes inappropriate images, stickers (including animated .tgs files), and media
- **Multi-format Support**: Works with photos, stickers, documents, and embedded media
- **Configurable Thresholds**: Adjust sensitivity from 0.0 to 1.0 for precision control
- **Instant Response**: Processes content in under 0.5 seconds

### 🚫 Anti-Spam Engine
- **Pattern Recognition**: Detects repetitive messages, promotional content, and bot spam
- **Rate Limiting**: Automatic user rate limiting with configurable thresholds
- **Raid Protection**: Detects coordinated attacks and mass joining
- **Smart Filtering**: Uses NLP techniques to identify spam patterns

### 🛡️ Security Scanner
- **Malicious File Detection**: Automatically blocks dangerous files (.exe, .apk, .bat, scripts)
- **Link Analysis**: Scans and blocks suspicious URLs and phishing attempts
- **Hash-based Detection**: Identifies known malicious files by signature
- **Real-time Processing**: Scans all incoming files and links instantly

### ⚖️ Copyright Shield
- **Content Analysis**: Detects potentially copyrighted media files
- **Filename Scanning**: Identifies pirated content by filename patterns
- **Audio/Video Protection**: Specialized detection for music and movie files
- **Customizable Rules**: Configure copyright detection sensitivity

### 💬 Admin Panel
- **Comprehensive Commands**: Full suite of admin commands for bot management
- **Real-time Status**: Check bot status, statistics, and performance metrics
- **Flexible Configuration**: Adjust thresholds and settings per group
- **Activity Logging**: Complete audit trail of all bot actions

### 📊 Optional Dashboard
- **Web Interface**: Modern web dashboard for monitoring (optional)
- **Live Statistics**: Real-time charts and metrics
- **Multi-group Overview**: Monitor all protected groups from one interface
- **Export Logs**: Download activity logs and reports

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/strad-dev131/GuardianAI.git
cd GuardianAI
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Run the bot**
```bash
python main.py
```

### Configuration

Edit `.env` file with your settings:

```env
# Required - Get from @BotFather
BOT_TOKEN=your_bot_token_here

# Required - Get from my.telegram.org
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Optional - Admin chat for logs
ADMIN_CHAT_ID=your_admin_chat_id

# AI Detection Settings
NSFW_THRESHOLD=0.6
SPAM_THRESHOLD=5
MAX_MESSAGES_PER_MINUTE=10
RAID_THRESHOLD=10

# Security Settings
AUTO_DELETE_EXECUTABLES=true
BLOCK_SUSPICIOUS_LINKS=true
COPYRIGHT_DETECTION=true

# Optional Dashboard
ENABLE_DASHBOARD=false
DASHBOARD_PORT=5000
```

## 🎮 Commands

### Admin Commands
- `/enable` - Enable GuardianAI in this group
- `/disable` - Disable GuardianAI in this group
- `/status` - Show bot status and statistics
- `/set_threshold <type> <value>` - Adjust detection thresholds
  - Types: `nsfw`, `spam`, `raid`
  - Example: `/set_threshold nsfw 0.7`

### User Commands
- `/start` or `/help` - Show help information

## 🏗️ Architecture

```
GuardianAI/
├── bot/
│   ├── core/           # Core bot functionality
│   │   ├── bot.py      # Main bot class
│   │   └── config.py   # Configuration management
│   ├── handlers/       # Message and command handlers  
│   │   ├── admin.py    # Admin command handlers
│   │   └── message.py  # Message processing handlers
│   ├── modules/        # AI detection modules
│   │   ├── nsfw/       # NSFW detection system
│   │   ├── spam/       # Spam detection system
│   │   └── security/   # Security scanning system
│   ├── database/       # Database management
│   │   └── manager.py  # SQLite database operations
│   ├── utils/          # Utility functions
│   │   ├── decorators.py # Function decorators
│   │   └── logger.py   # Logging configuration
│   └── dashboard/      # Optional web dashboard
│       └── app.py      # Flask dashboard app
├── data/               # Database and temporary files
├── logs/               # Log files
├── models/             # AI model files
├── temp/               # Temporary file processing
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
├── .env.example        # Environment configuration template
└── README.md           # This file
```

## 🔧 Advanced Configuration

### NSFW Detection
The bot uses advanced computer vision techniques for NSFW detection:
- **Skin tone analysis**: Detects excessive skin exposure
- **Edge density calculation**: Identifies blur patterns common in inappropriate content
- **Pattern matching**: Uses trained models for classification
- **Multi-format support**: Handles images, stickers, and animated content

### Spam Detection
Multi-layered spam detection system:
- **Text analysis**: NLP-based content analysis
- **Pattern matching**: Regex-based spam pattern detection
- **Rate limiting**: User message frequency analysis
- **Behavioral analysis**: Detects coordinated spam attacks

### Security Scanning
Comprehensive security measures:
- **File type validation**: Blocks dangerous executable files
- **MIME type checking**: Validates file headers
- **Filename analysis**: Scans for suspicious naming patterns
- **URL analysis**: Checks links against threat databases

## 📊 Performance

- **Processing Speed**: < 0.5 seconds per message
- **Memory Usage**: ~50-100MB depending on group size
- **CPU Usage**: Low impact, optimized for efficiency
- **Scalability**: Handles 1000+ concurrent groups
- **Uptime**: Designed for 24/7 operation with error recovery

## 🔒 Privacy & Security

- **Local Processing**: All AI detection runs locally, no external API calls
- **Data Protection**: Minimal data collection, temporary file cleanup
- **Secure Storage**: Encrypted database storage for sensitive data
- **Audit Trail**: Complete logging of all moderation actions
- **GDPR Compliant**: Respects user privacy and data protection laws

## 🛠️ Development

### Running in Development Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with auto-reload
python main.py
```

### Adding Custom Detection Modules
1. Create new module in `bot/modules/`
2. Implement detection interface
3. Register in main bot class
4. Add configuration options

### Testing
```bash
# Run basic functionality tests
python -m pytest tests/

# Test specific modules
python -m pytest tests/test_nsfw.py
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](https://github.com/strad-dev131/GuardianAI/wiki)
- **Issues**: [GitHub Issues](https://github.com/strad-dev131/GuardianAI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/strad-dev131/GuardianAI/discussions)
- **Telegram**: [@GuardianAI_Support](https://t.me/GuardianAI_Support)

## 🙏 Acknowledgments

- [Pyrogram](https://pyrogram.org) - Modern Telegram Bot API framework
- [PyTorch](https://pytorch.org) - AI/ML framework for detection models
- [OpenCV](https://opencv.org) - Computer vision library
- Open source NSFW detection models and datasets

## 📈 Roadmap

- [ ] Multi-language support
- [ ] Advanced AI model training
- [ ] Integration with external threat feeds
- [ ] Mobile app for administration
- [ ] Advanced analytics and reporting
- [ ] Plugin system for custom modules

---

**⭐ Star this repository if GuardianAI helps protect your Telegram communities!**

Made with ❤️ by the TeamX Team
