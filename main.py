
#!/usr/bin/env python3
"""
GuardianAI - Advanced Telegram Moderation Bot
Main entry point for the bot application
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bot.core.bot import GuardianBot
from bot.core.config import load_config
from bot.utils.logger import setup_logging

async def main():
    """Main function to start the GuardianAI bot"""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("🛡️ Starting GuardianAI Bot...")
        
        # Load configuration
        config = load_config()
        
        # Initialize and start bot
        bot = GuardianBot(config)
        await bot.start()
        
        logger.info("✅ GuardianAI Bot started successfully!")
        
        # Keep the bot running
        await bot.idle()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        if 'bot' in locals():
            await bot.stop()

if __name__ == "__main__":
    # Create event loop for Windows compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())
