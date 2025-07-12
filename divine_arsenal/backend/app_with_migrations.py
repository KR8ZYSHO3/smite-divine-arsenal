#!/usr/bin/env python3
"""
Flask app with PostgreSQL migrations for SMITE 2 Divine Arsenal
Enhanced with build optimization endpoints
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from typing import Dict, List, Any, Optional

# Add project root to path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Add backend directory to path for local imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import database configuration with absolute imports (Grok's suggestion)
try:
    from divine_arsenal.backend.database_config import get_database_config
except ImportError:
    # Fallback for different execution contexts
    from database_config import get_database_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with template directory
template_dir = os.path.join(backend_dir, 'templates')
app = Flask(__name__, template_folder=template_dir)

# Load database configuration
db_config = get_database_config()
flask_config = db_config.get_flask_config()

# Apply configuration to Flask app
for key, value in flask_config.items():
    app.config[key] = value

# Additional Flask configuration
app.config.update({
    'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
    'JSON_SORT_KEYS': False,
    'PROPAGATE_EXCEPTIONS': True,
})

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Import legacy database for migration reference (absolute import)
try:
    from divine_arsenal.backend.database import Database as LegacyDatabase
    logger.info("✅ Legacy database imported for migration reference")
except ImportError:
    try:
        from database import Database as LegacyDatabase
        logger.info("✅ Legacy database imported for migration reference")
    except ImportError as e:
        logger.warning(f"Could not import legacy database: {e}")


# SQLAlchemy Models for Migration
class God(db.Model):
    """God model for SQLAlchemy."""
    __tablename__ = 'gods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(50))
    damage_type = db.Column(db.String(20))
    pantheon = db.Column(db.String(50))

    # Stats
    health = db.Column(db.Float, default=0.0)
    mana = db.Column(db.Float, default=0.0)
    physical_power = db.Column(db.Float, default=0.0)
    magical_power = db.Column(db.Float, default=0.0)
    physical_protection = db.Column(db.Float, default=0.0)
    magical_protection = db.Column(db.Float, default=0.0)
    attack_speed = db.Column(db.Float, default=0.0)
    movement_speed = db.Column(db.Float, default=0.0)

    # Scaling
    health_per_level = db.Column(db.Float, default=0.0)
    mana_per_level = db.Column(db.Float, default=0.0)
    physical_power_per_level = db.Column(db.Float, default=0.0)
    magical_power_per_level = db.Column(db.Float, default=0.0)
    physical_protection_per_level = db.Column(db.Float, default=0.0)
    magical_protection_per_level = db.Column(db.Float, default=0.0)

    # Metadata
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'damage_type': self.damage_type,
            'pantheon': self.pantheon,
            'health': self.health,
            'mana': self.mana,
            'physical_power': self.physical_power,
            'magical_power': self.magical_power,
            'physical_protection': self.physical_protection,
            'magical_protection': self.magical_protection,
            'attack_speed': self.attack_speed,
            'movement_speed': self.movement_speed,
            'health_per_level': self.health_per_level,
            'mana_per_level': self.mana_per_level,
            'physical_power_per_level': self.physical_power_per_level,
            'magical_power_per_level': self.magical_power_per_level,
            'physical_protection_per_level': self.physical_protection_per_level,
            'magical_protection_per_level': self.magical_protection_per_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Item(db.Model):
    """Item model for SQLAlchemy."""
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    cost = db.Column(db.Integer, default=0)
    tier = db.Column(db.Integer, default=1)
    category = db.Column(db.String(50))

    # Stats
    health = db.Column(db.Float, default=0.0)
    mana = db.Column(db.Float, default=0.0)
    physical_power = db.Column(db.Float, default=0.0)
    magical_power = db.Column(db.Float, default=0.0)
    physical_protection = db.Column(db.Float, default=0.0)
    magical_protection = db.Column(db.Float, default=0.0)
    attack_speed = db.Column(db.Float, default=0.0)
    movement_speed = db.Column(db.Float, default=0.0)
    penetration = db.Column(db.Float, default=0.0)
    critical_chance = db.Column(db.Float, default=0.0)
    cooldown_reduction = db.Column(db.Float, default=0.0)
    lifesteal = db.Column(db.Float, default=0.0)

    # Descriptions
    passive_description = db.Column(db.Text)
    active_description = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'tier': self.tier,
            'category': self.category,
            'health': self.health,
            'mana': self.mana,
            'physical_power': self.physical_power,
            'magical_power': self.magical_power,
            'physical_protection': self.physical_protection,
            'magical_protection': self.magical_protection,
            'attack_speed': self.attack_speed,
            'movement_speed': self.movement_speed,
            'penetration': self.penetration,
            'critical_chance': self.critical_chance,
            'cooldown_reduction': self.cooldown_reduction,
            'lifesteal': self.lifesteal,
            'passive_description': self.passive_description,
            'active_description': self.active_description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Patch(db.Model):
    """Patch model for SQLAlchemy."""
    __tablename__ = 'patches'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100))
    release_date = db.Column(db.Date)
    
    # Patch notes data
    god_changes = db.Column(db.Text)  # JSON
    item_changes = db.Column(db.Text)  # JSON
    system_changes = db.Column(db.Text)  # JSON
    
    # Metadata
    source = db.Column(db.String(50), default='hirez')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'version': self.version,
            'name': self.name,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'god_changes': self.god_changes,
            'item_changes': self.item_changes,
            'system_changes': self.system_changes,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Community Models
class User(db.Model):
    """User model for community features."""
    __tablename__ = 'users'
    
    user_id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255))
    
    # Profile information
    tracker_username = db.Column(db.String(100))
    rank = db.Column(db.String(50))
    favorite_gods = db.Column(db.Text)  # JSON array
    favorite_roles = db.Column(db.Text)  # JSON array
    discord_id = db.Column(db.String(100))
    steam_id = db.Column(db.String(100))
    bio = db.Column(db.Text)
    
    # Status
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=db.func.current_timestamp())
    current_party_id = db.Column(db.String(50))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'tracker_username': self.tracker_username,
            'rank': self.rank,
            'favorite_gods': self.favorite_gods,
            'favorite_roles': self.favorite_roles,
            'discord_id': self.discord_id,
            'steam_id': self.steam_id,
            'bio': self.bio,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'current_party_id': self.current_party_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ChatMessage(db.Model):
    """Chat message model."""
    __tablename__ = 'chat_messages'
    
    message_id = db.Column(db.String(50), primary_key=True)
    sender_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    room_id = db.Column(db.String(100), nullable=False)  # 'global', 'party_<id>', 'dm_<user_id>'
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, system, emote
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationship
    sender = db.relationship('User', backref='messages')

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.username if self.sender else 'Unknown',
            'room_id': self.room_id,
            'message': self.message,
            'message_type': self.message_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Party(db.Model):
    """Party model for group formation."""
    __tablename__ = 'parties'
    
    party_id = db.Column(db.String(50), primary_key=True)
    leader_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    max_members = db.Column(db.Integer, default=5)
    is_public = db.Column(db.Boolean, default=True)
    game_mode = db.Column(db.String(50), default='conquest')
    skill_level = db.Column(db.String(50), default='any')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    leader = db.relationship('User', backref='led_parties')

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'party_id': self.party_id,
            'leader_id': self.leader_id,
            'leader_name': self.leader.username if self.leader else 'Unknown',
            'name': self.name,
            'description': self.description,
            'max_members': self.max_members,
            'is_public': self.is_public,
            'game_mode': self.game_mode,
            'skill_level': self.skill_level,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# PostgreSQL Adapter (MOVED AFTER MODELS)
class PostgreSQLAdapter:
    """Adapter to make SQLAlchemy models work with legacy build optimizers."""
    
    def __init__(self, app=None):
        self.app = app or globals()['app']
    
    def get_all_gods(self):
        """Get all gods from PostgreSQL database."""
        try:
            with self.app.app_context():
                gods = God.query.all()
                return [god.to_dict() for god in gods]
        except Exception as e:
            logger.error(f"Error fetching gods from PostgreSQL: {e}")
            return []
    
    def get_all_items(self):
        """Get all items from PostgreSQL database."""
        try:
            with self.app.app_context():
                items = Item.query.all()
                return [item.to_dict() for item in items]
        except Exception as e:
            logger.error(f"Error fetching items from PostgreSQL: {e}")
            return []
            
    def get_item(self, name: str):
        """Get a specific item by name."""
        try:
            with self.app.app_context():
                item = Item.query.filter_by(name=name).first()
                return item.to_dict() if item else None
        except Exception as e:
            logger.error(f"Error fetching item {name}: {e}")
            return None
    
    def get_god(self, name: str):
        """Get a specific god by name."""
        try:
            with self.app.app_context():
                god = God.query.filter_by(name=name).first()
                return god.to_dict() if god else None
        except Exception as e:
            logger.error(f"Error fetching god {name}: {e}")
            return None
    
    def get_patches(self):
        """Get all patches from PostgreSQL database."""
        try:
            with self.app.app_context():
                patches = Patch.query.all()
                return [patch.to_dict() for patch in patches]
        except Exception as e:
            logger.error(f"Error fetching patches from PostgreSQL: {e}")
            return []
    
    def get_connection(self):
        """Get database connection for legacy compatibility."""
        return self.app.app_context()
    
    def close(self):
        """Close database connection for legacy compatibility."""
        pass


# Initialize build optimizers AFTER models and adapter are defined
build_optimizer = None
advanced_optimizer = None
enhanced_optimizer = None

try:
    # Initialize PostgreSQL adapter
    postgres_adapter = PostgreSQLAdapter(app)
    logger.info("✅ PostgreSQL adapter initialized")
    
    # Import and initialize build optimizers with PostgreSQL data
    from divine_arsenal.backend.simple_build_optimizer import SimpleBuildOptimizer
    build_optimizer = SimpleBuildOptimizer(postgres_adapter)  # type: ignore
    logger.info("✅ Simple build optimizer initialized")
    
    try:
        from divine_arsenal.backend.working_build_optimizer import WorkingBuildOptimizer
        advanced_optimizer = WorkingBuildOptimizer(postgres_adapter)  # type: ignore
        logger.info("✅ Advanced build optimizer initialized")
    except ImportError as e:
        logger.warning(f"Advanced optimizer not available: {e}")
    
    try:
        from divine_arsenal.backend.enhanced_build_optimizer import EnhancedBuildOptimizer
        enhanced_optimizer = EnhancedBuildOptimizer(postgres_adapter)  # type: ignore
        logger.info("✅ Enhanced build optimizer initialized")
    except ImportError as e:
        logger.warning(f"Enhanced optimizer not available: {e}")
        
except Exception as e:
    logger.error(f"Error initializing build optimizers: {e}")

# Initialize other components
statistical_analyzer = None
build_explainer = None
patch_analyzer = None
user_auth = None
community_dashboard = None

try:
    from divine_arsenal.backend.postgres_statistical_analyzer import PostgreSQLStatisticalAnalyzer
    statistical_analyzer = PostgreSQLStatisticalAnalyzer()
    logger.info("✅ PostgreSQL Statistical analyzer initialized")
except Exception as e:
    logger.warning(f"Statistical analyzer not available: {e}")

try:
    from divine_arsenal.backend.postgres_user_auth import PostgreSQLUserAuth
    user_auth = PostgreSQLUserAuth()
    logger.info("✅ PostgreSQL User Auth initialized")
except Exception as e:
    logger.warning(f"PostgreSQL User Auth not available: {e}")

try:
    from divine_arsenal.backend.build_explainer import BuildExplainer
    build_explainer = BuildExplainer()
    logger.info("✅ Build explainer initialized")
except Exception as e:
    logger.warning(f"Build explainer not available: {e}")

try:
    from divine_arsenal.backend.patch_meta_analyzer import PatchMetaAnalyzer
    patch_analyzer = PatchMetaAnalyzer()
    logger.info("✅ Patch analyzer initialized")
except Exception as e:
    logger.warning(f"Patch analyzer not available: {e}")

# Initialize community components for PostgreSQL
user_auth = None
community_dashboard = None

try:
    # Import PostgreSQL-compatible community components
    from postgresql_community_auth import PostgreSQLUserAuth
    
    # Create PostgreSQL-compatible auth system
    user_auth = PostgreSQLUserAuth(db.session, User)
    
    # Create simple community dashboard (PostgreSQL-compatible)
    class PostgreSQLCommunityDashboard:
        """Simple PostgreSQL-compatible community dashboard."""
        
        def __init__(self, db_session, models):
            self.db = db_session
            self.User = models['User']
            self.ChatMessage = models['ChatMessage']
            self.Party = models['Party']
        
        def get_online_users(self):
            """Get online users."""
            try:
                cutoff_time = datetime.now() - timedelta(minutes=30)
                users = self.User.query.filter(
                    self.User.is_online == True,
                    self.User.last_seen > cutoff_time
                ).all()
                return [user.to_dict() for user in users]
            except Exception as e:
                logger.error(f"Error getting online users: {e}")
                return []
        
        def get_community_stats(self):
            """Get basic community statistics."""
            try:
                return {
                    'total_users': self.User.query.count(),
                    'online_users': len(self.get_online_users()),
                    'total_messages': self.ChatMessage.query.count(),
                    'total_parties': self.Party.query.count()
                }
            except Exception as e:
                logger.error(f"Error getting community stats: {e}")
                return {}
        
        def get_chat_messages(self, room_id: str, limit: int = 50):
            """Get chat messages for a room."""
            try:
                messages = self.ChatMessage.query.filter_by(room_id=room_id)\
                    .order_by(self.ChatMessage.created_at.desc())\
                    .limit(limit).all()
                return [msg.to_dict() for msg in reversed(messages)]
            except Exception as e:
                logger.error(f"Error getting chat messages: {e}")
                return []
        
        def get_public_parties(self):
            """Get public parties."""
            try:
                parties = self.Party.query.filter_by(is_public=True)\
                    .order_by(self.Party.created_at.desc()).all()
                return [party.to_dict() for party in parties]
            except Exception as e:
                logger.error(f"Error getting public parties: {e}")
                return []
        
        def log_user_activity(self, user_id: str, activity: str, metadata: dict):
            """Log user activity (simple implementation)."""
            logger.info(f"User {user_id} activity: {activity} - {metadata}")
    
    community_dashboard = PostgreSQLCommunityDashboard(db.session, {
        'User': User,
        'ChatMessage': ChatMessage,
        'Party': Party
    })
    
    logger.info("✅ Community components initialized")
    
    # Register community API with PostgreSQL auth
    try:
        # Create a simple community API blueprint for PostgreSQL
        from flask import Blueprint
        
        community_bp = Blueprint('community', __name__, url_prefix='/api/community')
        
        @community_bp.route('/health', methods=['GET'])
        def community_health_check():
            """Community health check endpoint."""
            try:
                online_count = len(community_dashboard.get_online_users())
                return jsonify({
                    "status": "healthy",
                    "online_users": online_count,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
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
                return jsonify({"error": "Failed to get community stats"}), 500
        
        @community_bp.route('/users/online', methods=['GET'])
        def get_online_users():
            """Get online users."""
            try:
                users = community_dashboard.get_online_users()
                return jsonify({
                    "success": True,
                    "users": users,
                    "count": len(users)
                })
            except Exception as e:
                return jsonify({"error": "Failed to get online users"}), 500
        
        app.register_blueprint(community_bp)
        logger.info("✅ Community API registered successfully")
    except Exception as e:
        logger.warning(f"Community API registration failed: {e}")
        
except Exception as e:
    logger.warning(f"Community components not available: {e}")

# Initialize Flask session management
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False


# Frontend Routes
@app.route('/')
def home():
    """Home page - serve the enhanced dashboard."""
    return render_template('enhanced_dashboard.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page - serve the enhanced dashboard."""
    return render_template('enhanced_dashboard.html')

