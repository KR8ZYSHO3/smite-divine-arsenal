#!/usr/bin/env python3
"""
User Authentication System for SMITE 2 Divine Arsenal
Integrates with Tracker.gg for SMITE 2 profile authentication
"""

import hashlib
import os
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

try:
    import jwt
except ImportError:
    print("⚠️ JWT not installed. Run: pip install PyJWT")
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


class UserAuth:
    """User authentication and profile management system."""

    def __init__(self, db_path: Optional[str] = None):
        # Use a proper database path relative to the backend directory
        if db_path is None:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(script_dir, "user_auth.db")
        else:
            self.db_path = os.path.abspath(db_path)

        # Ensure the database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        print(f"[DEBUG] Trying to open database at: {self.db_path}")
        self.secret_key = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))

        # 🔧 LAZY INITIALIZATION - Don't create TrackerScraper during startup
        self._tracker_scraper = None

        self._init_database()

    @property
    def tracker_scraper(self):
        """Lazy initialization of TrackerScraper to prevent WebDriver spam during startup."""
        if self._tracker_scraper is None and TrackerScraper is not None:
            print("🔧 Initializing TrackerScraper on first use (lazy loading)")
            # 🔧 DISABLE WebDriver during startup to prevent spam
            self._tracker_scraper = TrackerScraper(use_selenium=False)
        return self._tracker_scraper

    def _init_database(self):
        """Initialize user authentication database tables."""
        print(f"[DEBUG] _init_database using path: {self.db_path}")
        print(f"[DEBUG] db_path repr: {repr(self.db_path)}")
        print(f"[DEBUG] DB file exists: {os.path.exists(self.db_path)}")
        print(f"[DEBUG] DB dir exists: {os.path.exists(os.path.dirname(self.db_path))}")
        print(f"[DEBUG] DB dir permissions: {oct(os.stat(os.path.dirname(self.db_path)).st_mode)}")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
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
            """)

            # User sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # Friends table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_friends (
                    friendship_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    friend_id TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',  -- pending, accepted, blocked
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (friend_id) REFERENCES users (user_id),
                    UNIQUE(user_id, friend_id)
                )
            """)

            # Chat messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    message_id TEXT PRIMARY KEY,
                    sender_id TEXT NOT NULL,
                    room_id TEXT NOT NULL,  -- 'global', 'party_<id>', 'dm_<user_id>'
                    message TEXT NOT NULL,
                    message_type TEXT DEFAULT 'text',  -- text, system, emote
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users (user_id)
                )
            """)

            # Online status table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS online_status (
                    user_id TEXT PRIMARY KEY,
                    is_online BOOLEAN DEFAULT FALSE,
                    status TEXT DEFAULT 'offline',
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    current_game TEXT,  -- game_id if in match
                    party_id TEXT,  -- party_id if in party
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_tracker_profile ON users(tracker_gg_profile)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_friends_user_id ON user_friends(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_room_id ON chat_messages(room_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_online_status ON online_status(is_online)")

            conn.commit()

    def authenticate_with_tracker(self, tracker_username: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with Tracker.gg SMITE 2 profile."""
        if not self.tracker_scraper:
            return {"error": "Tracker.gg integration not available"}

        try:
            # Get profile from Tracker.gg
            profile = self.tracker_scraper.get_player_profile(tracker_username)
            if not profile:
                return {"error": "Profile not found on Tracker.gg"}

            # Check if user exists in our database
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
                    "is_new_user": False
                }
            else:
                # Create new user
                user_data = self._create_user_from_tracker(tracker_username, profile)
                if user_data:
                    token = self.create_session(user_data['user_id'])

                    return {
                        "success": True,
                        "user": user_data,
                        "token": token,
                        "profile": profile,
                        "is_new_user": True
                    }
                else:
                    return {"error": "Failed to create user account"}

        except Exception as e:
            return {"error": f"Authentication failed: {str(e)}"}

    def _create_user_from_tracker(self, tracker_username: str, profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create new user from Tracker.gg profile."""
        try:
            user_id = f"user_{secrets.token_hex(8)}"

            # Extract data from Tracker.gg profile
            stats = profile.get('stats', {})
            recent_matches = profile.get('recent_matches', [])

            # Determine favorite role and gods from recent matches
            role_counts = {}
            god_counts = {}

            for _match in recent_matches[:10]:  # Last 10 matches
                role = match.get('role', 'Unknown')
                god = match.get('god_name', 'Unknown')
                role_counts[role] = role_counts.get(role, 0) + 1
                god_counts[god] = god_counts.get(god, 0) + 1

            favorite_role = max(role_counts.items(), key=lambda x: x[1])[0] if role_counts else None
            favorite_gods = [god for god, count in sorted(god_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

            user_data = {
                'user_id': user_id,
                'username': tracker_username,
                'tracker_gg_profile': tracker_username,
                'avatar_url': profile.get('avatar_url'),
                'rank': stats.get('rank', 'Unranked'),
                'level': stats.get('level', 1),
                'favorite_role': favorite_role,
                'favorite_gods': favorite_gods,
                'join_date': datetime.now(),
                'last_login': datetime.now(),
                'is_online': True,
                'status': 'online',
                'bio': "SMITE 2 player from Tracker.gg"
            }

            # Insert into database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (
                        user_id, username, tracker_gg_profile, avatar_url, rank, level,
                        favorite_role, favorite_gods, join_date, last_login, is_online, status, bio
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data['user_id'], user_data['username'], user_data['tracker_gg_profile'],
                    user_data['avatar_url'], user_data['rank'], user_data['level'],
                    user_data['favorite_role'], ','.join(user_data['favorite_gods']),
                    user_data['join_date'], user_data['last_login'], user_data['is_online'],
                    user_data['status'], user_data['bio']
                ))

                # Add to online status table
                cursor.execute("""
                    INSERT INTO online_status (user_id, is_online, status, last_seen)
                    VALUES (?, ?, ?, ?)
                """, (user_data['user_id'], True, 'online', datetime.now()))

                conn.commit()

            return user_data

        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def register_user(self, username: str, email: str, password: str, tracker_gg_profile: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user with site credentials."""
        try:
            # Check if username already exists
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    return {"error": "Username already exists"}

                # Check if email already exists
                if email:
                    cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
                    if cursor.fetchone():
                        return {"error": "Email already registered"}

            # Hash the password
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Generate user ID
            user_id = f"user_{secrets.token_hex(8)}"

            # Create user data
            user_data = {
                'user_id': user_id,
                'username': username,
                'email': email,
                'tracker_gg_profile': tracker_gg_profile or username,  # Use username as fallback
                'join_date': datetime.now(),
                'last_login': datetime.now(),
                'is_online': True,
                'status': 'online',
                'bio': f"SMITE 2 player - {username}"
            }

            # Insert into database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (
                        user_id, username, email, password_hash, tracker_gg_profile, join_date,
                        last_login, is_online, status, bio
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data['user_id'], user_data['username'], user_data['email'],
                    password_hash, user_data['tracker_gg_profile'], user_data['join_date'],
                    user_data['last_login'], user_data['is_online'], user_data['status'],
                    user_data['bio']
                ))

                # Add to online status table
                cursor.execute("""
                    INSERT INTO online_status (user_id, is_online, status, last_seen)
                    VALUES (?, ?, ?, ?)
                """, (user_data['user_id'], True, 'online', datetime.now()))

                conn.commit()

            # Create session token
            token = self.create_session(user_id)

            return {
                "success": True,
                "user": user_data,
                "token": token,
                "is_new_user": True
            }

        except Exception as e:
            print(f"Error registering user: {e}")
            return {"error": f"Registration failed: {str(e)}"}

    def authenticate_with_credentials(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        try:
            # Hash the password for comparison
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM users WHERE username = ?
                """, (username,))

                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for _desc in cursor.description]
                    user_data = dict(zip(columns, row))

                    # Check if password hash matches
                    stored_password_hash = user_data.get('password_hash')
                    if not stored_password_hash:
                        return {"error": "Account not properly configured"}

                    if stored_password_hash != password_hash:
                        return {"error": "Invalid username or password"}

                    # Parse favorite gods
                    if user_data.get('favorite_gods'):
                        user_data['favorite_gods'] = user_data['favorite_gods'].split(',')
                    else:
                        user_data['favorite_gods'] = []

                    # Update last login and online status
                    self.update_user_login(user_data['user_id'])
                    self.set_user_online(user_data['user_id'])

                    # Generate new session token
                    token = self.create_session(user_data['user_id'])

                    return {
                        "success": True,
                        "user": user_data,
                        "token": token,
                        "is_new_user": False
                    }

            return {"error": "Invalid username or password"}

        except Exception as e:
            print(f"Error authenticating user: {e}")
            return {"error": f"Authentication failed: {str(e)}"}

    def get_user_by_tracker_profile(self, tracker_username: str) -> Optional[Dict[str, Any]]:
        """Get user by Tracker.gg profile name."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users WHERE tracker_gg_profile = ?
            """, (tracker_username,))

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for _desc in cursor.description]
                user_data = dict(zip(columns, row))

                # Parse favorite gods
                if user_data.get('favorite_gods'):
                    user_data['favorite_gods'] = user_data['favorite_gods'].split(',')
                else:
                    user_data['favorite_gods'] = []

                return user_data
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by user ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for _desc in cursor.description]
                user_data = dict(zip(columns, row))

                # Parse favorite gods
                if user_data.get('favorite_gods'):
                    user_data['favorite_gods'] = user_data['favorite_gods'].split(',')
                else:
                    user_data['favorite_gods'] = []

                return user_data
            return None

    def create_session(self, user_id: str, expires_in_hours: int = 24) -> str:
        """Create a new session for user."""
        if not jwt:
            raise ImportError("JWT library not available. Install with: pip install PyJWT")

        session_id = f"session_{secrets.token_hex(16)}"
        token = jwt.encode(
            {
                'user_id': user_id,
                'session_id': session_id,
                'exp': datetime.utcnow() + timedelta(hours=expires_in_hours)
            },
            self.secret_key,
            algorithm='HS256'
        )

        expires_at = datetime.now() + timedelta(hours=expires_in_hours)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_sessions (session_id, user_id, token, expires_at)
                VALUES (?, ?, ?, ?)
            """, (session_id, user_id, token, expires_at))
            conn.commit()

        return token

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return user data."""
        if not jwt:
            return None

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
            session_id = payload.get('session_id')

            if not user_id or not session_id:
                return None

            # Check if session exists and is valid
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM user_sessions
                    WHERE session_id = ? AND user_id = ? AND expires_at > ?
                """, (session_id, user_id, datetime.now()))

                if cursor.fetchone():
                    return self.get_user_by_id(user_id)

            return None

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def update_user_login(self, user_id: str):
        """Update user's last login time."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET last_login = ? WHERE user_id = ?
            """, (datetime.now(), user_id))
            conn.commit()

    def set_user_online(self, user_id: str, status: str = "online"):
        """Set user as online."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Update users table
            cursor.execute("""
                UPDATE users SET is_online = ?, status = ? WHERE user_id = ?
            """, (True, status, user_id))

            # Update online_status table
            cursor.execute("""
                INSERT OR REPLACE INTO online_status (user_id, is_online, status, last_seen)
                VALUES (?, ?, ?, ?)
            """, (user_id, True, status, datetime.now()))

            conn.commit()

    def set_user_offline(self, user_id: str):
        """Set user as offline."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Update users table
            cursor.execute("""
                UPDATE users SET is_online = ?, status = ? WHERE user_id = ?
            """, (False, "offline", user_id))

            # Update online_status table
            cursor.execute("""
                UPDATE online_status SET is_online = ?, status = ?, last_seen = ?
                WHERE user_id = ?
            """, (False, "offline", datetime.now(), user_id))

            conn.commit()

    def get_online_users(self) -> List[Dict[str, Any]]:
        """Get list of online users."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.user_id, u.username, u.avatar_url, u.rank, u.level,
                       u.favorite_role, u.status, os.last_seen, os.current_game, os.party_id
                FROM users u
                JOIN online_status os ON u.user_id = os.user_id
                WHERE os.is_online = TRUE
                ORDER BY os.last_seen DESC
            """)

            users = []
            for _row in cursor.fetchall():
                users.append({
                    'user_id': row[0],
                    'username': row[1],
                    'avatar_url': row[2],
                    'rank': row[3],
                    'level': row[4],
                    'favorite_role': row[5],
                    'status': row[6],
                    'last_seen': row[7],
                    'current_game': row[8],
                    'party_id': row[9]
                })

            return users

    def search_users(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search users by username."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, username, avatar_url, rank, level, favorite_role, is_online, status
                FROM users
                WHERE username LIKE ?
                ORDER BY is_online DESC, username ASC
                LIMIT ?
            """, (f"%{query}%", limit))

            users = []
            for _row in cursor.fetchall():
                users.append({
                    'user_id': row[0],
                    'username': row[1],
                    'avatar_url': row[2],
                    'rank': row[3],
                    'level': row[4],
                    'favorite_role': row[5],
                    'is_online': bool(row[6]),
                    'status': row[7]
                })

            return users

    def add_friend(self, user_id: str, friend_username: str) -> Dict[str, Any]:
        """Add a friend request."""
        # Get friend's user_id
        friend = self.get_user_by_tracker_profile(friend_username)
        if not friend:
            return {"error": "User not found"}

        if user_id == friend['user_id']:
            return {"error": "Cannot add yourself as friend"}

        friendship_id = f"friendship_{secrets.token_hex(8)}"

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_friends (friendship_id, user_id, friend_id, status)
                    VALUES (?, ?, ?, ?)
                """, (friendship_id, user_id, friend['user_id'], 'pending'))
                conn.commit()

            return {"success": True, "message": "Friend request sent"}

        except sqlite3.IntegrityError:
            return {"error": "Friend request already exists"}

    def get_friends(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's friends list."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.user_id, u.username, u.avatar_url, u.rank, u.level,
                       u.favorite_role, u.is_online, u.status, uf.status as friendship_status
                FROM user_friends uf
                JOIN users u ON (uf.friend_id = u.user_id OR uf.user_id = u.user_id)
                WHERE (uf.user_id = ? OR uf.friend_id = ?)
                AND u.user_id != ?
                AND uf.status = 'accepted'
            """, (user_id, user_id, user_id))

            friends = []
            for _row in cursor.fetchall():
                friends.append({
                    'user_id': row[0],
                    'username': row[1],
                    'avatar_url': row[2],
                    'rank': row[3],
                    'level': row[4],
                    'favorite_role': row[5],
                    'is_online': bool(row[6]),
                    'status': row[7],
                    'friendship_status': row[8]
                })

            return friends

    def logout(self, token: str) -> bool:
        """Logout user by invalidating session."""
        if not jwt:
            return False

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            session_id = payload.get('session_id')

            if session_id:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM user_sessions WHERE session_id = ?", (session_id,))
                    conn.commit()

                return True
        except Exception:
            pass

        return False

    def cleanup(self):
        """Clean up resources including WebDriver instances."""
        if self._tracker_scraper is not None:
            try:
                if hasattr(self._tracker_scraper, 'driver') and self._tracker_scraper.driver:
                    self._tracker_scraper.driver.quit()
                    print("🔧 WebDriver cleaned up successfully")
            except Exception as e:
                print(f"⚠️ Error cleaning up WebDriver: {e}")
            finally:
                self._tracker_scraper = None
