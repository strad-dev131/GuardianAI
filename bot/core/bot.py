
"""
Main GuardianAI Bot Class
Handles bot initialization and message routing
"""

import asyncio
import logging
from typing import Dict, Set
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMember

from .config import Config, create_directories
from ..handlers.admin import AdminHandler
from ..handlers.message import MessageHandler
from ..modules.nsfw.detector import NSFWDetector
from ..modules.spam.detector import SpamDetector
from ..modules.security.scanner import SecurityScanner
from ..database.manager import DatabaseManager

class GuardianBot:
    """Main GuardianAI Bot class"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Create necessary directories
        create_directories(config)
        
        # Initialize Pyrogram client
        self.app = Client(
            name="guardian_bot",
            bot_token=config.bot_token,
            api_id=config.api_id,
            api_hash=config.api_hash,
            workdir="data"
        )
        
        # Initialize modules
        self.db_manager = DatabaseManager(config.database_path)
        self.nsfw_detector = NSFWDetector(config)
        self.spam_detector = SpamDetector(config)
        self.security_scanner = SecurityScanner(config)
        
        # Initialize handlers
        self.admin_handler = AdminHandler(self)
        self.message_handler = MessageHandler(self)
        
        # Bot state
        self.enabled_groups: Set[int] = set()
        self.admin_users: Dict[int, Set[int]] = {}  # chat_id -> set of admin user_ids
        
        # Setup handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup message handlers"""
        
        # Admin commands
        @self.app.on_message(filters.command(["start", "help"]))
        async def help_command(client, message: Message):
            await self.admin_handler.help_command(message)
        
        @self.app.on_message(filters.command(["status"]))
        async def status_command(client, message: Message):
            await self.admin_handler.status_command(message)
        
        @self.app.on_message(filters.command(["enable"]))
        async def enable_command(client, message: Message):
            await self.admin_handler.enable_command(message)
        
        @self.app.on_message(filters.command(["disable"]))
        async def disable_command(client, message: Message):
            await self.admin_handler.disable_command(message)
        
        @self.app.on_message(filters.command(["set_threshold"]))
        async def set_threshold_command(client, message: Message):
            await self.admin_handler.set_threshold_command(message)
        
        # Message filtering
        @self.app.on_message(filters.group & ~filters.command(None))
        async def process_message(client, message: Message):
            await self.message_handler.process_message(message)
        
        # New member handling (raid protection)
        @self.app.on_chat_member_updated()
        async def handle_member_update(client, chat_member_update):
            await self.message_handler.handle_member_update(chat_member_update)
    
    async def start(self):
        """Start the bot"""
        try:
            # Initialize database
            await self.db_manager.initialize()
            
            # Initialize AI models
            await self.nsfw_detector.initialize()
            
            # Start Pyrogram client
            await self.app.start()
            
            # Load enabled groups from database
            enabled_groups = await self.db_manager.get_enabled_groups()
            self.enabled_groups = set(enabled_groups)
            
            self.logger.info(f"✅ Bot started with {len(self.enabled_groups)} enabled groups")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start bot: {e}")
            raise
    
    async def stop(self):
        """Stop the bot"""
        try:
            await self.app.stop()
            await self.db_manager.close()
            self.logger.info("🛑 Bot stopped successfully")
        except Exception as e:
            self.logger.error(f"❌ Error stopping bot: {e}")
    
    async def idle(self):
        """Keep the bot running"""
        await self.app.idle()
    
    async def is_admin(self, chat_id: int, user_id: int) -> bool:
        """Check if user is admin in the chat"""
        try:
            member = await self.app.get_chat_member(chat_id, user_id)
            return member.status in ["creator", "administrator"]
        except Exception:
            return False
    
    async def is_enabled(self, chat_id: int) -> bool:
        """Check if bot is enabled in the chat"""
        return chat_id in self.enabled_groups
    
    async def enable_group(self, chat_id: int):
        """Enable bot in a group"""
        self.enabled_groups.add(chat_id)
        await self.db_manager.set_group_enabled(chat_id, True)
    
    async def disable_group(self, chat_id: int):
        """Disable bot in a group"""
        self.enabled_groups.discard(chat_id)
        await self.db_manager.set_group_enabled(chat_id, False)
    
    async def log_action(self, action: str, chat_id: int, user_id: int = None, details: str = None):
        """Log bot actions"""
        try:
            await self.db_manager.log_action(action, chat_id, user_id, details)
            
            # Send to admin chat if configured
            if self.config.admin_chat_id:
                log_message = f"🛡️ **GuardianAI Action**\n"
                log_message += f"**Action:** {action}\n"
                log_message += f"**Chat ID:** `{chat_id}`\n"
                if user_id:
                    log_message += f"**User ID:** `{user_id}`\n"
                if details:
                    log_message += f"**Details:** {details}"
                
                try:
                    await self.app.send_message(self.config.admin_chat_id, log_message)
                except Exception as e:
                    self.logger.error(f"Failed to send admin log: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to log action: {e}")