# Community Routes
@app.route("/login", methods=["GET", "POST"])
def login_page():
    """Login page with form handling."""
    if not user_auth:
        return render_template('login.html', error="Authentication system unavailable")

    if request.method == "POST":
        # Handle form submission
        username = request.form.get('username')
        password = request.form.get('password')
        tracker_username = request.form.get('tracker_username')
        login_type = request.form.get('login_type')

        if login_type == 'tracker' and tracker_username:
            # Tracker.gg login
            result = user_auth.authenticate_with_tracker(tracker_username)
            if result and "error" not in result:
                session['user_id'] = result['user']['user_id']
                session['token'] = result['token']
                return redirect(url_for('community_page'))
            else:
                return render_template('login.html', error="Invalid Tracker.gg username")
        elif username and password:
            # Site credentials login
            result = user_auth.authenticate_with_credentials(username, password)
            if result and "error" not in result:
                session['user_id'] = result['user']['user_id']
                session['token'] = result['token']
                return redirect(url_for('community_page'))
            else:
                return render_template('login.html', error="Invalid username or password")
        else:
            return render_template('login.html', error="Please provide login credentials")

    return render_template('login.html')

@app.route("/logout")
def logout():
    """Logout and clear session."""
    session.clear()
    return redirect(url_for('home'))

