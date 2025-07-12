#!/usr/bin/env python3
"""
Community Dashboard System for SMITE 2 Divine Arsenal
Provides chat, online players, and community features
"""

import sqlite3
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from user_auth import UserAuth


@dataclass
class ChatMessage:
    """Chat message data structure."""
    message_id: str
    sender_id: str
    sender_name: str
    room_id: str
    message: str
    message_type: str = "text"  # text, system, emote
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Party:
    """Party/group data structure."""
    party_id: str
    leader_id: str
    name: str
    description: str
    max_members: int = 5
    current_members: List[str] = field(default_factory=list)
    is_public: bool = True
    game_mode: str = "conquest"
    skill_level: str = "any"  # any, casual, competitive
    created_at: datetime = field(default_factory=datetime.now)


class CommunityDashboard:
    """Community dashboard with chat, parties, and social features."""

    def __init__(self, db_path: str = "divine_arsenal/backend/divine_arsenal.db"):
        self.db_path = db_path
        self.user_auth = UserAuth(db_path)
        self._init_community_tables()

    def _init_community_tables(self):
        """Initialize community database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Parties table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parties (
                    party_id TEXT PRIMARY KEY,
                    leader_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    max_members INTEGER DEFAULT 5,
                    current_members TEXT,  -- JSON array of user_ids
                    is_public BOOLEAN DEFAULT TRUE,
                    game_mode TEXT DEFAULT 'conquest',
                    skill_level TEXT DEFAULT 'any',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (leader_id) REFERENCES users (user_id)
                )
            """)

            # Party members table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS party_members (
                    party_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    role TEXT DEFAULT 'member',  -- leader, member
                    PRIMARY KEY (party_id, user_id),
                    FOREIGN KEY (party_id) REFERENCES parties (party_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # Game sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    session_id TEXT PRIMARY KEY,
                    party_id TEXT,
                    game_mode TEXT NOT NULL,
                    status TEXT DEFAULT 'waiting',  -- waiting, in_game, finished
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    ended_at TIMESTAMP,
                    FOREIGN KEY (party_id) REFERENCES parties (party_id)
                )
            """)

            # User activity table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    activity_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,  -- login, logout, join_party, leave_party, start_game
                    details TEXT,  -- JSON details
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_parties_leader ON parties(leader_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_parties_public ON parties(is_public)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_party_members_party ON party_members(party_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_party_members_user ON party_members(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_room_created ON chat_messages(room_id, created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_activity_user ON user_activity(user_id, created_at)")

            conn.commit()

    def get_online_users(self) -> List[Dict[str, Any]]:
        """Get list of online users with additional info."""
        return self.user_auth.get_online_users()

    def get_online_users_count(self) -> int:
        """Get count of online users."""
        users = self.get_online_users()
        return len(users)

    def search_online_users(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search online users by username."""
        all_users = self.get_online_users()
        filtered_users = [
            user for _user in all_users
            if query.lower() in user['username'].lower()
        ]
        return filtered_users[:limit]

    def search_users(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search all users by username."""
        return self.user_auth.search_users(query, limit)

    def get_users_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Get online users by their favorite role."""
        all_users = self.get_online_users()
        return [
            user for _user in all_users
            if user.get('favorite_role', '').lower() == role.lower()
        ]

    def send_chat_message(self, sender_id: str, room_id: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """Send a chat message."""
        try:
            message_id = f"msg_{secrets.token_hex(8)}"

            # Get sender info
            sender = self.user_auth.get_user_by_id(sender_id)
            if not sender:
                return {"error": "User not found"}

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO chat_messages (message_id, sender_id, room_id, message, message_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (message_id, sender_id, room_id, message, message_type))
                conn.commit()

            return {
                "success": True,
                "message_id": message_id,
                "sender_name": sender['username'],
                "message": message,
                "message_type": message_type,
                "created_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Failed to send message: {str(e)}"}

    def get_chat_messages(self, room_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get chat messages for a room."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cm.message_id, cm.sender_id, u.username, cm.room_id,
                       cm.message, cm.message_type, cm.created_at
                FROM chat_messages cm
                JOIN users u ON cm.sender_id = u.user_id
                WHERE cm.room_id = ?
                ORDER BY cm.created_at DESC
                LIMIT ? OFFSET ?
            """, (room_id, limit, offset))

            messages = []
            for _row in cursor.fetchall():
                messages.append({
                    'message_id': row[0],
                    'sender_id': row[1],
                    'sender_name': row[2],
                    'room_id': row[3],
                    'message': row[4],
                    'message_type': row[5],
                    'created_at': row[6]
                })

            return list(reversed(messages))  # Return in chronological order

    def create_party(self, leader_id: str, name: str, description: str = "",
                    max_members: int = 5, game_mode: str = "conquest",
                    skill_level: str = "any", is_public: bool = True) -> Dict[str, Any]:
        """Create a new party."""
        try:
            party_id = f"party_{secrets.token_hex(8)}"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO parties (party_id, leader_id, name, description, max_members,
                                       game_mode, skill_level, is_public, current_members)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (party_id, leader_id, name, description, max_members,
                     game_mode, skill_level, is_public, json.dumps([leader_id])))

                # Add leader to party members
                cursor.execute("""
                    INSERT INTO party_members (party_id, user_id, role)
                    VALUES (?, ?, ?)
                """, (party_id, leader_id, 'leader'))

                conn.commit()

            return {
                "success": True,
                "party_id": party_id,
                "message": "Party created successfully"
            }

        except Exception as e:
            return {"error": f"Failed to create party: {str(e)}"}

    def get_public_parties(self) -> List[Dict[str, Any]]:
        """Get list of public parties."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.party_id, p.leader_id, u.username as leader_name, p.name, p.description,
                       p.max_members, p.current_members, p.game_mode, p.skill_level, p.created_at,
                       COUNT(pm.user_id) as member_count
                FROM parties p
                JOIN users u ON p.leader_id = u.user_id
                LEFT JOIN party_members pm ON p.party_id = pm.party_id
                WHERE p.is_public = TRUE
                GROUP BY p.party_id
                ORDER BY p.created_at DESC
            """)

            parties = []
            for _row in cursor.fetchall():
                current_members = json.loads(row[6]) if row[6] else []
                parties.append({
                    'party_id': row[0],
                    'leader_id': row[1],
                    'leader_name': row[2],
                    'name': row[3],
                    'description': row[4],
                    'max_members': row[5],
                    'current_members': current_members,
                    'game_mode': row[7],
                    'skill_level': row[8],
                    'created_at': row[9],
                    'member_count': row[10]
                })

            return parties

    def join_party(self, user_id: str, party_id: str) -> Dict[str, Any]:
        """Join a party."""
        try:
            # Check if party exists and has space
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.max_members, p.current_members, COUNT(pm.user_id) as member_count
                    FROM parties p
                    LEFT JOIN party_members pm ON p.party_id = pm.party_id
                    WHERE p.party_id = ?
                    GROUP BY p.party_id
                """, (party_id,))

                row = cursor.fetchone()
                if not row:
                    return {"error": "Party not found"}

                max_members, current_members_json, member_count = row
                current_members = json.loads(current_members_json) if current_members_json else []

                if member_count >= max_members:
                    return {"error": "Party is full"}

                if user_id in current_members:
                    return {"error": "Already in party"}

                # Add user to party
                current_members.append(user_id)
                cursor.execute("""
                    UPDATE parties SET current_members = ? WHERE party_id = ?
                """, (json.dumps(current_members), party_id))

                cursor.execute("""
                    INSERT INTO party_members (party_id, user_id, role)
                    VALUES (?, ?, ?)
                """, (party_id, user_id, 'member'))

                conn.commit()

            return {
                "success": True,
                "message": "Joined party successfully"
            }

        except Exception as e:
            return {"error": f"Failed to join party: {str(e)}"}

    def leave_party(self, user_id: str, party_id: str) -> Dict[str, Any]:
        """Leave a party."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if user is in party
                cursor.execute("""
                    SELECT role FROM party_members WHERE party_id = ? AND user_id = ?
                """, (party_id, user_id))

                row = cursor.fetchone()
                if not row:
                    return {"error": "Not in party"}

                role = row[0]

                # Remove from party members
                cursor.execute("""
                    DELETE FROM party_members WHERE party_id = ? AND user_id = ?
                """, (party_id, user_id))

                # Update current members list
                cursor.execute("SELECT current_members FROM parties WHERE party_id = ?", (party_id,))
                row = cursor.fetchone()
                if row:
                    current_members = json.loads(row[0]) if row[0] else []
                    if user_id in current_members:
                        current_members.remove(user_id)
                        cursor.execute("""
                            UPDATE parties SET current_members = ? WHERE party_id = ?
                        """, (json.dumps(current_members), party_id))

                # If leader left, disband party or transfer leadership
                if role == 'leader':
                    cursor.execute("""
                        SELECT user_id FROM party_members WHERE party_id = ? LIMIT 1
                    """, (party_id,))

                    new_leader = cursor.fetchone()
                    if new_leader:
                        # Transfer leadership
                        cursor.execute("""
                            UPDATE party_members SET role = 'leader' WHERE party_id = ? AND user_id = ?
                        """, (party_id, new_leader[0]))

                        cursor.execute("""
                            UPDATE parties SET leader_id = ? WHERE party_id = ?
                        """, (new_leader[0], party_id))
                    else:
                        # Disband party
                        cursor.execute("DELETE FROM parties WHERE party_id = ?", (party_id,))

                conn.commit()

            return {
                "success": True,
                "message": "Left party successfully"
            }

        except Exception as e:
            return {"error": f"Failed to leave party: {str(e)}"}

    def get_party_members(self, party_id: str) -> List[Dict[str, Any]]:
        """Get members of a party."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.user_id, u.username, u.avatar_url, u.rank, u.level,
                       u.favorite_role, u.is_online, u.status, pm.role as party_role
                FROM party_members pm
                JOIN users u ON pm.user_id = u.user_id
                WHERE pm.party_id = ?
                ORDER BY pm.role DESC, u.username ASC
            """, (party_id,))

            members = []
            for _row in cursor.fetchall():
                members.append({
                    'user_id': row[0],
                    'username': row[1],
                    'avatar_url': row[2],
                    'rank': row[3],
                    'level': row[4],
                    'favorite_role': row[5],
                    'is_online': bool(row[6]),
                    'status': row[7],
                    'party_role': row[8]
                })

            return members

    def get_user_parties(self, user_id: str) -> List[Dict[str, Any]]:
        """Get parties that a user is in."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.party_id, p.leader_id, u.username as leader_name, p.name, p.description,
                       p.max_members, p.current_members, p.game_mode, p.skill_level, p.created_at,
                       pm.role as user_role
                FROM party_members pm
                JOIN parties p ON pm.party_id = p.party_id
                JOIN users u ON p.leader_id = u.user_id
                WHERE pm.user_id = ?
                ORDER BY p.created_at DESC
            """, (user_id,))

            parties = []
            for _row in cursor.fetchall():
                current_members = json.loads(row[6]) if row[6] else []
                parties.append({
                    'party_id': row[0],
                    'leader_id': row[1],
                    'leader_name': row[2],
                    'name': row[3],
                    'description': row[4],
                    'max_members': row[5],
                    'current_members': current_members,
                    'game_mode': row[7],
                    'skill_level': row[8],
                    'created_at': row[9],
                    'user_role': row[10]
                })

            return parties

    def log_user_activity(self, user_id: str, activity_type: str, details: Optional[Dict[str, Any]] = None):
        """Log user activity for analytics."""
        try:
            activity_id = f"activity_{secrets.token_hex(8)}"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_activity (activity_id, user_id, activity_type, details)
                    VALUES (?, ?, ?, ?)
                """, (activity_id, user_id, activity_type, json.dumps(details) if details else None))
                conn.commit()

        except Exception as e:
            print(f"Failed to log activity: {e}")

    def get_community_stats(self) -> Dict[str, Any]:
        """Get community statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            # Online users
            cursor.execute("SELECT COUNT(*) FROM online_status WHERE is_online = TRUE")
            online_users = cursor.fetchone()[0]

            # Active parties
            cursor.execute("SELECT COUNT(*) FROM parties")
            total_parties = cursor.fetchone()[0]

            # Active parties with members
            cursor.execute("""
                SELECT COUNT(DISTINCT p.party_id)
                FROM parties p
                JOIN party_members pm ON p.party_id = pm.party_id
            """)
            active_parties = cursor.fetchone()[0]

            # Recent messages (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM chat_messages
                WHERE created_at > datetime('now', '-1 day')
            """)
            recent_messages = cursor.fetchone()[0]

            # Users by role
            cursor.execute("""
                SELECT favorite_role, COUNT(*)
                FROM users
                WHERE favorite_role IS NOT NULL
                GROUP BY favorite_role
                ORDER BY COUNT(*) DESC
            """)
            users_by_role = dict(cursor.fetchall())

            return {
                'total_users': total_users,
                'online_users': online_users,
                'total_parties': total_parties,
                'active_parties': active_parties,
                'recent_messages': recent_messages,
                'users_by_role': users_by_role,
                'online_percentage': round((online_users / total_users * 100) if total_users > 0 else 0, 1)
            }
