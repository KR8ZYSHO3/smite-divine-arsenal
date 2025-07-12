#!/usr/bin/env python3
"""
Real-Time Build Updates using Flask-SocketIO
Implements Grok's recommendations for real-time WebSocket updates
"""

import logging
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional

from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
import jwt

from enhanced_build_optimizer import EnhancedBuildOptimizer
from tracker_realtime import TrackerRealtimeCollector
from user_auth import UserAuth

logger = logging.getLogger(__name__)


class RealtimeBuildsManager:
    """
    Real-time builds manager using Flask-SocketIO.
    
    Implements Grok's recommendations:
    - Hybrid approach: REST for initial loads, SocketIO for updates
    - JWT authentication on connections
    - Namespaces for organization
    - Rate limiting and error handling
    - Background polling for Tracker.gg updates
    """
    
    def __init__(self, socketio: SocketIO, enhanced_optimizer: EnhancedBuildOptimizer, user_auth: UserAuth):
        self.socketio = socketio
        self.enhanced_optimizer = enhanced_optimizer
        self.user_auth = user_auth
        self.tracker_collector = TrackerRealtimeCollector()
        
        # Active sessions tracking
        self.active_sessions = {}  # session_id -> session_data
        self.user_sessions = {}    # user_id -> session_id
        
        # Background polling
        self.polling_active = False
        self.polling_thread = None
        
        # Rate limiting
        self.user_requests = {}  # user_id -> request_count
        self.rate_limit = 10  # requests per minute
        
        self._register_socket_handlers()
    
    def _register_socket_handlers(self):
        """Register SocketIO event handlers."""
        
        @self.socketio.on('connect', namespace='/realtime-builds')
        def handle_connect(auth):
            """Handle client connection with JWT authentication."""
            try:
                # Validate JWT token
                token = auth.get('token') if auth else None
                if not token:
                    logger.warning("Connection rejected: No token provided")
                    return False
                
                user = self.user_auth.validate_token(token)
                if not user:
                    logger.warning("Connection rejected: Invalid token")
                    return False
                
                user_id = user.get('user_id')
                session_id = request.sid
                
                # Store session info
                self.active_sessions[session_id] = {
                    'user_id': user_id,
                    'username': user.get('username', 'Unknown'),
                    'connected_at': datetime.now(),
                    'current_match': None,
                    'last_build': None
                }
                
                self.user_sessions[user_id] = session_id
                
                logger.info(f"User {user.get('username')} connected to real-time builds")
                
                emit('connected', {
                    'message': 'Real-time build updates enabled',
                    'user': user.get('username'),
                    'timestamp': datetime.now().isoformat()
                })
                
                # Start background polling if not already active
                if not self.polling_active:
                    self._start_background_polling()
                
                return True
                
            except Exception as e:
                logger.error(f"Error in connect handler: {e}")
                return False
        
        @self.socketio.on('disconnect', namespace='/realtime-builds')
        def handle_disconnect():
            """Handle client disconnection."""
            try:
                session_id = request.sid
                if session_id in self.active_sessions:
                    session_data = self.active_sessions[session_id]
                    user_id = session_data['user_id']
                    username = session_data['username']
                    
                    # Clean up session data
                    del self.active_sessions[session_id]
                    if user_id in self.user_sessions:
                        del self.user_sessions[user_id]
                    
                    logger.info(f"User {username} disconnected from real-time builds")
                
            except Exception as e:
                logger.error(f"Error in disconnect handler: {e}")
        
        @self.socketio.on('join_match', namespace='/realtime-builds')
        def handle_join_match(data):
            """Handle user joining a match for real-time updates."""
            try:
                session_id = request.sid
                if session_id not in self.active_sessions:
                    emit('error', {'message': 'Session not found'})
                    return
                
                # Rate limiting
                user_id = self.active_sessions[session_id]['user_id']
                if not self._check_rate_limit(user_id):
                    emit('error', {'message': 'Rate limit exceeded'})
                    return
                
                # Validate input data
                required_fields = ['god_name', 'role', 'match_id']
                for field in required_fields:
                    if field not in data:
                        emit('error', {'message': f'Missing required field: {field}'})
                        return
                
                god_name = data['god_name']
                role = data['role']
                match_id = data['match_id']
                enemy_gods = data.get('enemy_gods', [])
                
                # Join match room
                join_room(match_id)
                
                # Update session data
                self.active_sessions[session_id]['current_match'] = {
                    'match_id': match_id,
                    'god_name': god_name,
                    'role': role,
                    'enemy_gods': enemy_gods,
                    'joined_at': datetime.now()
                }
                
                # Get initial build recommendation
                recommendation = self.enhanced_optimizer.optimize_build_real_time(
                    god_name=god_name,
                    role=role,
                    enemy_gods=enemy_gods,
                    playstyle=data.get('playstyle', 'meta')
                )
                
                # Store last build
                self.active_sessions[session_id]['last_build'] = recommendation
                
                # Send initial build
                emit('build_update', {
                    'type': 'initial',
                    'god': god_name,
                    'role': role,
                    'core_build': recommendation.core_build,
                    'situational_items': recommendation.situational_items,
                    'counter_items': recommendation.counter_items,
                    'enemy_analysis': {
                        'composition_type': recommendation.enemy_analysis.composition_type,
                        'threat_level': recommendation.enemy_analysis.threat_level
                    },
                    'confidence_score': recommendation.confidence_score,
                    'meta_compliance': recommendation.meta_compliance,
                    'reasoning': recommendation.reasoning,
                    'timestamp': datetime.now().isoformat()
                })
                
                logger.info(f"User joined match {match_id} as {god_name} ({role})")
                
            except Exception as e:
                logger.error(f"Error in join_match handler: {e}")
                emit('error', {'message': 'Failed to join match'})
        
        @self.socketio.on('leave_match', namespace='/realtime-builds')
        def handle_leave_match():
            """Handle user leaving a match."""
            try:
                session_id = request.sid
                if session_id in self.active_sessions:
                    match_data = self.active_sessions[session_id].get('current_match')
                    if match_data:
                        match_id = match_data['match_id']
                        leave_room(match_id)
                        self.active_sessions[session_id]['current_match'] = None
                        
                        emit('match_left', {
                            'message': 'Left match successfully',
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        logger.info(f"User left match {match_id}")
                
            except Exception as e:
                logger.error(f"Error in leave_match handler: {e}")
        
        @self.socketio.on('update_enemy_items', namespace='/realtime-builds')
        def handle_update_enemy_items(data):
            """Handle manual enemy item updates from user."""
            try:
                session_id = request.sid
                if session_id not in self.active_sessions:
                    emit('error', {'message': 'Session not found'})
                    return
                
                # Rate limiting
                user_id = self.active_sessions[session_id]['user_id']
                if not self._check_rate_limit(user_id):
                    emit('error', {'message': 'Rate limit exceeded'})
                    return
                
                match_data = self.active_sessions[session_id].get('current_match')
                if not match_data:
                    emit('error', {'message': 'Not in a match'})
                    return
                
                # Update enemy items
                detected_items = data.get('detected_items', {})
                enemy_gods = data.get('enemy_gods', match_data['enemy_gods'])
                
                # Get updated build recommendation
                recommendation = self.enhanced_optimizer.optimize_build_real_time(
                    god_name=match_data['god_name'],
                    role=match_data['role'],
                    enemy_gods=enemy_gods,
                    detected_items=detected_items,
                    playstyle=data.get('playstyle', 'meta')
                )
                
                # Check if build changed significantly
                last_build = self.active_sessions[session_id].get('last_build')
                if self._build_changed_significantly(last_build, recommendation):
                    # Update session
                    self.active_sessions[session_id]['last_build'] = recommendation
                    
                    # Emit to match room
                    self.socketio.emit('build_update', {
                        'type': 'enemy_update',
                        'god': match_data['god_name'],
                        'role': match_data['role'],
                        'core_build': recommendation.core_build,
                        'situational_items': recommendation.situational_items,
                        'counter_items': recommendation.counter_items,
                        'enemy_analysis': {
                            'composition_type': recommendation.enemy_analysis.composition_type,
                            'threat_level': recommendation.enemy_analysis.threat_level,
                            'detected_items': detected_items
                        },
                        'confidence_score': recommendation.confidence_score,
                        'meta_compliance': recommendation.meta_compliance,
                        'reasoning': recommendation.reasoning,
                        'timestamp': datetime.now().isoformat()
                    }, room=match_data['match_id'], namespace='/realtime-builds')
                    
                    logger.info(f"Build updated for match {match_data['match_id']} due to enemy item changes")
                
            except Exception as e:
                logger.error(f"Error in update_enemy_items handler: {e}")
                emit('error', {'message': 'Failed to update enemy items'})
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limits."""
        now = datetime.now()
        
        if user_id not in self.user_requests:
            self.user_requests[user_id] = {'count': 0, 'reset_time': now}
        
        user_data = self.user_requests[user_id]
        
        # Reset if minute has passed
        if (now - user_data['reset_time']).total_seconds() >= 60:
            user_data['count'] = 0
            user_data['reset_time'] = now
        
        # Check limit
        if user_data['count'] >= self.rate_limit:
            return False
        
        user_data['count'] += 1
        return True
    
    def _build_changed_significantly(self, old_build, new_build) -> bool:
        """Check if build changed significantly enough to warrant an update."""
        if not old_build or not new_build:
            return True
        
        # Compare core builds
        old_core = set(old_build.core_build)
        new_core = set(new_build.core_build)
        
        # If core build changed by more than 1 item, it's significant
        if len(old_core.symmetric_difference(new_core)) > 1:
            return True
        
        # Compare counter items
        old_counters = set(old_build.counter_items)
        new_counters = set(new_build.counter_items)
        
        # If counter items changed, it's significant
        if old_counters != new_counters:
            return True
        
        # Compare threat level
        old_threat = old_build.enemy_analysis.threat_level
        new_threat = new_build.enemy_analysis.threat_level
        
        # If threat level changed by more than 0.2, it's significant
        if abs(old_threat - new_threat) > 0.2:
            return True
        
        return False
    
    def _start_background_polling(self):
        """Start background polling for Tracker.gg updates."""
        if self.polling_active:
            return
        
        self.polling_active = True
        self.polling_thread = threading.Thread(target=self._background_polling_loop)
        self.polling_thread.daemon = True
        self.polling_thread.start()
        
        logger.info("Started background polling for real-time updates")
    
    def _background_polling_loop(self):
        """Background polling loop for Tracker.gg updates."""
        while self.polling_active and self.active_sessions:
            try:
                # Poll for each active match
                for session_id, session_data in list(self.active_sessions.items()):
                    match_data = session_data.get('current_match')
                    if not match_data:
                        continue
                    
                    # Check for updates from Tracker.gg
                    # This would integrate with your TrackerRealtimeCollector
                    # For now, we'll simulate periodic updates
                    
                    # In a real implementation, you'd:
                    # 1. Poll Tracker.gg for enemy item updates
                    # 2. Compare with last known state
                    # 3. Emit updates if significant changes detected
                
                # Sleep for polling interval
                time.sleep(60)  # Poll every minute
                
            except Exception as e:
                logger.error(f"Error in background polling: {e}")
                time.sleep(30)  # Back off on error
        
        self.polling_active = False
        logger.info("Stopped background polling")
    
    def stop_polling(self):
        """Stop background polling."""
        self.polling_active = False
        if self.polling_thread:
            self.polling_thread.join(timeout=5)
    
    def get_status(self) -> Dict[str, Any]:
        """Get real-time builds manager status."""
        return {
            'active_sessions': len(self.active_sessions),
            'active_matches': len([s for s in self.active_sessions.values() if s.get('current_match')]),
            'polling_active': self.polling_active,
            'rate_limit': self.rate_limit,
            'status': 'operational'
        } 