@app.route("/community")
def community_page():
    """Community dashboard page with data."""
    # Check if user is logged in, but don't force login
    is_authenticated = 'user_id' in session and user_auth

    if not is_authenticated:
        # Show community page with login prompt instead of forcing redirect
        return render_template('community.html',
                             current_user=None,
                             online_users=[],
                             parties=[],
                             messages=[],
                             stats={},
                             login_required=True,
                             error="Please log in to access community features")

    if not user_auth:
        return render_template('community.html',
                             current_user=None,
                             online_users=[],
                             parties=[],
                             messages=[],
                             stats={},
                             error="Authentication system unavailable")

    try:
        # Get current user
        current_user = user_auth.get_user_by_id(session['user_id'])

        # Get community data
        online_users = user_auth.get_online_users() if hasattr(user_auth, 'get_online_users') else []
        parties = community_dashboard.get_public_parties() if community_dashboard and hasattr(community_dashboard, 'get_public_parties') else []
        messages = community_dashboard.get_chat_messages('global') if community_dashboard and hasattr(community_dashboard, 'get_chat_messages') else []
        stats = community_dashboard.get_community_stats() if community_dashboard and hasattr(community_dashboard, 'get_community_stats') else {}

        return render_template('community.html',
                             current_user=current_user,
                             online_users=online_users,
                             parties=parties,
                             messages=messages,
                             stats=stats)
    except Exception as e:
        logger.error(f"Error loading community page: {e}")
        return render_template('community.html',
                             current_user=None,
                             online_users=[],
                             parties=[],
                             messages=[],
                             stats={})

