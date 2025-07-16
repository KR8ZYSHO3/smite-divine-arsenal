#!/usr/bin/env python3
"""
Minimal Flask app for testing Render deployment
"""

import os
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    """Home page."""
    return jsonify({
        'message': 'SMITE 2 Divine Arsenal - Minimal Test App',
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': 'minimal-test'
    })

@app.route('/api/test')
def api_test():
    """Test API endpoint."""
    return jsonify({
        'message': 'API is working',
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'database_url_present': 'DATABASE_URL' in os.environ
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 