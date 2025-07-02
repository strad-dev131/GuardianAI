"""
Configuration management for GuardianAI
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

@dataclass
class Config:
    """Bot configuration data class"""

    # Telegram Bot Settings
    bot_token: str
    api_id: int
    api_hash: str
    bot_name: str = "GuardianAI"
    admin_chat_id: Optional[int] = None

    # AI Detection Settings
    nsfw_threshold: float = 0.6
    nsfw_model_path: str = "models/nsfw_model.onnx"

    # Spam Detection
    spam_threshold: int = 5
    max_messages_per_minute: int = 10
    raid_threshold: int = 10

    # Security Settings
    auto_delete_executables: bool = True
    block_suspicious_links: bool = True
    copyright_detection: bool = True

    # Database
    database_path: str = "data/guardian.db"

    # Web Dashboard
    enable_dashboard: bool = False
    dashboard_port: int = 5000
    dashboard_host: str = "0.0.0.0"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/guardian.log"

def load_config() -> Config:
    """Load configuration from environment variables"""

    # Load .env file if it exists
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)

    try:
        # Get required values with better error handling
        bot_token = os.getenv("BOT_TOKEN", "").strip()
        api_id_str = os.getenv("API_ID", "0")
        api_hash = os.getenv("API_HASH", "").strip()

        # Convert API_ID safely
        try:
            api_id = int(api_id_str) if api_id_str else 0
        except ValueError:
            raise ValueError(f"API_ID must be a number, got: {api_id_str}")

        # Handle admin chat ID safely
        admin_chat_id = None
        admin_chat_str = os.getenv("ADMIN_CHAT_ID", "").strip()
        if admin_chat_str:
            try:
                admin_chat_id = int(admin_chat_str)
            except ValueError:
                raise ValueError(f"ADMIN_CHAT_ID must be a number, got: {admin_chat_str}")

        config = Config(
            bot_token=bot_token,
            api_id=api_id,
            api_hash=api_hash,
            bot_name=os.getenv("BOT_NAME", "GuardianAI"),
            admin_chat_id=admin_chat_id,

            nsfw_threshold=float(os.getenv("NSFW_THRESHOLD", "0.6")),
            nsfw_model_path=os.getenv("NSFW_MODEL_PATH", "models/nsfw_model.onnx"),

            spam_threshold=int(os.getenv("SPAM_THRESHOLD", "5")),
            max_messages_per_minute=int(os.getenv("MAX_MESSAGES_PER_MINUTE", "10")),
            raid_threshold=int(os.getenv("RAID_THRESHOLD", "10")),

            auto_delete_executables=(os.getenv("AUTO_DELETE_EXECUTABLES") or "true").lower() == "true",
            block_suspicious_links=(os.getenv("BLOCK_SUSPICIOUS_LINKS") or "true").lower() == "true",
            copyright_detection=(os.getenv("COPYRIGHT_DETECTION") or "true").lower() == "true",

            database_path=os.getenv("DATABASE_PATH", "data/guardian.db"),

            enable_dashboard=(os.getenv("ENABLE_DASHBOARD") or "false").lower() == "true",
            dashboard_port=int(os.getenv("DASHBOARD_PORT", "5000")),
            dashboard_host=os.getenv("DASHBOARD_HOST", "0.0.0.0"),

            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "logs/guardian.log")
        )

        # Validate required fields
        if not config.bot_token:
            raise ValueError("BOT_TOKEN is required")
        if not config.api_id:
            raise ValueError("API_ID is required")
        if not config.api_hash:
            raise ValueError("API_HASH is required")

        return config

    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid configuration: {e}")

def create_directories(config: Config):
    """Create necessary directories"""
    directories = [
        Path(config.database_path).parent,
        Path(config.log_file).parent,
        Path(config.nsfw_model_path).parent,
        Path("temp"),
        Path("data"),
        Path("logs"),
        Path("models")
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