# Enhanced health check endpoint (following Grok's suggestion)
@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring with DB connectivity test."""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        db.session.commit()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'version': '1.0.0',
            'components': {
                'database': 'connected',
                'build_optimizer': 'ready' if build_optimizer else 'unavailable',
                'advanced_optimizer': 'ready' if advanced_optimizer else 'unavailable',
                'enhanced_optimizer': 'ready' if enhanced_optimizer else 'unavailable',
                'statistical_analyzer': 'ready' if statistical_analyzer else 'unavailable',
                'build_explainer': 'ready' if build_explainer else 'unavailable',
                'patch_analyzer': 'ready' if patch_analyzer else 'unavailable',
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }), 500

# Build Optimization endpoints
@app.route("/api/optimize-build", methods=["POST"])
def optimize_build():
    """Optimize build for a specific god and role."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        god = data.get("god")
        role = data.get("role")
        mode = data.get("mode", "Conquest")
        budget = data.get("budget", 15000)

        if not god or not role:
            return jsonify({"error": "God and role are required"}), 400

        logger.info(f"Optimizing build for {god} ({role}) in {mode} with budget {budget}g")

        # Try advanced optimizer first, fallback to simple
        build_result = None
        
        if advanced_optimizer:
            try:
                build_result = advanced_optimizer.optimize_build(god, role, budget=budget)
                if build_result and "error" not in build_result:
                    logger.info(f"Advanced optimizer succeeded for {god} ({role})")
                else:
                    build_result = None
            except Exception as e:
                logger.warning(f"Advanced optimizer failed: {e}")
                build_result = None

        # Fallback to simple optimizer
        if not build_result and build_optimizer:
            try:
                logger.info(f"Falling back to simple optimizer for {god} ({role})")
                build_result = build_optimizer.get_optimal_build(god, role)
            except Exception as e:
                logger.warning(f"Simple optimizer also failed: {e}")
                build_result = None

        if not build_result:
            return jsonify({
                "error": "Build optimization failed",
                "details": "No optimizers available or all failed"
            }), 500

        return jsonify(build_result)

    except Exception as e:
        logger.error(f"Error optimizing build: {e}")
        return jsonify({"error": "Build optimization failed", "details": str(e)}), 500

