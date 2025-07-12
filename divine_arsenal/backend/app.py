"""Flask application for Divine Arsenal."""

import logging
import os
import threading
import traceback  # <-- Add this for error logging
from datetime import datetime, timedelta
from typing import Dict, List

from build_explainer import BuildExplainer
from database import Database
from enhanced_data_collector import EnhancedDataCollector
from flask import Flask, jsonify, render_template, request, g, redirect, url_for, session
from flask_socketio import SocketIO
from multi_mode_optimizer import GameMode, MultiModeOptimizer
from patch_enhancer import PatchNotesEnhancer
from patch_meta_analyzer import PatchMetaAnalyzer
from player_performance_integrator import PlayerPerformanceIntegrator
from scrapers.smite2 import Smite2Scraper
from scrapers.smitebase import SmiteBaseScraper
from scrapers.smitesource import SmiteSourceScraper
from scrapers.tracker import TrackerScraper
from scrapers.wiki_smite2 import WikiSmite2Scraper
from simple_build_optimizer import SimpleBuildOptimizer
from statistical_analyzer import StatisticalAnalyzer
from divine_arsenal.backend.config import *

# Configure logging
logging.basicConfig(
    filename="divine_arsenal.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Register community blueprint
try:
    from community_api import community_bp
    app.register_blueprint(community_bp)
    print("✅ Community API registered successfully")
except ImportError as e:
    print(f"⚠️ Community API not available: {e}")

db = Database()
smite2_scraper = Smite2Scraper()
tracker_scraper = TrackerScraper()
smitesource_scraper = SmiteSourceScraper()
smitebase_scraper = SmiteBaseScraper()
wiki_scraper = WikiSmite2Scraper()
enhancer = PatchNotesEnhancer()

# Initialize build optimizers
try:
    build_optimizer = SimpleBuildOptimizer(db)
    print("✅ Simple build optimizer initialized successfully")

    from working_build_optimizer import WorkingBuildOptimizer

    advanced_optimizer = WorkingBuildOptimizer(db)
    print("✅ Advanced build optimizer initialized successfully")
    print("🚀 Professional build logic enabled with synergies, meta analysis, and counter-building")

    # Initialize enhanced build optimizer with real-time analysis
    from enhanced_build_optimizer import EnhancedBuildOptimizer

    enhanced_optimizer = EnhancedBuildOptimizer(db)
    print("✅ Enhanced build optimizer initialized successfully")
    print("🚀 Real-time enemy analysis and counter-building enabled")

except Exception as e:
    print(f"❌ Error initializing build optimizers: {e}")
    build_optimizer = None
    advanced_optimizer = None
    enhanced_optimizer = None

# Initialize statistical analyzer
statistical_analyzer = StatisticalAnalyzer("statistical_analysis.db")
print("✅ Statistical Analyzer initialized successfully")

# Initialize patch meta analyzer
patch_analyzer = PatchMetaAnalyzer()
print("✅ Patch Meta Analyzer initialized successfully")

# Initialize build explainer
build_explainer = BuildExplainer()
print("✅ Build Explainer initialized successfully")

# Initialize enhanced components
try:
    enhanced_data_collector = EnhancedDataCollector()
    print("✅ Enhanced Data Collector initialized successfully")

    player_integrator = PlayerPerformanceIntegrator()
    print("✅ Player Performance Integrator initialized successfully")

    multi_mode_optimizer = MultiModeOptimizer()
    print("✅ Multi-Mode Optimizer initialized successfully")

    print(
        "🚀 Enhanced features enabled: Player Calibration, Multi-Mode Optimization, Real-time Data Collection"
    )
except Exception as e:
    print(f"❌ Error initializing enhanced components: {e}")
    enhanced_data_collector = None
    player_integrator = None
    multi_mode_optimizer = None

# Initialize user authentication and community components
try:
    from user_auth import UserAuth
    from community_dashboard import CommunityDashboard

    user_auth = UserAuth()
    community_dashboard = CommunityDashboard()
    print("✅ User Authentication & Community Dashboard initialized successfully")
except Exception as e:
    print(f"❌ Error initializing user auth: {e}")
    user_auth = None
    community_dashboard = None


# Rate limiting setup
class RateLimiter:
    """Simple rate limiter using a dictionary to track requests."""

    def __init__(self, requests_per_hour: int = 100):
        """Initialize rate limiter.

        Args:
            requests_per_hour: Maximum requests allowed per hour
        """
        self.requests_per_hour = requests_per_hour
        self.requests: Dict[str, List[datetime]] = {}
        self.lock = threading.Lock()

    def is_allowed(self, ip: str) -> bool:
        """Check if request from IP is allowed.

        Args:
            ip: IP address of the request

        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            now = datetime.now()
            if ip not in self.requests:
                self.requests[ip] = []

            # Remove old requests
            self.requests[ip] = [
                req_time for _req_time in self.requests[ip] if now - req_time < timedelta(hours=1)
            ]

            if len(self.requests[ip]) >= self.requests_per_hour:
                return False

            self.requests[ip].append(now)
            return True


rate_limiter = RateLimiter()


def check_rate_limit():
    """Check rate limit for current request."""
    ip = request.remote_addr or "unknown"
    if not rate_limiter.is_allowed(ip):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    return None


@app.before_request
def before_request():
    """Check rate limit before processing request."""
    if request.path.startswith("/api/"):
        response = check_rate_limit()
        if response:
            return response


@app.route("/")
def home():
    """Main page - accessible without login."""
    return render_template("enhanced_dashboard.html")

@app.route("/dashboard")
def dashboard():
    """Dashboard - accessible without login."""
    return render_template("enhanced_dashboard.html")

@app.route("/guest")
def guest_mode():
    """Guest mode - skip login and go straight to dashboard."""
    return render_template("enhanced_dashboard.html")


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
        online_users = user_auth.get_online_users()
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

@app.route("/logout")
def logout_page():
    """Logout user and redirect to login."""
    if 'token' in session and user_auth:
        user_auth.logout(session['token'])
    session.clear()
    return redirect(url_for('login_page'))

@app.route("/community-old")
def community_dashboard():
    """Community dashboard page."""
    return render_template("community_dashboard.html")


@app.route("/api")
def api_welcome():
    """API welcome endpoint for applications that expect JSON."""
    return jsonify(
        {
            "message": "Welcome to Divine Arsenal - Your Smite 2 Companion",
            "version": "1.0.0",
        }
    )


@app.route("/api/patches", methods=["GET"])
def get_patches():
    """Return all stored patches."""
    limit = request.args.get("limit", type=int)
    return jsonify(db.get_patches(limit))


@app.route("/api/patches/<version>", methods=["GET"])
def get_patch(version: str):
    """Return a specific patch by version."""
    patch = db.get_patch_by_version(version)
    if not patch:
        return jsonify({"error": "Patch not found"}), 404
    return jsonify(patch)


@app.route("/api/patches/update", methods=["POST"])
def update_patches():
    """Fetch and store new patches from Smite2.com."""
    try:
        patches = smite2_scraper.get_patch_notes()
        for _patch in patches:
            # Only add if not already in database
            if not db.get_patch_by_version(patch["version"]):
                db.add_patch(version=patch["version"], date=patch["date"], notes=patch["notes"])
        return jsonify(
            {
                "message": f"Successfully updated {len(patches)} patches",
                "patches": patches,
            }
        )
    except Exception as e:
        logger.error(f"Error updating patches: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<player_name>", methods=["GET"])
def get_player_stats(player_name: str):
    """Get player statistics from Tracker.gg."""
    try:
        if not tracker_scraper:
            return jsonify({"error": "Tracker scraper not available"}), 500

        stats = tracker_scraper.get_player_profile(player_name)
        if not stats:
            return jsonify({"error": "Player not found"}), 404

        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error fetching player stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    """Get leaderboard data from Tracker.gg."""
    try:
        category = request.args.get("category", "kills")
        return jsonify(tracker_scraper.get_leaderboard(category))
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/god/<god_name>/stats", methods=["GET"])
def get_god_stats(god_name: str):
    """Get historical statistics for a specific god."""
    try:
        stat_name = request.args.get("stat", "win_rate")
        days = request.args.get("days", 30, type=int)
        return jsonify(db.get_god_stats_history(god_name, stat_name, days))
    except Exception as e:
        logger.error(f"Error fetching god stats: {e}")
        return jsonify({"error": str(e)}), 500


# SmiteSource endpoints
@app.route("/api/builds/<god_name>", methods=["GET"])
def get_god_build(god_name: str):
    """Get pro build for a specific god from SmiteSource."""
    try:
        build = smitesource_scraper.get_god_build(god_name)
        if not build:
            return jsonify({"error": "Build not found"}), 404
        return jsonify(build)
    except Exception as e:
        logger.error(f"Error fetching god build: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/builds/meta", methods=["GET"])
def get_meta_builds():
    """Get all current meta builds from SmiteSource."""
    try:
        return jsonify(smitesource_scraper.get_meta_builds())
    except Exception as e:
        logger.error(f"Error fetching meta builds: {e}")
        return jsonify({"error": str(e)}), 500


# SmiteBase endpoints
@app.route("/api/guides/<god_name>", methods=["GET"])
def get_god_guide(god_name: str):
    """Get community guide for a specific god from SmiteBase."""
    try:
        guide = smitebase_scraper.get_god_guide(god_name)
        if not guide:
            return jsonify({"error": "Guide not found"}), 404
        return jsonify(guide)
    except Exception as e:
        logger.error(f"Error fetching god guide: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/guides/top", methods=["GET"])
def get_top_guides():
    """Get top-rated community guides from SmiteBase."""
    try:
        limit = request.args.get("limit", 10, type=int)
        return jsonify(smitebase_scraper.get_top_guides(limit))
    except Exception as e:
        logger.error(f"Error fetching top guides: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/guides/new", methods=["GET"])
def get_new_guides():
    """Get recently added community guides from SmiteBase."""
    try:
        limit = request.args.get("limit", 10, type=int)
        return jsonify(smitebase_scraper.get_new_guides(limit))
    except Exception as e:
        logger.error(f"Error fetching new guides: {e}")
        return jsonify({"error": str(e)}), 500


# Build Optimization endpoints (temporarily disabled)
# @app.route("/api/builds/optimize", methods=["GET"])
# def optimize_build() -> Dict[str, str]:
#     """Get an optimized build for a god and role."""
#     try:
#         god_name = request.args.get("god")
#         role = request.args.get("role")
#         enemy_comp = request.args.getlist("enemies")

#         if not god_name or not role:
#             return jsonify({"error": "God name and role are required"}), 400

#         build = build_optimizer.get_optimal_build(god_name, role, enemy_comp)
#         return jsonify(
#             {
#                 "items": [item.name for _item in build.items],
#                 "total_cost": build.total_cost,
#                 "stats_summary": build.stats_summary,
#                 "win_rate": build.win_rate,
#                 "popularity": build.popularity,
#             }
#         )
#     except Exception as e:
#         logger.error(f"Error optimizing build: {e}")
#         return jsonify({"error": str(e)}), 500


# @app.route("/api/builds/analyze", methods=["POST"])
# def analyze_build() -> Dict[str, str]:
#     """Analyze a build and return performance metrics."""
#     try:
#         data = request.get_json()
#         if not data or "items" not in data or "god" not in data or "role" not in data:
#             return jsonify({"error": "Invalid request data"}), 400

#         # TODO: Convert request data to Build object
#         # This will require implementing item data loading
#         return jsonify({"error": "Not implemented yet"}), 501
#     except Exception as e:
#         logger.error(f"Error analyzing build: {e}")
#         return jsonify({"error": str(e)}), 500


# @app.route("/api/builds/successful", methods=["GET"])
# def get_successful_builds() -> List[Dict[str, str]]:
#     """Get successful builds for a god and role."""
#     try:
#         god_name = request.args.get("god")
#         role = request.args.get("role")
#         limit = request.args.get("limit", 10, type=int)

#         if not god_name or not role:
#             return jsonify({"error": "God name and role are required"}), 400

#         builds = build_optimizer.get_successful_builds(god_name, role, limit)
#         return jsonify(
#             [
#                 {
#                     "items": [item.name for _item in build.items],
#                     "total_cost": build.total_cost,
#                     "stats_summary": build.stats_summary,
#                     "win_rate": build.win_rate,
#                     "popularity": build.popularity,
#                 }
#                 for _build in builds
#             ]
#         )
#     except Exception as e:
#         logger.error(f"Error fetching successful builds: {e}")
#         return jsonify({"error": str(e)}), 500


# New Wiki Database endpoints
@app.route("/api/gods", methods=["GET"])
def get_all_gods():
    """Get all gods from the database."""
    try:
        gods = db.get_all_gods()
        return jsonify({"gods": gods, "count": len(gods)})
    except Exception as e:
        logger.error(f"Error fetching all gods: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/gods/<god_name>", methods=["GET"])
def get_god_details(god_name: str):
    """Get detailed information for a specific god."""
    try:
        god = db.get_god(god_name)
        if not god:
            return jsonify({"error": "God not found"}), 404
        return jsonify(god)
    except Exception as e:
        logger.error(f"Error fetching god details: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/items", methods=["GET"])
def get_all_items():
    """Get all items from the database."""
    try:
        items = db.get_all_items()
        return jsonify({"items": items, "count": len(items)})
    except Exception as e:
        logger.error(f"Error fetching all items: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/items/<item_name>", methods=["GET"])
def get_item_details(item_name: str):
    """Get detailed information for a specific item."""
    try:
        item = db.get_item(item_name)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item)
    except Exception as e:
        logger.error(f"Error fetching item details: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/sync", methods=["POST"])
def sync_wiki_data():
    """Sync data from Smite 2 Wiki to database."""
    try:
        # Scrape data from wiki
        logger.info("Starting wiki sync...")

        gods_data = wiki_scraper.get_all_gods()
        items_data = wiki_scraper.get_all_items()
        patches_data = wiki_scraper.get_patch_notes()

        # Import to database
        db.import_wiki_data(gods_data, items_data, patches_data)

        return jsonify(
            {
                "message": "Wiki sync completed successfully",
                "stats": {
                    "gods_imported": len(gods_data),
                    "items_imported": len(items_data),
                    "patches_imported": len(patches_data),
                },
            }
        )
    except Exception as e:
        logger.error(f"Error syncing wiki data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/search", methods=["GET"])
def search_wiki():
    """Search the Smite 2 Wiki."""
    try:
        query = request.args.get("q", "")
        limit = request.args.get("limit", 10, type=int)

        if not query:
            return jsonify({"error": "Search query is required"}), 400

        results = wiki_scraper.search_wiki(query, limit)
        return jsonify({"query": query, "results": results, "count": len(results)})
    except Exception as e:
        logger.error(f"Error searching wiki: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/dashboard", methods=["GET"])
def get_dashboard_data():
    """Get dashboard overview data."""
    try:
        gods_count = len(db.get_all_gods())
        items_count = len(db.get_all_items())
        patches_count = len(db.get_patches())

        # Get recent patches
        recent_patches = db.get_patches(limit=5)

        # Get gods by role (cleaned up for standard Smite 2 positions)
        all_gods = db.get_all_gods()
        gods_by_role = {}

        # Standard Smite 2 position mapping
        role_mapping = {
            "Solo": "Solo",
            "Mid": "Mid",
            "Carry": "Carry",
            "Support": "Support",
            "Jungle": "Jungle",
            # Clean up hybrid/messy roles
            "MidCarry": "Mid",
            "MidJungle": "Mid",
            "MidSolo": "Mid",
            "MidSupport": "Mid",
            "SoloJungle": "Solo",
            "SupportSolo": "Support",
            "CarrySolo": "Carry",
        }

        for _god in all_gods:
            raw_role = god.get("role", "Unknown")

            # Skip garbage data
            if "File:" in raw_role or ".png" in raw_role or len(raw_role) > 20:
                continue

            # Map to standard role
            clean_role = role_mapping.get(raw_role, raw_role)

            # Only count valid roles
            if clean_role in ["Solo", "Mid", "Carry", "Support", "Jungle"]:
                gods_by_role[clean_role] = gods_by_role.get(clean_role, 0) + 1

        return jsonify(
            {
                "overview": {
                    "gods_count": gods_count,
                    "items_count": items_count,
                    "patches_count": patches_count,
                },
                "recent_patches": recent_patches,
                "gods_by_role": gods_by_role,
            }
        )
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        return jsonify({"error": str(e)}), 500


# Build Optimization endpoints
@app.route("/api/optimize-build", methods=["POST"])
def optimize_build():
    """Optimize build for a specific god and role."""
    try:
        data = request.get_json()
        god = data.get("god")
        role = data.get("role")
        budget = data.get("budget", 15000)

        logger.info(f"Optimizing build for {god} ({role}) with budget {budget}g")

        # Get optimized build - try advanced first, fallback to simple
        build_result = None
        try:
            if not advanced_optimizer:
                logger.error("Advanced optimizer is not available.")
                raise RuntimeError("Advanced optimizer is not available.")
            build_result = advanced_optimizer.optimize_build(god, role, budget=budget)
            if build_result and "error" in build_result:
                build_result = None  # Force fallback
        except Exception as e:
            logger.warning(f"Advanced optimizer failed: {e}")
            build_result = None

        # Fallback to simple optimizer if available
        if not build_result:
            if build_optimizer:
                try:
                    logger.info(f"Falling back to simple optimizer for {god} ({role})")
                    if hasattr(build_optimizer, "get_optimal_build"):
                        build_result = build_optimizer.get_optimal_build(god, role)
                    else:
                        logger.error("Simple optimizer does not have 'get_optimal_build' method.")
                except Exception as e:
                    logger.warning(f"Simple optimizer also failed: {e}")
            else:
                logger.error("Simple optimizer is not available.")

        # Create a basic build structure if all optimizers fail
        if not build_result:
            logger.info(f"Creating basic build for {god} ({role})")

            # Role-specific Smite 2 items
            if role and role.lower() in ["jungle", "carry"]:
                items = [
                    "Hunter's Cowl",
                    "Devourer's Gauntlet",
                    "Wind Demon",
                    "The Executioner",
                    "Qin's Sais",
                    "Titan's Bane",
                ]
            elif role and role.lower() == "mid":
                items = [
                    "Vampiric Shroud",
                    "Book of Thoth",
                    "Shoes of the Magi",
                    "Obsidian Shard",
                    "Rod of Tahuti",
                    "Soul Reaver",
                ]
            elif role and role.lower() == "solo":
                items = [
                    "Warrior's Axe",
                    "Breastplate of Valor",
                    "Shoes of Focus",
                    "Mystical Mail",
                    "Spirit Robe",
                    "Mantle of Discord",
                ]
            elif role and role.lower() == "support":
                items = [
                    "Sentinel's Gift",
                    "Shoes of Focus",
                    "Sovereignty",
                    "Heartward Amulet",
                    "Spirit Robe",
                    "Mantle of Discord",
                ]
            else:
                items = [
                    "Hunter's Cowl",
                    "Devourer's Gauntlet",
                    "Wind Demon",
                    "The Executioner",
                    "Qin's Sais",
                    "Titan's Bane",
                ]

            build_result = {
                "items": items,
                "score": 75,
                "explanation": f"Basic {role} build for {god}. Advanced optimization unavailable - using fallback Smite 2 items.",
            }

        logger.info(f"Build optimization successful: {len(build_result.get('items', []))} items")
        return jsonify(
            {
                "success": True,
                "build": build_result,
                "god": god,
                "role": role,
                "mode": data.get("mode", "conquest"),
            }
        )

    except Exception as e:
        logger.error(f"Error in optimize_build: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/explain-build", methods=["POST"])
def explain_build():
    """Get detailed explanation for a build."""
    try:
        data = request.get_json()
        god = data.get("god")
        role = data.get("role")
        budget = data.get("budget", 15000)

        logger.info(f"Generating build explanation for {god} ({role})")

        # Get optimized build first
        if not advanced_optimizer:
            return jsonify({"success": False, "error": "Advanced optimizer not available"}), 500
        build_result = advanced_optimizer.optimize_build(god, role, budget)

        if not build_result:
            return (
                jsonify({"success": False, "error": "Could not generate build for explanation"}),
                400,
            )

        # Generate detailed explanation
        explanation = build_explainer.explain_complete_build(build_result)

        logger.info(f"Build explanation generated: {len(explanation)} characters")

        return jsonify({"success": True, "build": build_result, "explanation": explanation})

    except Exception as e:
        logger.error(f"Error in explain_build: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/meta-analysis", methods=["GET"])
def get_meta_analysis():
    """Get current meta analysis."""
    try:
        logger.info("Generating meta analysis report")

        # Generate meta insights
        meta_insights = patch_analyzer.analyze_meta_evolution()

        # Generate comprehensive report
        report = patch_analyzer.export_meta_report()
        logger.info(f"Meta analysis complete: {len(report)} characters")

        return jsonify({"success": True, "meta_insights": meta_insights, "report": report})

    except Exception as e:
        logger.error(f"Error in get_meta_analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/statistical-analysis", methods=["POST"])
def run_statistical_analysis():
    """Run statistical analysis with Monte Carlo simulation."""
    try:
        data = request.get_json()
        god = data.get("god")
        role = data.get("role")
        simulations = data.get("simulations", 100)

        logger.info(
            f"Running statistical analysis for {god} ({role}) with {simulations} simulations"
        )

        # Generate multiple build options
        if not advanced_optimizer:
            return jsonify({"success": False, "error": "Advanced optimizer not available"}), 500
        build1 = advanced_optimizer.optimize_build(god, role, budget=15000)
        build2 = advanced_optimizer.optimize_build(god, role, budget=13000)  # Budget variant
        build3 = advanced_optimizer.optimize_build(god, role, budget=12000)  # Early game variant
        builds = [build for _build in [build1, build2, build3] if build]
        if len(builds) < 2:
            return (
                jsonify(
                    {"success": False, "error": "Could not generate enough builds for comparison"}
                ),
                400,
            )
        # Run Monte Carlo analysis
        build_item_lists = [
            b["items"] for _b in builds if isinstance(b, dict) and isinstance(b.get("items"), list)
        ]
        enemy_comps = [[]]  # Placeholder: you can expand this to real enemy comps if available
        results = statistical_analyzer.monte_carlo_simulation(
            god, role, build_item_lists, enemy_comps, iterations=simulations
        )
        logger.info(
            f"Statistical analysis complete: {len(results) if isinstance(results, dict) else 'N/A'} results"
        )
        return jsonify({"success": True, "builds": builds, "analysis_results": results})

    except Exception as e:
        logger.error(f"Error in run_statistical_analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/calibration/start", methods=["POST"])
def start_calibration():
    """Start player calibration process."""
    if not player_integrator:
        return jsonify({"error": "Player integrator not available"}), 500

    try:
        data = request.get_json()
        player_name = data.get("player_name")
        preferred_role = data.get("preferred_role", "mid")

        if not player_name:
            return jsonify({"error": "Player name is required"}), 400

        # Start calibration
        result = player_integrator.start_calibration(player_name)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error starting calibration: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/calibration/match", methods=["POST"])
def add_calibration_match():
    """Add a calibration match."""
    if not player_integrator:
        return jsonify({"error": "Player integrator not available"}), 500

    try:
        data = request.get_json()
        player_name = data.get("player_name")
        match_data = data.get("match_data")

        if not player_name or not match_data:
            return jsonify({"error": "Player name and match data are required"}), 400

        result = player_integrator.add_calibration_match(player_name, match_data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error adding calibration match: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<player_name>/profile", methods=["GET"])
def get_player_profile(player_name: str):
    """Get player profile and performance data."""
    if not player_integrator:
        return jsonify({"error": "Player integrator not available"}), 500

    try:
        # No get_player_profile method; return personalized weights instead
        weights = player_integrator.get_personalized_weights(player_name)
        if not weights:
            return jsonify({"error": "Player profile not found"}), 404
        return jsonify(weights)
    except Exception as e:
        logger.error(f"Error getting player profile: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/optimize-build/enhanced", methods=["POST"])
def optimize_build_enhanced():
    """Enhanced build optimization with personalization and multi-mode support."""
    try:
        data = request.get_json()
        god = data.get("god")
        role = data.get("role", "mid")
        mode = data.get("mode", "conquest")
        player_name = data.get("player_name")

        if not god:
            return jsonify({"error": "God name is required"}), 400

        # Use multi-mode optimizer if available
        optimized_build = None
        if multi_mode_optimizer and advanced_optimizer:
            base_build = advanced_optimizer.optimize_build(god, role)
            if base_build:
                try:
                    optimized_build = multi_mode_optimizer.optimize_for_mode(
                        base_build, GameMode(mode)
                    )
                except Exception as e:
                    logger.warning(f"Multi-mode optimization failed: {e}")
                    optimized_build = base_build
        else:
            # Fallback to regular optimization
            optimized_build = (
                advanced_optimizer.optimize_build(god, role) if advanced_optimizer else None
            )

        if not optimized_build:
            return jsonify({"error": "Build optimization failed"}), 500

        # Get explanation
        explanation = None
        if build_explainer:
            try:
                explanation = build_explainer.explain_complete_build(optimized_build)
            except Exception as e:
                logger.warning(f"Failed to generate explanation: {e}")

        result = {
            "build": optimized_build,
            "god": god,
            "role": role,
            "mode": mode,
            "personalized": False,  # No player profile used
            "explanation": explanation,
        }

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in enhanced build optimization: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/optimize-build/realtime", methods=["POST"])
def optimize_build_realtime():
    """Real-time build optimization with enemy composition analysis."""
    try:
        data = request.get_json()
        god = data.get("god")
        role = data.get("role", "mid")
        enemy_gods = data.get("enemy_gods", [])
        detected_items = data.get("detected_items", {})
        budget = data.get("budget", 15000)
        playstyle = data.get("playstyle", "meta")

        if not god:
            return jsonify({"error": "God name is required"}), 400

        if not enhanced_optimizer:
            return jsonify({"error": "Enhanced optimizer not available"}), 500

        # Get real-time build recommendation
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
            "core_build": recommendation.core_build,
            "situational_items": recommendation.situational_items,
            "counter_items": recommendation.counter_items,
            "enemy_analysis": {
                "composition_type": recommendation.enemy_analysis.composition_type,
                "threat_level": recommendation.enemy_analysis.threat_level,
                "gods": recommendation.enemy_analysis.gods,
                "roles": recommendation.enemy_analysis.roles,
                "detected_items": recommendation.enemy_analysis.detected_items
            },
            "confidence_score": recommendation.confidence_score,
            "meta_compliance": recommendation.meta_compliance,
            "reasoning": recommendation.reasoning,
            "last_updated": recommendation.last_updated.isoformat()
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in real-time build optimization: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/analyze-enemy-composition", methods=["POST"])
def analyze_enemy_composition():
    """Analyze enemy composition for build optimization."""
    try:
        data = request.get_json()
        enemy_gods = data.get("enemy_gods", [])
        detected_items = data.get("detected_items", {})

        if not enemy_gods:
            return jsonify({"error": "Enemy gods list is required"}), 400

        if not enhanced_optimizer:
            return jsonify({"error": "Enhanced optimizer not available"}), 500

        # Analyze enemy composition
        composition = enhanced_optimizer.analyze_enemy_composition_real_time(
            enemy_gods=enemy_gods,
            detected_items=detected_items
        )

        result = {
            "success": True,
            "enemy_gods": composition.gods,
            "roles": composition.roles,
            "detected_items": composition.detected_items,
            "composition_type": composition.composition_type,
            "threat_level": composition.threat_level,
            "last_updated": composition.last_updated.isoformat(),
            "cache_duration": enhanced_optimizer.cache_duration
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error analyzing enemy composition: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/enhanced-dashboard", methods=["GET"])
def get_enhanced_dashboard():
    """Serve the enhanced dashboard."""
    return render_template("enhanced_dashboard.html")


@app.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "components": {
                "database": "connected",
                "advanced_optimizer": "ready" if advanced_optimizer else "unavailable",
                "statistical_analyzer": "ready" if statistical_analyzer else "unavailable",
                "patch_analyzer": "ready" if patch_analyzer else "unavailable",
                "build_explainer": "ready" if build_explainer else "unavailable",
                "enhanced_data_collector": "ready" if enhanced_data_collector else "unavailable",
                "player_integrator": "ready" if player_integrator else "unavailable",
                "multi_mode_optimizer": "ready" if multi_mode_optimizer else "unavailable",
            },
        }
    )


@app.route("/api/tracker/profile/<player_name>", methods=["GET"])
def get_tracker_profile(player_name: str):
    """Get player profile from Tracker.gg and integrate with calibration."""
    try:
        if not tracker_scraper:
            return jsonify({"error": "Tracker scraper not available"}), 500

        # Get player profile from Tracker.gg
        profile = tracker_scraper.get_player_profile(player_name)
        if not profile:
            return jsonify({"error": "Player not found on Tracker.gg"}), 404

        # Get recent matches for calibration
        recent_matches = tracker_scraper.get_recent_matches(player_name, limit=20)

        # Convert Tracker.gg data to calibration format
        calibration_matches = []
        for _match in recent_matches:
            calibration_match = {
                "god_name": match.get("god_name", "Unknown"),
                "role": match.get("role", "Unknown"),
                "win": match.get("result", "").upper() == "WIN",
                "kills": match.get("kills", 0),
                "deaths": match.get("deaths", 0),
                "assists": match.get("assists", 0),
                "damage_dealt": match.get("damage_dealt", 0),
                "damage_mitigated": match.get("damage_mitigated", 0),
                "gold_earned": match.get("gold_earned", 0),
                "match_duration": match.get("match_duration", 0),
                "game_mode": match.get("game_mode", "conquest"),
                "timestamp": match.get("timestamp", "")
            }
            calibration_matches.append(calibration_match)

        # Start calibration if player doesn't exist
        if player_integrator:
            calibration_result = player_integrator.start_calibration(player_name)

            # Add all matches to calibration
            for _match in calibration_matches:
                player_integrator.add_calibration_match(player_name, match)

        return jsonify({
            "player_name": player_name,
            "tracker_profile": profile,
            "recent_matches": recent_matches,
            "calibration_matches": calibration_matches,
            "calibration_status": calibration_result if player_integrator else "unavailable"
        })

    except Exception as e:
        logger.error(f"Error fetching Tracker.gg profile for {player_name}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/tracker/calibration/<player_name>", methods=["POST"])
def auto_calibration_from_tracker(player_name: str):
    """Automatically calibrate player using Tracker.gg data."""
    try:
        if not tracker_scraper or not player_integrator:
            return jsonify({"error": "Required components not available"}), 500

        # Get player profile and matches
        profile = tracker_scraper.get_player_profile(player_name)
        if not profile:
            return jsonify({"error": "Player not found on Tracker.gg"}), 404

        recent_matches = tracker_scraper.get_recent_matches(player_name, limit=50)

        if len(recent_matches) < 5:
            return jsonify({
                "error": "Not enough matches found",
                "matches_found": len(recent_matches),
                "required": 5
            }), 400

        # Start calibration
        calibration_result = player_integrator.start_calibration(player_name)

        # Add matches to calibration
        added_matches = 0
        for _match in recent_matches:
            try:
                calibration_match = {
                    "god_name": match.get("god_name", "Unknown"),
                    "role": match.get("role", "Unknown"),
                    "win": match.get("result", "").upper() == "WIN",
                    "kills": match.get("kills", 0),
                    "deaths": match.get("deaths", 0),
                    "assists": match.get("assists", 0),
                    "damage_dealt": match.get("damage_dealt", 0),
                    "damage_mitigated": match.get("damage_mitigated", 0),
                    "gold_earned": match.get("gold_earned", 0),
                    "match_duration": match.get("match_duration", 0),
                    "game_mode": match.get("game_mode", "conquest"),
                    "timestamp": match.get("timestamp", "")
                }

                result = player_integrator.add_calibration_match(player_name, calibration_match)
                added_matches += 1

                # Check if calibration is complete
                if result.get("status") == "calibration_completed":
                    break

            except Exception as e:
                logger.warning(f"Error adding match {match.get('match_id', 'unknown')}: {e}")
                continue

        # Get final calibration result
        final_result = player_integrator.get_personalized_weights(player_name)

        return jsonify({
            "player_name": player_name,
            "calibration_status": "completed" if added_matches >= 5 else "in_progress",
            "matches_processed": added_matches,
            "total_matches_found": len(recent_matches),
            "personalized_weights": final_result,
            "tracker_profile": profile
        })

    except Exception as e:
        logger.error(f"Error in auto calibration for {player_name}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/tracker/search", methods=["GET"])
def search_tracker_players():
    """Search for players on Tracker.gg."""
    try:
        query = request.args.get("q", "")
        limit = request.args.get("limit", 10, type=int)

        if not query:
            return jsonify({"error": "Search query required"}), 400

        if not tracker_scraper:
            return jsonify({"error": "Tracker scraper not available"}), 500

        results = tracker_scraper.search_players(query, limit)

        return jsonify({
            "query": query,
            "results": results,
            "total_found": len(results)
        })

    except Exception as e:
        logger.error(f"Error searching Tracker.gg for '{query}': {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/tracker/leaderboard", methods=["GET"])
def get_tracker_leaderboard():
    """Get leaderboard data from Tracker.gg."""
    try:
        category = request.args.get("category", "kills")
        platform = request.args.get("platform", "pc")

        if not tracker_scraper:
            return jsonify({"error": "Tracker scraper not available"}), 500

        leaderboard = tracker_scraper.get_leaderboard(category, platform)

        return jsonify({
            "category": category,
            "platform": platform,
            "leaderboard": leaderboard,
            "total_entries": len(leaderboard)
        })

    except Exception as e:
        logger.error(f"Error fetching Tracker.gg leaderboard: {e}")
        return jsonify({"error": str(e)}), 500


def setup_logging():
    """Set up logging configuration."""
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("divine_arsenal.log")],
    )


if __name__ == "__main__":
    setup_logging()
    logger.info("🚀 Starting Enhanced SMITE 2 Divine Arsenal Server")

    # Get port from environment variable or default to 5000
    port = int(os.environ.get("FLASK_PORT", 5000))

    try:
        logger.info("✅ Application initialization complete")

        # Initialize real-time builds manager if components are available
        if enhanced_optimizer and user_auth:
            try:
                from realtime_builds import RealtimeBuildsManager
                realtime_manager = RealtimeBuildsManager(socketio, enhanced_optimizer, user_auth)
                logger.info("✅ Real-time builds manager initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Real-time builds manager not available: {e}")

        # Run the Flask application with SocketIO
        socketio.run(app, host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        raise
