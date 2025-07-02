
"""
Database Manager for GuardianAI
Handles all database operations
"""

import asyncio
import logging
import aiosqlite
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class DatabaseManager:
    """Database management system"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._connection = None
    
    async def initialize(self):
        """Initialize database and create tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await self._create_tables(db)
                await db.commit()
            
            self.logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize database: {e}")
            raise
    
    async def _create_tables(self, db: aiosqlite.Connection):
        """Create database tables"""
        
        # Groups table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                chat_title TEXT,
                enabled BOOLEAN DEFAULT TRUE,
                nsfw_threshold REAL DEFAULT 0.6,
                spam_threshold INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Activity logs table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES groups (chat_id)
            )
        """)
        
        # Statistics table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                stat_type TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                date DATE DEFAULT (DATE('now')),
                UNIQUE(chat_id, stat_type, date),
                FOREIGN KEY (chat_id) REFERENCES groups (chat_id)
            )
        """)
        
        # Blocked users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS blocked_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                reason TEXT,
                blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chat_id, user_id),
                FOREIGN KEY (chat_id) REFERENCES groups (chat_id)
            )
        """)
        
        # Whitelist table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS whitelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chat_id, user_id),
                FOREIGN KEY (chat_id) REFERENCES groups (chat_id)
            )
        """)
    
    async def get_enabled_groups(self) -> List[int]:
        """Get list of enabled group chat IDs"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT chat_id FROM groups WHERE enabled = TRUE"
                )
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
                
        except Exception as e:
            self.logger.error(f"Error getting enabled groups: {e}")
            return []
    
    async def set_group_enabled(self, chat_id: int, enabled: bool):
        """Set group enabled status"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO groups (chat_id, enabled, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (chat_id, enabled))
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Error setting group enabled status: {e}")
    
    async def log_action(self, action: str, chat_id: int, user_id: Optional[int] = None, details: Optional[str] = None):
        """Log bot action"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO activity_logs (chat_id, user_id, action, details)
                    VALUES (?, ?, ?, ?)
                """, (chat_id, user_id, action, details))
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Error logging action: {e}")
    
    async def increment_stat(self, chat_id: int, stat_type: str, count: int = 1):
        """Increment statistics counter"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO statistics (chat_id, stat_type, count)
                    VALUES (?, ?, ?)
                    ON CONFLICT(chat_id, stat_type, date)
                    DO UPDATE SET count = count + ?
                """, (chat_id, stat_type, count, count))
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Error incrementing stat: {e}")
    
    async def get_chat_stats(self, chat_id: int, days: int = 30) -> Dict[str, int]:
        """Get chat statistics"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).date()
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT stat_type, SUM(count) as total
                    FROM statistics
                    WHERE chat_id = ? AND date >= ?
                    GROUP BY stat_type
                """, (chat_id, cutoff_date))
                
                rows = await cursor.fetchall()
                return {row[0]: row[1] for row in rows}
                
        except Exception as e:
            self.logger.error(f"Error getting chat stats: {e}")
            return {}
    
    async def add_to_whitelist(self, chat_id: int, user_id: int, added_by: int):
        """Add user to whitelist"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO whitelist (chat_id, user_id, added_by)
                    VALUES (?, ?, ?)
                """, (chat_id, user_id, added_by))
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Error adding to whitelist: {e}")
    
    async def remove_from_whitelist(self, chat_id: int, user_id: int):
        """Remove user from whitelist"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    DELETE FROM whitelist
                    WHERE chat_id = ? AND user_id = ?
                """, (chat_id, user_id))
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Error removing from whitelist: {e}")
    
    async def is_whitelisted(self, chat_id: int, user_id: int) -> bool:
        """Check if user is whitelisted"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT 1 FROM whitelist
                    WHERE chat_id = ? AND user_id = ?
                """, (chat_id, user_id))
                
                result = await cursor.fetchone()
                return result is not None
                
        except Exception as e:
            self.logger.error(f"Error checking whitelist: {e}")
            return False
    
    async def block_user(self, chat_id: int, user_id: int, reason: str):
        """Block user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO blocked_users (chat_id, user_id, reason)
                    VALUES (?, ?, ?)
                """, (chat_id, user_id, reason))
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Error blocking user: {e}")
    
    async def is_blocked(self, chat_id: int, user_id: int) -> bool:
        """Check if user is blocked"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT 1 FROM blocked_users
                    WHERE chat_id = ? AND user_id = ?
                """, (chat_id, user_id))
                
                result = await cursor.fetchone()
                return result is not None
                
        except Exception as e:
            self.logger.error(f"Error checking blocked status: {e}")
            return False
    
    async def get_recent_actions(self, chat_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent actions for a chat"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT user_id, action, details, timestamp
                    FROM activity_logs
                    WHERE chat_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (chat_id, limit))
                
                rows = await cursor.fetchall()
                return [
                    {
                        'user_id': row[0],
                        'action': row[1],
                        'details': row[2],
                        'timestamp': row[3]
                    }
                    for row in rows
                ]
                
        except Exception as e:
            self.logger.error(f"Error getting recent actions: {e}")
            return []
    
    async def close(self):
        """Close database connection"""
        try:
            if self._connection:
                await self._connection.close()
        except Exception as e:
            self.logger.error(f"Error closing database: {e}")