@app.route("/api/optimize-build/enhanced", methods=["POST"])
def optimize_build_enhanced():
    """Enhanced build optimization with personalization and multi-mode support."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        god = data.get("god")
        role = data.get("role", "Mid")
        mode = data.get("mode", "Conquest")
        budget = data.get("budget", 15000)
        enemy_gods = data.get("enemy_gods", [])
        
        if not god or not role:
            return jsonify({"error": "God and role are required"}), 400

        logger.info(f"Enhanced optimization for {god} ({role}) in {mode} with budget {budget}g")

        # Try enhanced optimizer first
        if enhanced_optimizer:
            try:
                # Use enhanced optimizer if available
                build_result = enhanced_optimizer.optimize_build(god, role, budget=budget)
                if build_result and "error" not in build_result:
                    # Add enhanced features
                    build_result.update({
                        "mode": mode,
                        "enhanced": True,
                        "enemy_analysis": enemy_gods,
                        "confidence_score": 0.85,
                        "meta_compliance": 0.78
                    })
                    return jsonify(build_result)
            except Exception as e:
                logger.warning(f"Enhanced optimizer failed: {e}")

        # Fallback to advanced optimizer
        if advanced_optimizer:
            try:
                build_result = advanced_optimizer.optimize_build(god, role, budget=budget)
                if build_result and "error" not in build_result:
                    build_result.update({
                        "mode": mode,
                        "enhanced": False,
                        "note": "Fallback to advanced optimizer"
                    })
                    return jsonify(build_result)
            except Exception as e:
                logger.warning(f"Advanced optimizer failed: {e}")

        # Final fallback to simple optimizer
        if build_optimizer:
            try:
                build_result = build_optimizer.get_optimal_build(god, role)
                if build_result:
                    return jsonify({
                        "god": god,
                        "role": role,
                        "mode": mode,
                        "build": build_result,
                        "enhanced": False,
                        "note": "Fallback to simple optimizer"
                    })
            except Exception as e:
                logger.warning(f"Simple optimizer failed: {e}")

        return jsonify({"error": "All optimizers failed"}), 500

    except Exception as e:
        logger.error(f"Error in enhanced build optimization: {e}")
        return jsonify({"error": "Enhanced optimization failed", "details": str(e)}), 500

@app.route("/api/optimize-build/realtime", methods=["POST"])
def optimize_build_realtime():
    """Real-time build optimization with enemy composition analysis."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        god = data.get("god")
        role = data.get("role", "Mid")
        enemy_gods = data.get("enemy_gods", [])
        detected_items = data.get("detected_items", {})
        budget = data.get("budget", 15000)
        playstyle = data.get("playstyle", "meta")
        current_items = data.get("current_items", [])
        game_time = data.get("game_time", 0)
        
        if not god or not role:
            return jsonify({"error": "God and role are required"}), 400

        logger.info(f"Real-time optimization for {god} ({role}) against {enemy_gods}")

        # Try enhanced optimizer with real-time method if available
        if enhanced_optimizer and hasattr(enhanced_optimizer, 'optimize_build_real_time'):
            try:
                recommendation = enhanced_optimizer.optimize_build_real_time(
                    god_name=god,
                    role=role,
                    enemy_gods=enemy_gods,
                    detected_items=detected_items,
                    budget=budget,
                    playstyle=playstyle
                )
                
                # Convert to JSON-serializable format
                result = {
                    "success": True,
                    "god": god,
                    "role": role,
                    "core_build": recommendation.core_build if hasattr(recommendation, 'core_build') else [],
                    "situational_items": recommendation.situational_items if hasattr(recommendation, 'situational_items') else [],
                    "counter_items": recommendation.counter_items if hasattr(recommendation, 'counter_items') else [],
                    "confidence_score": recommendation.confidence_score if hasattr(recommendation, 'confidence_score') else 0.8,
                    "meta_compliance": recommendation.meta_compliance if hasattr(recommendation, 'meta_compliance') else 0.7,
                    "reasoning": recommendation.reasoning if hasattr(recommendation, 'reasoning') else "Real-time optimization based on enemy composition",
                    "enemy_analysis": {
                        "gods": enemy_gods,
                        "detected_items": detected_items,
                        "threat_level": "moderate"
                    }
                }
                return jsonify(result)
            except Exception as e:
                logger.warning(f"Enhanced real-time optimizer failed: {e}")

        # Fallback to regular enhanced/advanced optimizer
        optimizer = enhanced_optimizer or advanced_optimizer
        if optimizer:
            try:
                build_result = optimizer.optimize_build(god, role, budget=budget)
                if build_result and "error" not in build_result:
                    result = {
                        "success": True,
                        "god": god,
                        "role": role,
                        "core_build": build_result.get("items", []),
                        "situational_items": [],
                        "counter_items": [],
                        "confidence_score": 0.75,
                        "meta_compliance": 0.65,
                        "reasoning": "Standard build optimization (real-time features limited)",
                        "enemy_analysis": {
                            "gods": enemy_gods,
                            "detected_items": detected_items,
                            "threat_level": "unknown"
                        },
                        "note": "Real-time features limited - using standard optimizer"
                    }
                    return jsonify(result)
            except Exception as e:
                logger.warning(f"Fallback optimizer failed: {e}")

        return jsonify({
            "success": False,
            "error": "Real-time optimizer not available",
            "details": "Enhanced optimizer with real-time capabilities required"
        }), 503

    except Exception as e:
        logger.error(f"Error in real-time build optimization: {e}")
        return jsonify({
            "success": False,
            "error": "Real-time optimization failed",
            "details": str(e)
        }), 500

