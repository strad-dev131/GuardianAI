"""
Admin Command Handlers for GuardianAI
"""

import logging
from pyrogram.types import Message
from ..utils.decorators import admin_required

class AdminHandler:
    """Handles admin commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
    
    async def help_command(self, message: Message):
        """Show help information"""
        help_text = """
🛡️ **GuardianAI - Advanced Telegram Moderation Bot**

**Admin Commands:**
• `/enable` - Enable bot in this group
• `/disable` - Disable bot in this group
• `/status` - Show bot status and settings
• `/set_threshold <type> <value>` - Set detection thresholds

**Features:**
🔥 NSFW Detection - Auto-delete inappropriate content
🚫 Spam Protection - Block spam and raids
🛡️ Security Scanner - Remove malicious files
⚖️ Copyright Shield - Detect copyrighted content

**Configuration:**
The bot automatically detects and removes:
- NSFW images and stickers
- Spam messages and raids
- Malicious files (.exe, .apk, etc.)
- Suspicious links
- Copyrighted content

For support: @GuardianAI_Support
        """
        try:
            await message.reply_text(help_text)
        except Exception as e:
            self.logger.error(f"Error sending help: {e}")
    
    @admin_required
    async def status_command(self, message: Message):
        """Show bot status"""
        chat_id = message.chat.id
        enabled = await self.bot.is_enabled(chat_id)
        
        # Get statistics
        stats = await self.bot.db_manager.get_chat_stats(chat_id)
        
        status_text = f"""
🛡️ **GuardianAI Status**

**Group Status:** {'✅ Enabled' if enabled else '❌ Disabled'}
**Chat ID:** `{chat_id}`

**Detection Settings:**
• NSFW Threshold: `{self.bot.config.nsfw_threshold}`
• Spam Threshold: `{self.bot.config.spam_threshold}`
• Max Messages/Min: `{self.bot.config.max_messages_per_minute}`

**Statistics (Last 30 days):**
• Messages Processed: `{stats.get('messages_processed', 0)}`
• NSFW Detected: `{stats.get('nsfw_detected', 0)}`
• Spam Blocked: `{stats.get('spam_blocked', 0)}`
• Files Scanned: `{stats.get('files_scanned', 0)}`
• Threats Blocked: `{stats.get('threats_blocked', 0)}`

**System Status:** 🟢 Online
        """
        try:
            await message.reply_text(status_text)
        except Exception as e:
            self.logger.error(f"Error sending status: {e}")
    
    @admin_required
    async def enable_command(self, message: Message):
        """Enable bot in the group"""
        chat_id = message.chat.id
        
        if await self.bot.is_enabled(chat_id):
            await message.reply_text("✅ GuardianAI is already enabled in this group!")
            return
        
        try:
            await self.bot.enable_group(chat_id)
            await self.bot.log_action("GROUP_ENABLED", chat_id, message.from_user.id)
            
            await message.reply_text(
                "🛡️ **GuardianAI Enabled!**\n\n"
                "The bot is now protecting this group from:\n"
                "• NSFW content\n"
                "• Spam and raids\n"
                "• Malicious files\n"
                "• Suspicious links\n\n"
                "Use `/status` to check current settings."
            )
        except Exception as e:
            self.logger.error(f"Error enabling bot: {e}")
            await message.reply_text("❌ Failed to enable GuardianAI. Please try again.")
    
    @admin_required
    async def disable_command(self, message: Message):
        """Disable bot in the group"""
        chat_id = message.chat.id
        
        if not await self.bot.is_enabled(chat_id):
            await message.reply_text("❌ GuardianAI is already disabled in this group!")
            return
        
        try:
            await self.bot.disable_group(chat_id)
            await self.bot.log_action("GROUP_DISABLED", chat_id, message.from_user.id)
            
            await message.reply_text(
                "🛑 **GuardianAI Disabled**\n\n"
                "The bot is no longer actively moderating this group.\n"
                "Use `/enable` to reactivate protection."
            )
        except Exception as e:
            self.logger.error(f"Error disabling bot: {e}")
            await message.reply_text("❌ Failed to disable GuardianAI. Please try again.")
    
    @admin_required
    async def set_threshold_command(self, message: Message):
        """Set detection thresholds"""
        try:
            args = message.text.split()[1:]
            if len(args) != 2 or not args[0] or not args[1]:
                await message.reply_text(
                    "❌ **Usage:** `/set_threshold <type> <value>`\n\n"
                    "**Available types:**\n"
                    "• `nsfw` - NSFW detection threshold (0.0–1.0)\n"
                    "• `spam` - Messages before spam detection (1–20)\n"
                    "• `raid` - Users joining to trigger raid mode (5–50)"
                )
                return

            try:
                threshold_type = args[0].strip().lower()
                value = float(args[1])
            except Exception:
                await message.reply_text("❌ Invalid input. Please make sure both type and value are valid.")
                return

            if threshold_type == "nsfw":
                if not 0.0 <= value <= 1.0:
                    await message.reply_text("❌ NSFW threshold must be between 0.0 and 1.0")
                    return
                self.bot.config.nsfw_threshold = value
            
            elif threshold_type == "spam":
                if not 1 <= value <= 20:
                    await message.reply_text("❌ Spam threshold must be between 1 and 20")
                    return
                self.bot.config.spam_threshold = int(value)
            
            elif threshold_type == "raid":
                if not 5 <= value <= 50:
                    await message.reply_text("❌ Raid threshold must be between 5 and 50")
                    return
                self.bot.config.raid_threshold = int(value)
            
            else:
                await message.reply_text("❌ Invalid threshold type. Use: nsfw, spam, or raid")
                return
            
            await self.bot.log_action(
                "THRESHOLD_CHANGED",
                message.chat.id,
                message.from_user.id,
                f"{threshold_type}={value}"
            )
            
            await message.reply_text(
                f"✅ **Threshold Updated**\n\n"
                f"**{threshold_type.upper()}** threshold set to `{value}`"
            )
        except Exception as e:
            self.logger.error(f"Error setting threshold: {e}")
            await message.reply_text("❌ Failed to update threshold. Please try again.")
