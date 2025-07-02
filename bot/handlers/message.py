
"""
Message Processing Handlers for GuardianAI
"""

import asyncio
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from pyrogram.types import Message, ChatMemberUpdated

class MessageHandler:
    """Handles message processing and filtering"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting tracking
        self.user_message_count: Dict[int, Dict[int, List[datetime]]] = {}  # chat_id -> user_id -> timestamps
        self.recent_joins: Dict[int, List[datetime]] = {}  # chat_id -> join timestamps
    
    async def process_message(self, message: Message):
        """Process incoming messages"""
        try:
            chat_id = message.chat.id
            
            # Skip if bot is disabled in this group
            if not await self.bot.is_enabled(chat_id):
                return
            
            # Skip if message is from admin
            if await self.bot.is_admin(chat_id, message.from_user.id):
                return
            
            # Update message count for spam detection
            await self._update_user_activity(chat_id, message.from_user.id)
            
            # Check for spam
            if await self._check_spam(message):
                await self._handle_spam(message)
                return
            
            # Check for NSFW content
            if message.photo or message.sticker or message.document:
                if await self._check_nsfw_content(message):
                    await self._handle_nsfw_content(message)
                    return
            
            # Check for security threats
            if message.document or message.audio or message.video:
                if await self._check_security_threats(message):
                    await self._handle_security_threat(message)
                    return
            
            # Check for suspicious links
            if message.text and any(keyword in message.text.lower() for keyword in ['http', 'www', '.com', '.org', '.net']):
                if await self._check_suspicious_links(message):
                    await self._handle_suspicious_link(message)
                    return
            
            # Log processed message
            await self.bot.db_manager.increment_stat(chat_id, 'messages_processed')
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    async def handle_member_update(self, chat_member_update: ChatMemberUpdated):
        """Handle new member joins (raid protection)"""
        try:
            chat_id = chat_member_update.chat.id
            
            # Skip if bot is disabled
            if not await self.bot.is_enabled(chat_id):
                return
            
            # Only handle new joins
            if (chat_member_update.old_chat_member is None and 
                chat_member_update.new_chat_member.status == "member"):
                
                await self._track_join(chat_id)
                
                # Check for raid
                if await self._check_raid(chat_id):
                    await self._handle_raid(chat_id)
                    
        except Exception as e:
            self.logger.error(f"Error handling member update: {e}")
    
    async def _update_user_activity(self, chat_id: int, user_id: int):
        """Update user message activity for spam detection"""
        now = datetime.now()
        
        if chat_id not in self.user_message_count:
            self.user_message_count[chat_id] = {}
        
        if user_id not in self.user_message_count[chat_id]:
            self.user_message_count[chat_id][user_id] = []
        
        # Add current timestamp
        self.user_message_count[chat_id][user_id].append(now)
        
        # Remove old timestamps (older than 1 minute)
        cutoff = now - timedelta(minutes=1)
        self.user_message_count[chat_id][user_id] = [
            ts for ts in self.user_message_count[chat_id][user_id] if ts > cutoff
        ]
    
    async def _check_spam(self, message: Message) -> bool:
        """Check if message is spam"""
        try:
            chat_id = message.chat.id
            user_id = message.from_user.id
            
            # Check message rate
            if chat_id in self.user_message_count and user_id in self.user_message_count[chat_id]:
                message_count = len(self.user_message_count[chat_id][user_id])
                if message_count > self.bot.config.max_messages_per_minute:
                    return True
            
            # Use spam detector module
            is_spam = await self.bot.spam_detector.detect_spam(message.text or "")
            return is_spam
            
        except Exception as e:
            self.logger.error(f"Error checking spam: {e}")
            return False
    
    async def _check_nsfw_content(self, message: Message) -> bool:
        """Check if message contains NSFW content"""
        try:
            # Use NSFW detector module
            if message.photo:
                file_path = await message.download(file_name="temp/")
                result = await self.bot.nsfw_detector.detect_image(file_path)
                return result.is_nsfw
            
            elif message.sticker:
                file_path = await message.download(file_name="temp/")
                result = await self.bot.nsfw_detector.detect_sticker(file_path)
                return result.is_nsfw
            
            elif message.document and message.document.mime_type.startswith('image/'):
                file_path = await message.download(file_name="temp/")
                result = await self.bot.nsfw_detector.detect_image(file_path)
                return result.is_nsfw
                
        except Exception as e:
            self.logger.error(f"Error checking NSFW content: {e}")
            
        return False
    
    async def _check_security_threats(self, message: Message) -> bool:
        """Check for security threats in files"""
        try:
            if message.document:
                return await self.bot.security_scanner.scan_document(message.document)
            elif message.audio:
                return await self.bot.security_scanner.scan_audio(message.audio)
            elif message.video:
                return await self.bot.security_scanner.scan_video(message.video)
                
        except Exception as e:
            self.logger.error(f"Error checking security threats: {e}")
            
        return False
    
    async def _check_suspicious_links(self, message: Message) -> bool:
        """Check for suspicious links"""
        try:
            if message.text:
                return await self.bot.security_scanner.scan_links(message.text)
        except Exception as e:
            self.logger.error(f"Error checking suspicious links: {e}")
            
        return False
    
    async def _track_join(self, chat_id: int):
        """Track user joins for raid detection"""
        now = datetime.now()
        
        if chat_id not in self.recent_joins:
            self.recent_joins[chat_id] = []
        
        self.recent_joins[chat_id].append(now)
        
        # Remove old joins (older than 5 minutes)
        cutoff = now - timedelta(minutes=5)
        self.recent_joins[chat_id] = [
            ts for ts in self.recent_joins[chat_id] if ts > cutoff
        ]
    
    async def _check_raid(self, chat_id: int) -> bool:
        """Check if there's a raid happening"""
        if chat_id not in self.recent_joins:
            return False
        
        return len(self.recent_joins[chat_id]) >= self.bot.config.raid_threshold
    
    async def _handle_spam(self, message: Message):
        """Handle spam message"""
        try:
            await message.delete()
            await self.bot.log_action(
                "SPAM_DELETED", 
                message.chat.id, 
                message.from_user.id,
                f"Spam message deleted"
            )
            await self.bot.db_manager.increment_stat(message.chat.id, 'spam_blocked')
            
        except Exception as e:
            self.logger.error(f"Error handling spam: {e}")
    
    async def _handle_nsfw_content(self, message: Message):
        """Handle NSFW content"""
        try:
            await message.delete()
            
            # Send warning
            warning_msg = await message.reply_text(
                f"🔞 **NSFW Content Detected**\n\n"
                f"@{message.from_user.username or message.from_user.first_name}, "
                f"inappropriate content has been removed."
            )
            
            # Delete warning after 10 seconds
            await asyncio.sleep(10)
            try:
                await warning_msg.delete()
            except:
                pass
            
            await self.bot.log_action(
                "NSFW_DELETED", 
                message.chat.id, 
                message.from_user.id,
                f"NSFW content removed"
            )
            await self.bot.db_manager.increment_stat(message.chat.id, 'nsfw_detected')
            
        except Exception as e:
            self.logger.error(f"Error handling NSFW content: {e}")
    
    async def _handle_security_threat(self, message: Message):
        """Handle security threats"""
        try:
            await message.delete()
            
            # Send warning
            warning_msg = await message.reply_text(
                f"⚠️ **Security Threat Detected**\n\n"
                f"@{message.from_user.username or message.from_user.first_name}, "
                f"potentially malicious file has been removed for group safety."
            )
            
            # Delete warning after 15 seconds
            await asyncio.sleep(15)
            try:
                await warning_msg.delete()
            except:
                pass
            
            await self.bot.log_action(
                "THREAT_BLOCKED", 
                message.chat.id, 
                message.from_user.id,
                f"Malicious file removed"
            )
            await self.bot.db_manager.increment_stat(message.chat.id, 'threats_blocked')
            
        except Exception as e:
            self.logger.error(f"Error handling security threat: {e}")
    
    async def _handle_suspicious_link(self, message: Message):
        """Handle suspicious links"""
        try:
            await message.delete()
            
            # Send warning
            warning_msg = await message.reply_text(
                f"🔗 **Suspicious Link Detected**\n\n"
                f"@{message.from_user.username or message.from_user.first_name}, "
                f"potentially harmful link has been removed."
            )
            
            # Delete warning after 10 seconds
            await asyncio.sleep(10)
            try:
                await warning_msg.delete()
            except:
                pass
            
            await self.bot.log_action(
                "LINK_BLOCKED", 
                message.chat.id, 
                message.from_user.id,
                f"Suspicious link removed"
            )
            
        except Exception as e:
            self.logger.error(f"Error handling suspicious link: {e}")
    
    async def _handle_raid(self, chat_id: int):
        """Handle raid situation"""
        try:
            # Send raid alert
            alert_msg = await self.bot.app.send_message(
                chat_id,
                "🚨 **RAID DETECTED**\n\n"
                "Multiple users joining rapidly. Raid protection activated!\n"
                "New member approval may be restricted temporarily."
            )
            
            await self.bot.log_action(
                "RAID_DETECTED", 
                chat_id,
                details=f"Raid protection activated - {len(self.recent_joins[chat_id])} joins detected"
            )
            
            # Delete alert after 30 seconds
            await asyncio.sleep(30)
            try:
                await alert_msg.delete()
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Error handling raid: {e}")