@app.route("/api/enhanced-optimize", methods=["POST"])
def enhanced_optimize():
    """Enhanced build optimization with enemy analysis."""
    try:
        if not enhanced_optimizer:
            return jsonify({"error": "Enhanced optimizer not available"}), 503
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        god = data.get("god")
        role = data.get("role")
        enemy_gods = data.get("enemy_gods", [])
        game_mode = data.get("game_mode", "Conquest")
        
        if not god or not role:
            return jsonify({"error": "God and role are required"}), 400

        # Placeholder for enhanced optimization - implement based on actual methods available
        result = {
            "god": god,
            "role": role,
            "enemy_gods": enemy_gods,
            "game_mode": game_mode,
            "build": ["Sovereignty", "Heartward Amulet", "Spectral Armor", "Mystical Mail", "Mantle of Discord", "Spirit Robe"],
            "reasoning": "Counter-build optimized for enemy composition",
            "note": "Enhanced optimizer integration pending"
        }
        
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in enhanced optimization: {e}")
        return jsonify({"error": "Enhanced optimization failed", "details": str(e)}), 500

@app.route("/api/explain-build", methods=["POST"])
def explain_build():
    """Explain why a build is optimal."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        god = data.get("god")
        role = data.get("role")
        items = data.get("items", [])
        budget = data.get("budget", 15000)
        
        if not god or not role:
            return jsonify({"error": "God and role are required"}), 400

        logger.info(f"Explaining build for {god} ({role})")

        # If no items provided, get an optimized build first
        if not items:
            # Try to get a build to explain
            optimizer = enhanced_optimizer or advanced_optimizer or build_optimizer
            if optimizer:
                try:
                    if hasattr(optimizer, 'optimize_build'):
                        build_result = optimizer.optimize_build(god, role, budget=budget)
                        if build_result and isinstance(build_result, dict):
                            items = build_result.get("items", [])
                    elif hasattr(optimizer, 'get_optimal_build'):
                        build_result = optimizer.get_optimal_build(god, role)
                        if build_result and isinstance(build_result, dict):
                            items = build_result.get("items", [])
                        elif isinstance(build_result, list):
                            items = build_result
                except Exception as e:
                    logger.warning(f"Could not get build for explanation: {e}")

        # Generate explanation
        if build_explainer and items:
            try:
                # Try to use the actual build explainer
                explanation = build_explainer.explain_complete_build({"items": items, "god": god, "role": role})
                return jsonify({
                    "success": True,
                    "god": god,
                    "role": role,
                    "items": items,
                    "explanation": explanation
                })
            except Exception as e:
                logger.warning(f"Build explainer failed: {e}")

        # Fallback to basic explanation
        if items:
            explanation = f"Build for {god} ({role}) with items: {', '.join(items)}. This build provides balanced stats and synergies optimized for the {role} role in Conquest mode."
        else:
            explanation = f"Unable to generate build explanation for {god} ({role}). No items available for analysis."
        
        return jsonify({
            "success": True,
            "god": god,
            "role": role,
            "items": items,
            "explanation": explanation,
            "note": "Basic explanation - enhanced explainer integration pending"
        })

    except Exception as e:
        logger.error(f"Error explaining build: {e}")
        return jsonify({"error": "Build explanation failed", "details": str(e)}), 500

@app.route("/api/statistical-analysis", methods=["POST"])
def statistical_analysis():
    """Perform statistical analysis on build performance."""
    try:
        if not statistical_analyzer:
            return jsonify({"error": "Statistical analyzer not available"}), 503
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        god = data.get("god")
        role = data.get("role")
        
        if not god or not role:
            return jsonify({"error": "God and role are required"}), 400

        # Placeholder analysis - implement based on actual methods available
        analysis = {
            "god": god,
            "role": role,
            "win_rate": 0.65,
            "pick_rate": 0.15,
            "ban_rate": 0.08,
            "avg_kda": 2.3,
            "performance_trend": "stable",
            "note": "Statistical analysis integration pending"
        }
        
        return jsonify(analysis)

    except Exception as e:
        logger.error(f"Error in statistical analysis: {e}")
        return jsonify({"error": "Statistical analysis failed", "details": str(e)}), 500

@app.route("/api/realtime-optimize", methods=["POST"])
def realtime_optimize():
    """Real-time build optimization during match."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        god = data.get("god")
        role = data.get("role")
        current_items = data.get("current_items", [])
        game_time = data.get("game_time", 0)
        gold = data.get("gold", 500)
        
        if not god or not role:
            return jsonify({"error": "God and role are required"}), 400

        # Use enhanced optimizer if available, otherwise advanced
        optimizer = enhanced_optimizer or advanced_optimizer
        
        if not optimizer:
            return jsonify({"error": "Real-time optimizer not available"}), 503

        result = {
            "god": god,
            "role": role,
            "current_items": current_items,
            "game_time": game_time,
            "gold": gold,
            "next_item_recommendation": "Sovereignty",  # Placeholder
            "reasoning": "Based on current game state and enemy composition"
        }
        
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in real-time optimization: {e}")
        return jsonify({"error": "Real-time optimization failed", "details": str(e)}), 500


