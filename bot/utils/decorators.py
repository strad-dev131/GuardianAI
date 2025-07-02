
"""
Utility decorators for GuardianAI
"""

import functools
import logging
from pyrogram.types import Message

def admin_required(func):
    """Decorator to require admin privileges"""
    @functools.wraps(func)
    async def wrapper(self, message: Message, *args, **kwargs):
        try:
            # Check if user is admin
            if not await self.bot.is_admin(message.chat.id, message.from_user.id):
                await message.reply_text(
                    "❌ **Access Denied**\n\n"
                    "This command requires administrator privileges."
                )
                return
            
            # Check if it's a group chat
            if message.chat.type not in ['group', 'supergroup']:
                await message.reply_text(
                    "❌ **Invalid Chat Type**\n\n"
                    "This command can only be used in groups."
                )
                return
            
            return await func(self, message, *args, **kwargs)
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error in admin_required decorator: {e}")
            await message.reply_text("❌ An error occurred while processing your request.")
    
    return wrapper

def error_handler(func):
    """Decorator for error handling"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error in {func.__name__}: {e}")
            # Optionally send error message to user
            if len(args) > 1 and hasattr(args[1], 'reply_text'):
                try:
                    await args[1].reply_text("❌ An unexpected error occurred.")
                except:
                    pass
    
    return wrapper

def rate_limit(max_calls: int = 5, window: int = 60):
    """Rate limiting decorator"""
    def decorator(func):
        calls = {}
        
        @functools.wraps(func)
        async def wrapper(self, message: Message, *args, **kwargs):
            import time
            
            user_id = message.from_user.id
            now = time.time()
            
            # Clean old calls
            if user_id in calls:
                calls[user_id] = [call_time for call_time in calls[user_id] if now - call_time < window]
            else:
                calls[user_id] = []
            
            # Check rate limit
            if len(calls[user_id]) >= max_calls:
                await message.reply_text(
                    f"⏰ **Rate Limited**\n\n"
                    f"Please wait before using this command again."
                )
                return
            
            # Record this call
            calls[user_id].append(now)
            
            return await func(self, message, *args, **kwargs)
        
        return wrapper
    return decorator
