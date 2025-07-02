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
    
    def safe_getenv(key: str, default: str = "") -> str:
        """Safely get environment variable with proper null handling"""
        value = os.getenv(key)
        return value.strip() if value else default.strip()

    def safe_getenv_bool(key: str, default: str = "true") -> bool:
        """Safely get boolean environment variable"""
        value = os.getenv(key, default)
        return str(value).strip().lower() in ("true", "1", "yes", "on")

    def safe_getenv_int(key: str, default: str = "0") -> int:
        """Safely get integer environment variable"""
        value = safe_getenv(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return int(default)

    def safe_getenv_float(key: str, default: str = "0.0") -> float:
        """Safely get float environment variable"""
        value = safe_getenv(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return float(default)
    
    try:
        # Get admin chat ID safely
        admin_chat_str = safe_getenv("ADMIN_CHAT_ID")
        admin_chat_id = None
        if admin_chat_str and admin_chat_str.strip():
            try:
                admin_chat_id = int(admin_chat_str)
            except (ValueError, TypeError):
                admin_chat_id = None

        config = Config(
            bot_token=safe_getenv("BOT_TOKEN"),
            api_id=safe_getenv_int("API_ID"),
            api_hash=safe_getenv("API_HASH"),
            bot_name=safe_getenv("BOT_NAME", "GuardianAI"),
            admin_chat_id=admin_chat_id,
            
            nsfw_threshold=safe_getenv_float("NSFW_THRESHOLD", "0.6"),
            nsfw_model_path=safe_getenv("NSFW_MODEL_PATH", "models/nsfw_model.onnx"),
            
            spam_threshold=safe_getenv_int("SPAM_THRESHOLD", "5"),
            max_messages_per_minute=safe_getenv_int("MAX_MESSAGES_PER_MINUTE", "10"),
            raid_threshold=safe_getenv_int("RAID_THRESHOLD", "10"),
            
            auto_delete_executables=safe_getenv_bool("AUTO_DELETE_EXECUTABLES", "true"),
            block_suspicious_links=safe_getenv_bool("BLOCK_SUSPICIOUS_LINKS", "true"),
            copyright_detection=safe_getenv_bool("COPYRIGHT_DETECTION", "true"),
            
            database_path=safe_getenv("DATABASE_PATH", "data/guardian.db"),
            
            enable_dashboard=safe_getenv_bool("ENABLE_DASHBOARD", "false"),
            dashboard_port=safe_getenv_int("DASHBOARD_PORT", "5000"),
            dashboard_host=safe_getenv("DASHBOARD_HOST", "0.0.0.0"),
            
            log_level=safe_getenv("LOG_LEVEL", "INFO"),
            log_file=safe_getenv("LOG_FILE", "logs/guardian.log")
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