@app.route('/api/migration/status')
def migration_status():
    """Get migration status."""
    try:
        # Check if tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        expected_tables = ['gods', 'items', 'patches', 'user_auth']
        existing_tables = [table for table in expected_tables if table in tables]
        missing_tables = [table for table in expected_tables if table not in tables]

        # Count records in existing tables
        table_counts = {}
        for table_name in existing_tables:
            try:
                from sqlalchemy import text
                result = db.session.execute(text(f'SELECT COUNT(*) FROM {table_name}'))
                count = result.scalar()
                table_counts[table_name] = count
            except Exception as e:
                table_counts[table_name] = f"Error: {e}"

        return jsonify({
            'database_type': db_config.get_database_type(),
            'existing_tables': existing_tables,
            'missing_tables': missing_tables,
            'table_counts': table_counts,
            'migration_needed': len(missing_tables) > 0 or any(count == 0 for _count in table_counts.values() if isinstance(count, int))
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'migration_needed': True
        }), 500


@app.route('/api/gods')
def get_gods():
    """Get all gods from the database."""
    try:
        gods = God.query.all()
        return jsonify([god.to_dict() for god in gods])
    except Exception as e:
        logger.error(f"Error fetching gods: {e}")
        return jsonify({'error': 'Failed to fetch gods'}), 500


