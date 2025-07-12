#!/usr/bin/env python3
"""
PostgreSQL-compatible User Authentication for SMITE 2 Divine Arsenal
Uses SQLAlchemy models instead of direct SQLite connections
"""

import os
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# JWT for session tokens
try:
    import jwt
except ImportError:
    jwt = None

logger = logging.getLogger(__name__)

class PostgreSQLUserAuth:
    """PostgreSQL-compatible user authentication using SQLAlchemy."""

    def __init__(self, db_session, user_model):
        """Initialize with SQLAlchemy session and User model."""
        self.db = db_session
        self.User = user_model
        self.secret_key = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
        
        # Lazy initialization for TrackerScraper
        self._tracker_scraper = None

    @property
    def tracker_scraper(self):
        """Lazy initialization of TrackerScraper."""
        if self._tracker_scraper is None:
            try:
                from scrapers.tracker import TrackerScraper
                print("🔧 Initializing TrackerScraper for PostgreSQL auth")
                self._tracker_scraper = TrackerScraper(use_selenium=False)
            except ImportError:
                logger.warning("TrackerScraper not available")
                self._tracker_scraper = None
        return self._tracker_scraper

    def authenticate_with_tracker(self, tracker_username: str) -> Dict[str, Any]:
        """Authenticate user with Tracker.gg profile."""
        try:
            # Check if user exists
            user = self.User.query.filter_by(tracker_username=tracker_username).first()
            
            if user:
                # Update login time
                user.last_seen = datetime.now()
                user.is_online = True
                self.db.session.commit()
                
                # Generate session token
                token = self.create_session_token(user.user_id)
                
                return {
                    "success": True,
                    "user": user.to_dict(),
                    "token": token,
                    "is_new_user": False
                }
            else:
                # Create new user from tracker profile
                user_data = self._create_user_from_tracker(tracker_username)
                if user_data:
                    token = self.create_session_token(user_data['user_id'])
                    return {
                        "success": True,
                        "user": user_data,
                        "token": token,
                        "is_new_user": True
                    }
                else:
                    return {"error": "Failed to create user from Tracker.gg profile"}
                    
        except Exception as e:
            logger.error(f"Tracker authentication error: {e}")
            return {"error": f"Authentication failed: {str(e)}"}

    def _create_user_from_tracker(self, tracker_username: str) -> Optional[Dict[str, Any]]:
        """Create user from Tracker.gg profile."""
        try:
            # Generate unique user ID
            user_id = f"tracker_{secrets.token_hex(8)}"
            
            # Create new user
            new_user = self.User(
                user_id=user_id,
                username=tracker_username,
                tracker_username=tracker_username,
                rank="Unranked",
                is_online=True,
                created_at=datetime.now(),
                last_seen=datetime.now()
            )
            
            self.db.session.add(new_user)
            self.db.session.commit()
            
            logger.info(f"Created new user from Tracker.gg: {tracker_username}")
            return new_user.to_dict()
            
        except Exception as e:
            logger.error(f"Error creating user from tracker: {e}")
            self.db.session.rollback()
            return None

    def register_user(self, username: str, email: str, password: str, tracker_gg_profile: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user with site credentials."""
        try:
            # Check if username exists
            existing_user = self.User.query.filter_by(username=username).first()
            if existing_user:
                return {"error": "Username already exists"}
            
            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Generate user ID
            user_id = f"user_{secrets.token_hex(8)}"
            
            # Create new user
            new_user = self.User(
                user_id=user_id,
                username=username,
                password_hash=password_hash,
                tracker_username=tracker_gg_profile or username,
                is_online=True,
                created_at=datetime.now(),
                last_seen=datetime.now()
            )
            
            self.db.session.add(new_user)
            self.db.session.commit()
            
            # Create session token
            token = self.create_session_token(user_id)
            
            logger.info(f"Registered new user: {username}")
            return {
                "success": True,
                "user": new_user.to_dict(),
                "token": token,
                "is_new_user": True
            }
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            self.db.session.rollback()
            return {"error": f"Registration failed: {str(e)}"}

    def authenticate_with_credentials(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user with username and password."""
        try:
            # Hash password for comparison
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Find user
            user = self.User.query.filter_by(username=username).first()
            
            if not user:
                return {"error": "Invalid username or password"}
            
            if not user.password_hash:
                return {"error": "Account not properly configured"}
                
            if user.password_hash != password_hash:
                return {"error": "Invalid username or password"}
            
            # Update login status
            user.last_seen = datetime.now()
            user.is_online = True
            self.db.session.commit()
            
            # Generate session token
            token = self.create_session_token(user.user_id)
            
            return {
                "success": True,
                "user": user.to_dict(),
                "token": token,
                "is_new_user": False
            }
            
        except Exception as e:
            logger.error(f"Credential authentication error: {e}")
            return {"error": f"Authentication failed: {str(e)}"}

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by user ID."""
        try:
            user = self.User.query.filter_by(user_id=user_id).first()
            return user.to_dict() if user else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        try:
            user = self.User.query.filter_by(username=username).first()
            return user.to_dict() if user else None
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None

    def create_session_token(self, user_id: str) -> str:
        """Create JWT session token."""
        if not jwt:
            return secrets.token_hex(16)  # Fallback token
            
        payload = {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(days=30),
            'iat': datetime.now()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return user data."""
        if not jwt:
            return None
            
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if user_id:
                return self.get_user_by_id(user_id)
                
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            
        return None

    def get_online_users(self) -> List[Dict[str, Any]]:
        """Get list of online users."""
        try:
            # Consider users online if they were active in the last 30 minutes
            cutoff_time = datetime.now() - timedelta(minutes=30)
            
            users = self.User.query.filter(
                self.User.is_online == True,
                self.User.last_seen > cutoff_time
            ).order_by(self.User.last_seen.desc()).all()
            
            return [user.to_dict() for user in users]
            
        except Exception as e:
            logger.error(f"Error getting online users: {e}")
            return []

    def set_user_offline(self, user_id: str):
        """Set user as offline."""
        try:
            user = self.User.query.filter_by(user_id=user_id).first()
            if user:
                user.is_online = False
                user.last_seen = datetime.now()
                self.db.session.commit()
        except Exception as e:
            logger.error(f"Error setting user offline: {e}")
            self.db.session.rollback()

    def set_user_online(self, user_id: str):
        """Set user as online."""
        try:
            user = self.User.query.filter_by(user_id=user_id).first()
            if user:
                user.is_online = True
                user.last_seen = datetime.now()
                self.db.session.commit()
        except Exception as e:
            logger.error(f"Error setting user online: {e}")
            self.db.session.rollback()

    def get_user_count(self) -> int:
        """Get total number of users."""
        try:
            return self.User.query.count()
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0 