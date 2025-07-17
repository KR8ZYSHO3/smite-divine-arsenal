from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        'message': 'SMITE Divine Arsenal is running!',
        'status': 'success'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'All systems operational'
    })

@app.route('/api/gods')
def get_gods():
    return jsonify({
        'gods': [
            {'name': 'Zeus', 'role': 'Mage'},
            {'name': 'Odin', 'role': 'Warrior'},
            {'name': 'Thor', 'role': 'Assassin'}
        ],
        'count': 3
    })

@app.route('/api/items')
def get_items():
    return jsonify({
        'items': [
            {'name': 'Bluestone Pendant', 'type': 'Starter'},
            {'name': 'Warrior\'s Axe', 'type': 'Starter'},
            {'name': 'Hastened Katana', 'type': 'Attack Speed'}
        ],
        'count': 3
    })

@app.route('/api/build-optimizer')
def build_optimizer():
    return jsonify({
        'status': 'available',
        'message': 'Build optimizer is ready'
    })

@app.route('/api/community/builds')
def community_builds():
    return jsonify({
        'builds': [],
        'count': 0
    })

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'total_gods': 3,
        'total_items': 3
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 