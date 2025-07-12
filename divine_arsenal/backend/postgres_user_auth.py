#!/usr/bin/env python3
"""
PostgreSQL User Authentication System for SMITE 2 Divine Arsenal
Replaces SQLite-based user_auth.py with PostgreSQL integration
"""

import hashlib
import os
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from sqlalchemy import text

from postgres_database_adapter import PostgreSQLDatabaseAdapter

logger = logging.getLogger(__name__)

try:
    import jwt
except ImportError:
    logger.warning("⚠️ JWT not installed. Run: pip install PyJWT")
    jwt = None

try:
    from scrapers.tracker import TrackerScraper
except ImportError:
    TrackerScraper = None


@dataclass
class UserProfile:
    """User profile data structure."""
    user_id: str
    username: str
    tracker_gg_profile: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    rank: Optional[str] = None
    level: Optional[int] = None
    favorite_role: Optional[str] = None
    favorite_gods: List[str] = field(default_factory=list)
    join_date: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_online: bool = False
    status: str = "offline"  # online, away, busy, invisible
    bio: Optional[str] = None
    discord_id: Optional[str] = None
    steam_id: Optional[str] = None


class PostgreSQLUserAuth:
    """PostgreSQL-based user authentication and profile management system."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize with PostgreSQL database adapter."""
        # Use PostgreSQL adapter instead of SQLite
        self.db_adapter = PostgreSQLDatabaseAdapter(db_path)
        self.secret_key = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
        
        # Lazy initialization for TrackerScraper
        self._tracker_scraper = None
        
        self._init_user_tables()

    @property
    def tracker_scraper(self):
        """Lazy initialization of TrackerScraper."""
        if self._tracker_scraper is None and TrackerScraper is not None:
            logger.info("🔧 Initializing TrackerScraper on first use (lazy loading)")
            self._tracker_scraper = TrackerScraper(use_selenium=False)
        return self._tracker_scraper

    def _init_user_tables(self):
        """Initialize PostgreSQL tables for user authentication."""
        with self.db_adapter.get_connection() as session:
            try:
                # Users table
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS user_auth (
                        user_id TEXT PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        tracker_gg_profile TEXT UNIQUE NOT NULL,
                        email TEXT,
                        avatar_url TEXT,
                        rank TEXT,
                        level INTEGER,
                        favorite_role TEXT,
                        favorite_gods TEXT,  -- JSON array
                        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_online BOOLEAN DEFAULT FALSE,
                        status TEXT DEFAULT 'offline',
                        bio TEXT,
                        discord_id TEXT,
                        steam_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                # User sessions table
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        token TEXT NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user_auth (user_id)
                    )
                """))

                # Friends table
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS user_friends (
                        friendship_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        friend_id TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',  -- pending, accepted, blocked
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user_auth (user_id),
                        FOREIGN KEY (friend_id) REFERENCES user_auth (user_id),
                        UNIQUE(user_id, friend_id)
                    )
                """))

                # Online status table
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS online_status (
                        user_id TEXT PRIMARY KEY,
                        is_online BOOLEAN DEFAULT FALSE,
                        status TEXT DEFAULT 'offline',
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        current_game TEXT,  -- game_id if in match
                        party_id TEXT,  -- party_id if in party
                        FOREIGN KEY (user_id) REFERENCES user_auth (user_id)
                    )
                """))

                # Create indexes
                session.execute(text("CREATE INDEX IF NOT EXISTS idx_user_auth_username ON user_auth(username)"))
                session.execute(text("CREATE INDEX IF NOT EXISTS idx_user_auth_tracker_profile ON user_auth(tracker_gg_profile)"))
                session.execute(text("CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)"))
                session.execute(text("CREATE INDEX IF NOT EXISTS idx_user_friends_user_id ON user_friends(user_id)"))
                session.execute(text("CREATE INDEX IF NOT EXISTS idx_online_status ON online_status(is_online)"))

                session.commit()
                logger.info("✅ PostgreSQL user authentication tables initialized")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error initializing user auth tables: {e}")

    def authenticate_with_tracker(self, tracker_username: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with Tracker.gg SMITE 2 profile."""
        if not self.tracker_scraper:
            return {"error": "Tracker.gg integration not available"}

        try:
            # Get profile from Tracker.gg
            profile = self.tracker_scraper.get_player_profile(tracker_username)
            if not profile:
                return {"error": "Profile not found on Tracker.gg"}

            # Check if user exists in PostgreSQL
            user = self.get_user_by_tracker_profile(tracker_username)

            if user:
                # Update last login and online status
                self.update_user_login(user['user_id'])
                self.set_user_online(user['user_id'])

                # Generate new session token
                token = self.create_session(user['user_id'])

                return {
                    "success": True,
                    "user": user,
                    "token": token,
                    "profile": profile,
                    "message": "Authentication successful"
                }
            else:
                # Create new user from Tracker.gg profile
                new_user = self._create_user_from_tracker(tracker_username, profile)
                if new_user:
                    token = self.create_session(new_user['user_id'])
                    return {
                        "success": True,
                        "user": new_user,
                        "token": token,
                        "profile": profile,
                        "message": "New user created successfully"
                    }
                else:
                    return {"error": "Failed to create user account"}

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {"error": f"Authentication failed: {str(e)}"}

    def _create_user_from_tracker(self, tracker_username: str, profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user from Tracker.gg profile."""
        with self.db_adapter.get_connection() as session:
            try:
                user_id = secrets.token_urlsafe(16)
                
                session.execute(text("""
                    INSERT INTO user_auth 
                    (user_id, username, tracker_gg_profile, rank, level, bio)
                    VALUES (:user_id, :username, :tracker_gg_profile, :rank, :level, :bio)
                """), {
                    "user_id": user_id,
                    "username": tracker_username,
                    "tracker_gg_profile": tracker_username,
                    "rank": profile.get("rank", "Unranked"),
                    "level": profile.get("level", 1),
                    "bio": f"SMITE 2 player from Tracker.gg"
                })
                
                session.commit()
                logger.info(f"✅ Created new user from Tracker.gg: {tracker_username}")
                
                return self.get_user_by_id(user_id)
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error creating user from tracker: {e}")
                return None

    def get_user_by_tracker_profile(self, tracker_username: str) -> Optional[Dict[str, Any]]:
        """Get user by Tracker.gg profile."""
        with self.db_adapter.get_connection() as session:
            try:
                result = session.execute(text("""
                    SELECT * FROM user_auth WHERE tracker_gg_profile = :tracker_username
                """), {"tracker_username": tracker_username})
                
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return None
                
            except Exception as e:
                logger.error(f"Error getting user by tracker profile: {e}")
                return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        with self.db_adapter.get_connection() as session:
            try:
                result = session.execute(text("""
                    SELECT * FROM user_auth WHERE user_id = :user_id
                """), {"user_id": user_id})
                
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return None
                
            except Exception as e:
                logger.error(f"Error getting user by ID: {e}")
                return None

    def create_session(self, user_id: str, expires_in_hours: int = 24) -> str:
        """Create a new session token."""
        if not jwt:
            return secrets.token_urlsafe(32)  # Fallback token
        
        try:
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
                'iat': datetime.utcnow()
            }
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            
            # Store session in PostgreSQL
            with self.db_adapter.get_connection() as session:
                session_id = secrets.token_urlsafe(16)
                session.execute(text("""
                    INSERT INTO user_sessions (session_id, user_id, token, expires_at)
                    VALUES (:session_id, :user_id, :token, :expires_at)
                """), {
                    "session_id": session_id,
                    "user_id": user_id,
                    "token": token,
                    "expires_at": datetime.utcnow() + timedelta(hours=expires_in_hours)
                })
                session.commit()
            
            return token
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return secrets.token_urlsafe(32)  # Fallback

    def update_user_login(self, user_id: str):
        """Update user's last login timestamp."""
        with self.db_adapter.get_connection() as session:
            try:
                session.execute(text("""
                    UPDATE user_auth SET last_login = CURRENT_TIMESTAMP WHERE user_id = :user_id
                """), {"user_id": user_id})
                session.commit()
            except Exception as e:
                logger.error(f"Error updating user login: {e}")

    def set_user_online(self, user_id: str, status: str = "online"):
        """Set user as online."""
        with self.db_adapter.get_connection() as session:
            try:
                session.execute(text("""
                    INSERT INTO online_status (user_id, is_online, status, last_seen)
                    VALUES (:user_id, TRUE, :status, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id) DO UPDATE SET
                        is_online = TRUE,
                        status = :status,
                        last_seen = CURRENT_TIMESTAMP
                """), {"user_id": user_id, "status": status})
                session.commit()
            except Exception as e:
                logger.error(f"Error setting user online: {e}")

    def set_user_offline(self, user_id: str):
        """Set user as offline."""
        with self.db_adapter.get_connection() as session:
            try:
                session.execute(text("""
                    UPDATE online_status SET 
                        is_online = FALSE, 
                        status = 'offline', 
                        last_seen = CURRENT_TIMESTAMP 
                    WHERE user_id = :user_id
                """), {"user_id": user_id})
                session.commit()
            except Exception as e:
                logger.error(f"Error setting user offline: {e}")

    def get_online_users(self) -> List[Dict[str, Any]]:
        """Get list of online users."""
        with self.db_adapter.get_connection() as session:
            try:
                result = session.execute(text("""
                    SELECT ua.user_id, ua.username, ua.rank, os.status, os.last_seen
                    FROM user_auth ua
                    JOIN online_status os ON ua.user_id = os.user_id
                    WHERE os.is_online = TRUE
                    ORDER BY os.last_seen DESC
                """))
                
                return [dict(row._mapping) for row in result]
                
            except Exception as e:
                logger.error(f"Error getting online users: {e}")
                return []

    def close(self):
        """Close database connections."""
        if hasattr(self, 'db_adapter'):
            self.db_adapter.close()
        logger.info("✅ PostgreSQL User Auth closed")


# For backward compatibility
UserAuth = PostgreSQLUserAuth 