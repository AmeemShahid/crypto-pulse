from flask import Flask, jsonify
import threading
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    """Home endpoint for keepalive"""
    return jsonify({
        "status": "alive",
        "service": "crypto-bot",
        "message": "Bot is running successfully!"
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "crypto-bot-keepalive"
    })

@app.route('/ping')
def ping():
    """Simple ping endpoint for UptimeRobot"""
    return "pong"

def keep_alive():
    """Start the Flask server for keepalive"""
    try:
        port = int(os.getenv('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start keepalive server: {e}")

if __name__ == "__main__":
    keep_alive()
