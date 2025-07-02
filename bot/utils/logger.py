
"""
Logging configuration for GuardianAI
"""

import logging
import sys
from pathlib import Path
import coloredlogs

def setup_logging(log_level: str = "INFO", log_file: str = "logs/guardian.log"):
    """Setup logging configuration"""
    
    # Create logs directory
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Setup colored logs
    coloredlogs.install(
        level=log_level.upper(),
        logger=logger,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[console_handler]
    )
    
    # Suppress noisy loggers
    logging.getLogger('pyrogram').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiosqlite').setLevel(logging.WARNING)
    
    logger.info("🔧 Logging system initialized")
