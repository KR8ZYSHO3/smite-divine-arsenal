#!/usr/bin/env python3
"""
Simple launcher for SMITE 2 Divine Arsenal - No WebDriver spam
"""

import os
import sys

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'divine_arsenal', 'backend')
sys.path.insert(0, backend_path)

from flask import Flask, jsonify, render_template, request, redirect, url_for, session

# Import database
try:
    from database import Database
    print("✅ Database module imported successfully")
except ImportError as e:
    print(f"❌ Database import error: {e}")
    print(f"Backend path: {backend_path}")
    sys.exit(1)

app = Flask(__name__, template_folder='divine_arsenal/backend/templates')
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize only the database
db = Database()

print("✅ Database initialized")

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

@app.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "SMITE 2 Divine Arsenal",
        "version": "1.0.0"
    })

if __name__ == "__main__":
    print("🚀 Starting Simple SMITE 2 Divine Arsenal Server (No WebDriver)")
    print("✅ Server accessible at: http://localhost:5000")
    print("✅ No scrapers initialized - clean startup!")
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False  # Prevent multiple instances
    ) 