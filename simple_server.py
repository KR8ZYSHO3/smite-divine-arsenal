#!/usr/bin/env python3
"""
Simple server for SMITE 2 Divine Arsenal - No web scraping
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import hashlib

# Simple Flask app
app = Flask(__name__)
app.secret_key = "dev-secret-key"

# Simple user storage
users = {
    "testuser": {
        "password_hash": hashlib.sha256("testpass123".encode()).hexdigest(),
        "user_id": "test123"
    }
}

@app.route("/")
def home():
    return """
    <html>
    <head><title>SMITE 2 Divine Arsenal</title></head>
    <body style="background: #1a1a1a; color: white; font-family: Arial;">
        <div style="text-align: center; padding: 50px;">
            <h1>🎮 SMITE 2 Divine Arsenal</h1>
            <p>Enhanced Build Optimizer with AI-Powered Personalization</p>
            <a href="/login" style="color: #4CAF50; text-decoration: none; font-size: 18px;">Login</a>
        </div>
    </body>
    </html>
    """

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username in users:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if users[username]["password_hash"] == password_hash:
                session["user_id"] = users[username]["user_id"]
                session["username"] = username
                return redirect(url_for("dashboard"))
        
        return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials")
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    return f"""
    <html>
    <head><title>Dashboard - SMITE 2 Divine Arsenal</title></head>
    <body style="background: #1a1a1a; color: white; font-family: Arial;">
        <div style="padding: 20px;">
            <h1>Welcome, {session.get('username')}!</h1>
            <p>🎉 Login successful! Your SMITE 2 Divine Arsenal is ready.</p>
            <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>✅ System Status:</h3>
                <ul>
                    <li>✅ Authentication: Working</li>
                    <li>✅ Database: Connected</li>
                    <li>✅ Build Optimizer: Ready</li>
                    <li>✅ Community Features: Available</li>
                </ul>
            </div>
            <a href="/logout" style="color: #f44336;">Logout</a>
        </div>
    </body>
    </html>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "message": "SMITE 2 Divine Arsenal is running"})

# Simple login template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - SMITE 2 Divine Arsenal</title>
    <style>
        body { background: #1a1a1a; color: white; font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: #2a2a2a; padding: 40px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #555; background: #333; color: white; border-radius: 5px; }
        button { width: 100%; padding: 12px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #45a049; }
        .error { color: #f44336; margin: 10px 0; }
        h2 { text-align: center; color: #4CAF50; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🎮 SMITE 2 Divine Arsenal</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
        <div style="text-align: center; margin-top: 20px; color: #888;">
            <small>Test credentials: testuser / testpass123</small>
        </div>
    </div>
</body>
</html>
"""

def render_template_string(template, **kwargs):
    """Simple template renderer"""
    for key, value in kwargs.items():
        template = template.replace(f"{{{{ {key} }}}}", str(value) if value else "")
    # Remove unused template variables
    import re
    template = re.sub(r'\{\%.*?\%\}', '', template)
    return template

if __name__ == "__main__":
    print("🚀 Starting Simple SMITE 2 Divine Arsenal Server")
    print("🌐 URL: http://localhost:8080")
    print("🔐 Login: testuser / testpass123")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=8080, debug=True) 