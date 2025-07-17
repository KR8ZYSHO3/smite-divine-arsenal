#!/usr/bin/env python3
"""
Simple Flask app for testing deployment
This will definitely work on Render
"""

from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    """Home page."""
    return jsonify({
        'message': 'SMITE 2 Divine Arsenal - Simple Test',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'version': 'simple-test'
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': 'simple-test',
        'database': 'not_configured'
    })

@app.route('/api/gods')
def get_gods():
    """Mock gods endpoint."""
    return jsonify({
        'gods': [
            {'name': 'Zeus', 'role': 'Mage'},
            {'name': 'Odin', 'role': 'Warrior'},
            {'name': 'Thor', 'role': 'Assassin'}
        ],
        'count': 3,
        'message': 'Mock data - full backend not loaded'
    })

@app.route('/api/items')
def get_items():
    """Mock items endpoint."""
    return jsonify({
        'items': [
            {'name': 'Bluestone Pendant', 'type': 'Starter'},
            {'name': 'Warrior\'s Axe', 'type': 'Starter'},
            {'name': 'Hastened Katana', 'type': 'Attack Speed'}
        ],
        'count': 3,
        'message': 'Mock data - full backend not loaded'
    })

@app.route('/api/build-optimizer')
def build_optimizer():
    """Mock build optimizer endpoint."""
    return jsonify({
        'status': 'available',
        'message': 'Mock build optimizer - full backend not loaded'
    })

@app.route('/api/community/builds')
def community_builds():
    """Mock community builds endpoint."""
    return jsonify({
        'builds': [],
        'count': 0,
        'message': 'Mock community builds - full backend not loaded'
    })

@app.route('/api/stats')
def get_stats():
    """Mock stats endpoint."""
    return jsonify({
        'total_gods': 3,
        'total_items': 3,
        'message': 'Mock statistics - full backend not loaded'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Simple Divine Arsenal Test Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 