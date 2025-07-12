#!/usr/bin/env python3
"""
Hybrid launcher for SMITE 2 Divine Arsenal - Full features, No WebDriver spam
"""

import os
import sys

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'divine_arsenal', 'backend')
sys.path.insert(0, backend_path)

from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from database import Database
from user_auth import UserAuth

app = Flask(__name__, template_folder='divine_arsenal/backend/templates')
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize database and auth (no scrapers)
db = Database()
user_auth = UserAuth()

print("✅ Database initialized")
print("✅ User authentication initialized")

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

@app.route("/login")
def login_page():
    """Login page."""
    return render_template("login.html")

@app.route("/api/login", methods=["POST"])
def login():
    """Handle login requests."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"success": False, "error": "Username and password required"}), 400
            
        # Authenticate user
        result = user_auth.authenticate_with_credentials(username, password)
        if result and result.get('success'):
            user = result.get('user')
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            return jsonify({"success": True, "message": "Login successful"})
        else:
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/register", methods=["POST"])
def register():
    """Handle registration requests."""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email', '')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"success": False, "error": "Username and password required"}), 400
            
        # Register user
        result = user_auth.register_user(username, email, password)
        if result['success']:
            return jsonify({"success": True, "message": "Registration successful"})
        else:
            return jsonify({"success": False, "error": result.get('error', 'Registration failed')}), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/logout", methods=["POST"])
def logout():
    """Handle logout requests."""
    session.clear()
    return jsonify({"success": True, "message": "Logout successful"})

# Add auth endpoints for frontend compatibility
@app.route("/auth/login", methods=["POST"])
def auth_login():
    """Handle login requests (frontend compatibility)."""
    return login()

@app.route("/auth/register", methods=["POST"])
def auth_register():
    """Handle registration requests (frontend compatibility)."""
    return register()

@app.route("/api/gods", methods=["GET"])
def get_all_gods():
    """Get all gods from database."""
    try:
        gods = db.get_all_gods()
        return jsonify({"success": True, "data": gods})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/items", methods=["GET"])
def get_all_items():
    """Get all items from database."""
    try:
        items = db.get_all_items()
        return jsonify({"success": True, "data": items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard_data():
    """Get dashboard statistics."""
    try:
        gods = db.get_all_gods()
        items = db.get_all_items()
        
        stats = {
            "gods_count": len(gods),
            "items_count": len(items),
            "builds_analyzed": 1247,  # Mock data
            "meta_insights": [
                "OB12 Meta: Tanks favored (Spectral Armor buff)",
                "Anti-heal crucial (Contagion)",
                "Early ganks dominant (lane XP changes)"
            ]
        }
        
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/user", methods=["GET"])
def get_current_user():
    """Get current user info."""
    if 'user_id' in session:
        return jsonify({
            "success": True,
            "data": {
                "user_id": session['user_id'],
                "username": session['username'],
                "logged_in": True
            }
        })
    else:
        return jsonify({
            "success": True,
            "data": {
                "logged_in": False
            }
        })

@app.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "SMITE 2 Divine Arsenal",
        "version": "1.0.0",
        "features": ["authentication", "database", "no_webdriver"]
    })

if __name__ == "__main__":
    print("🚀 Starting SMITE 2 Divine Arsenal Hybrid Server")
    print("✅ Full authentication system enabled")
    print("✅ No WebDriver components loaded")
    print("✅ Server accessible at: http://localhost:5000")
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,  # Disable debug mode to prevent auto-reloading
        use_reloader=False  # Prevent multiple instances
    ) 