@app.route('/api/items')
def get_items():
    """Get all items from the database."""
    try:
        items = Item.query.all()
        return jsonify([item.to_dict() for item in items])
    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        return jsonify({'error': 'Failed to fetch items'}), 500


@app.route('/api/patches')
def get_patches():
    """Get all patches."""
    try:
        patches = Patch.query.all()
        return jsonify([patch.to_dict() for patch in patches])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """Get database statistics."""
    try:
        gods_count = God.query.count()
        items_count = Item.query.count()
        patches_count = Patch.query.count()
        
        return jsonify({
            'gods': gods_count,
            'items': items_count,
            'patches': patches_count,
            'total_records': gods_count + items_count + patches_count
        })
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': 'Failed to fetch stats'}), 500


# Tracker.gg Integration endpoints
@app.route('/api/tracker/profile/<username>')
def get_tracker_profile(username):
    """Get player profile from Tracker.gg."""
    try:
        # Placeholder implementation - actual Tracker.gg integration would go here
        profile = {
            'username': username,
            'rank': 'Gold III',
            'wins': 45,
            'losses': 32,
            'winrate': 58.4,
            'favorite_gods': ['Zeus', 'Hecate', 'Loki'],
            'recent_matches': [
                {'god': 'Zeus', 'role': 'Mid', 'result': 'Win', 'kda': '12/3/8'},
                {'god': 'Hecate', 'role': 'Mid', 'result': 'Loss', 'kda': '8/5/12'},
                {'god': 'Loki', 'role': 'Jungle', 'result': 'Win', 'kda': '15/2/6'}
            ],
            'note': 'Tracker.gg integration pending - placeholder data'
        }
        
        return jsonify(profile)
    except Exception as e:
        logger.error(f"Error fetching tracker profile: {e}")
        return jsonify({'error': 'Failed to fetch tracker profile'}), 500


@app.route('/api/tracker/match/<match_id>')
def get_match_details(match_id):
    """Get match details from Tracker.gg."""
    try:
        # Placeholder implementation
        match_details = {
            'match_id': match_id,
            'mode': 'Conquest',
            'duration': '28:45',
            'result': 'Victory',
            'players': [
                {'username': 'TestPlayer', 'god': 'Zeus', 'role': 'Mid', 'kda': '12/3/8'},
                {'username': 'Player2', 'god': 'Apollo', 'role': 'Carry', 'kda': '8/2/10'}
            ],
            'note': 'Tracker.gg integration pending - placeholder data'
        }
        
        return jsonify(match_details)
    except Exception as e:
        logger.error(f"Error fetching match details: {e}")
        return jsonify({'error': 'Failed to fetch match details'}), 500


@app.route('/api/tracker/leaderboard')
def get_leaderboard():
    """Get leaderboard from Tracker.gg."""
    try:
        # Placeholder implementation
        leaderboard = {
            'top_players': [
                {'rank': 1, 'username': 'ProPlayer1', 'mmr': 2850, 'winrate': 72.3},
                {'rank': 2, 'username': 'ProPlayer2', 'mmr': 2820, 'winrate': 69.8},
                {'rank': 3, 'username': 'ProPlayer3', 'mmr': 2795, 'winrate': 68.5}
            ],
            'note': 'Tracker.gg integration pending - placeholder data'
        }
        
        return jsonify(leaderboard)
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        return jsonify({'error': 'Failed to fetch leaderboard'}), 500


if __name__ == "__main__":
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        logger.info("✅ Database tables created/verified")
    
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    logger.info(f"🚀 Starting SMITE 2 Divine Arsenal on port {port}")
    logger.info(f"🔗 Database: {db_config.get_database_type()}")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False  # Disable debug in production
    )
