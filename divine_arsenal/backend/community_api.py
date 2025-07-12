#!/usr/bin/env python3
"""
Community API Endpoints for SMITE 2 Divine Arsenal
Provides REST API for user authentication, chat, and community features
"""

import logging
from datetime import datetime
from functools import wraps
from typing import Dict, Any

from flask import Blueprint, request, jsonify, current_app, g
from flask_cors import CORS

from user_auth import UserAuth
from community_dashboard import CommunityDashboard

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
community_bp = Blueprint('community', __name__, url_prefix='/api/community')
CORS(community_bp)

# Initialize components
user_auth = UserAuth()
community_dashboard = CommunityDashboard()


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required"}), 401

        token = auth_header.split(' ')[1]
        user = user_auth.validate_token(token)

        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Add user to request context using g
        from flask import g
        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


# Authentication endpoints
@community_bp.route('/auth/login', methods=['POST'])
def login():
    """Login with Tracker.gg SMITE 2 profile."""
    try:
        data = request.get_json()
        tracker_username = data.get('tracker_username')

        if not tracker_username:
            return jsonify({"error": "Tracker.gg username required"}), 400

        result = user_auth.authenticate_with_tracker(tracker_username)

        if result and "error" in result:
            return jsonify(result), 400

        if not result or "user" not in result:
            return jsonify({"error": "Authentication failed"}), 400

        # Log activity
        community_dashboard.log_user_activity(
            result['user']['user_id'],
            'login',
            {'tracker_username': tracker_username}
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500


@community_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user with site credentials."""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        tracker_gg_profile = data.get('tracker_gg_profile')  # Optional

        if not username or not email or not password:
            return jsonify({"error": "Username, email, and password are required"}), 400

        # Basic validation
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        result = user_auth.register_user(username, email, password, tracker_gg_profile)

        if result and "error" in result:
            return jsonify(result), 400

        if not result or "user" not in result:
            return jsonify({"error": "Registration failed"}), 400

        # Log activity
        community_dashboard.log_user_activity(
            result['user']['user_id'],
            'register',
            {'username': username, 'email': email}
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": "Registration failed"}), 500


@community_bp.route('/auth/login', methods=['POST'])
def login_site():
    """Login with site credentials (username/password)."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        result = user_auth.authenticate_with_credentials(username, password)

        if result and "error" in result:
            return jsonify(result), 400

        if not result or "user" not in result:
            return jsonify({"error": "Invalid username or password"}), 400

        # Log activity
        community_dashboard.log_user_activity(
            result['user']['user_id'],
            'login',
            {'username': username}
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500


@community_bp.route('/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user."""
    try:
        from flask import g
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header required"}), 400

        token = auth_header.split(' ')[1]

        success = user_auth.logout(token)
        if success:
            # Set user offline
            user_auth.set_user_offline(g.current_user['user_id'])

            # Log activity
            community_dashboard.log_user_activity(
                g.current_user['user_id'],
                'logout'
            )

            return jsonify({"success": True, "message": "Logged out successfully"})
        else:
            return jsonify({"error": "Logout failed"}), 400

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"error": "Logout failed"}), 500


@community_bp.route('/auth/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get current user profile."""
    from flask import g
    return jsonify({
        "success": True,
        "user": g.current_user
    })


# Online users endpoints
@community_bp.route('/users/online', methods=['GET'])
def get_online_users():
    """Get list of online users."""
    try:
        users = community_dashboard.get_online_users()
        return jsonify({
            "success": True,
            "users": users,
            "count": len(users)
        })
    except Exception as e:
        logger.error(f"Error getting online users: {e}")
        return jsonify({"error": "Failed to get online users"}), 500


@community_bp.route('/users/search', methods=['GET'])
def search_users():
    """Search users by username."""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)

        if not query:
            return jsonify({"error": "Search query required"}), 400

        users = community_dashboard.search_users(query, limit)
        return jsonify({
            "success": True,
            "users": users,
            "query": query
        })
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        return jsonify({"error": "Search failed"}), 500


@community_bp.route('/users/by-role/<role>', methods=['GET'])
def get_users_by_role(role):
    """Get online users by role."""
    try:
        users = community_dashboard.get_users_by_role(role)
        return jsonify({
            "success": True,
            "users": users,
            "role": role,
            "count": len(users)
        })
    except Exception as e:
        logger.error(f"Error getting users by role: {e}")
        return jsonify({"error": "Failed to get users by role"}), 500


# Chat endpoints
@community_bp.route('/chat/messages/<room_id>', methods=['GET'])
def get_chat_messages(room_id):
    """Get chat messages for a room."""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        messages = community_dashboard.get_chat_messages(room_id, limit, offset)
        return jsonify({
            "success": True,
            "messages": messages,
            "room_id": room_id
        })
    except Exception as e:
        logger.error(f"Error getting chat messages: {e}")
        return jsonify({"error": "Failed to get messages"}), 500


@community_bp.route('/chat/send', methods=['POST'])
@require_auth
def send_message():
    """Send a chat message."""
    try:
        data = request.get_json()
        room_id = data.get('room_id')
        message = data.get('message')
        message_type = data.get('message_type', 'text')

        if not room_id or not message:
            return jsonify({"error": "Room ID and message required"}), 400

        result = community_dashboard.send_chat_message(
            g.current_user['user_id'],
            room_id,
            message,
            message_type
        )

        if "error" in result:
            return jsonify(result), 400

        # Log activity
        community_dashboard.log_user_activity(
            g.current_user['user_id'],
            'send_message',
            {'room_id': room_id, 'message_type': message_type}
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({"error": "Failed to send message"}), 500


# Party endpoints
@community_bp.route('/parties', methods=['GET'])
def get_public_parties():
    """Get list of public parties."""
    try:
        parties = community_dashboard.get_public_parties()
        return jsonify({
            "success": True,
            "parties": parties,
            "count": len(parties)
        })
    except Exception as e:
        logger.error(f"Error getting parties: {e}")
        return jsonify({"error": "Failed to get parties"}), 500


@community_bp.route('/parties', methods=['POST'])
@require_auth
def create_party():
    """Create a new party."""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        max_members = data.get('max_members', 5)
        game_mode = data.get('game_mode', 'conquest')
        skill_level = data.get('skill_level', 'any')
        is_public = data.get('is_public', True)

        if not name:
            return jsonify({"error": "Party name required"}), 400

        result = community_dashboard.create_party(
            g.current_user['user_id'],
            name,
            description,
            max_members,
            game_mode,
            skill_level,
            is_public
        )

        if "error" in result:
            return jsonify(result), 400

        # Log activity
        community_dashboard.log_user_activity(
            g.current_user['user_id'],
            'create_party',
            {'party_name': name, 'game_mode': game_mode}
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error creating party: {e}")
        return jsonify({"error": "Failed to create party"}), 500


@community_bp.route('/parties/<party_id>/join', methods=['POST'])
@require_auth
def join_party(party_id):
    """Join a party."""
    try:
        result = community_dashboard.join_party(g.current_user['user_id'], party_id)

        if "error" in result:
            return jsonify(result), 400

        # Log activity
        community_dashboard.log_user_activity(
            g.current_user['user_id'],
            'join_party',
            {'party_id': party_id}
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error joining party: {e}")
        return jsonify({"error": "Failed to join party"}), 500


@community_bp.route('/parties/<party_id>/leave', methods=['POST'])
@require_auth
def leave_party(party_id):
    """Leave a party."""
    try:
        result = community_dashboard.leave_party(g.current_user['user_id'], party_id)

        if "error" in result:
            return jsonify(result), 400

        # Log activity
        community_dashboard.log_user_activity(
            g.current_user['user_id'],
            'leave_party',
            {'party_id': party_id}
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error leaving party: {e}")
        return jsonify({"error": "Failed to leave party"}), 500


@community_bp.route('/parties/<party_id>/members', methods=['GET'])
def get_party_members(party_id):
    """Get members of a party."""
    try:
        members = community_dashboard.get_party_members(party_id)
        return jsonify({
            "success": True,
            "members": members,
            "party_id": party_id,
            "count": len(members)
        })
    except Exception as e:
        logger.error(f"Error getting party members: {e}")
        return jsonify({"error": "Failed to get party members"}), 500


@community_bp.route('/parties/my', methods=['GET'])
@require_auth
def get_my_parties():
    """Get parties that the current user is in."""
    try:
        parties = community_dashboard.get_user_parties(g.current_user['user_id'])
        return jsonify({
            "success": True,
            "parties": parties,
            "count": len(parties)
        })
    except Exception as e:
        logger.error(f"Error getting user parties: {e}")
        return jsonify({"error": "Failed to get user parties"}), 500


# Friends endpoints
@community_bp.route('/friends', methods=['GET'])
@require_auth
def get_friends():
    """Get user's friends list."""
    try:
        friends = user_auth.get_friends(g.current_user['user_id'])
        return jsonify({
            "success": True,
            "friends": friends,
            "count": len(friends)
        })
    except Exception as e:
        logger.error(f"Error getting friends: {e}")
        return jsonify({"error": "Failed to get friends"}), 500


@community_bp.route('/friends/add', methods=['POST'])
@require_auth
def add_friend():
    """Add a friend request."""
    try:
        data = request.get_json()
        friend_username = data.get('friend_username')

        if not friend_username:
            return jsonify({"error": "Friend username required"}), 400

        result = user_auth.add_friend(g.current_user['user_id'], friend_username)

        if "error" in result:
            return jsonify(result), 400

        # Log activity
        community_dashboard.log_user_activity(
            g.current_user['user_id'],
            'add_friend',
            {'friend_username': friend_username}
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error adding friend: {e}")
        return jsonify({"error": "Failed to add friend"}), 500


# Community stats endpoint
@community_bp.route('/stats', methods=['GET'])
def get_community_stats():
    """Get community statistics."""
    try:
        stats = community_dashboard.get_community_stats()
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Error getting community stats: {e}")
        return jsonify({"error": "Failed to get community stats"}), 500


# Health check endpoint
@community_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        online_count = community_dashboard.get_online_users_count()
        return jsonify({
            "status": "healthy",
            "online_users": online_count,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500
