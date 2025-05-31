from flask import Flask, jsonify, request, send_from_directory, Response
from flasgger import Swagger
import random
import time
import os
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
Swagger(app)

# Path to local jokes file
JOKES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jokes.txt')

# Path to home.html
HOME_HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'home.html')

@app.route('/')
def index():
    """Serve the React frontend"""
    with open(HOME_HTML_PATH, 'r') as f:
        return Response(f.read(), mimetype='text/html')

# Path to SQLite database
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jokes.db')

def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS joke_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_ip TEXT NOT NULL,
            timestamp REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_joke_request(user_ip):
    """Add a joke request to the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO joke_requests (user_ip, timestamp) VALUES (?, ?)', 
                   (user_ip, time.time()))
    conn.commit()
    conn.close()

def get_requests_count_24h(user_ip):
    """Get count of requests for user in past 24 hours"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    twenty_four_hours_ago = time.time() - (24 * 60 * 60)
    cursor.execute('SELECT COUNT(*) FROM joke_requests WHERE user_ip = ? AND timestamp > ?', 
                   (user_ip, twenty_four_hours_ago))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_user_timestamps(user_ip):
    """Get all timestamps for a user in past 24 hours"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    twenty_four_hours_ago = time.time() - (24 * 60 * 60)
    cursor.execute('SELECT timestamp FROM joke_requests WHERE user_ip = ? AND timestamp > ? ORDER BY timestamp', 
                   (user_ip, twenty_four_hours_ago))
    timestamps = [row[0] for row in cursor.fetchall()]
    conn.close()
    return timestamps

def clean_old_requests():
    """Remove requests older than 24 hours from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    twenty_four_hours_ago = time.time() - (24 * 60 * 60)
    cursor.execute('DELETE FROM joke_requests WHERE timestamp <= ?', (twenty_four_hours_ago,))
    conn.commit()
    conn.close()

@app.route('/health')
def health_check():
    """
    Health check endpoint for deployment monitoring
    ---
    responses:
      200:
        description: API is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [healthy]
            database:
              type: string
            jokes_loaded:
              type: integer
            total_requests:
              type: integer
            timestamp:
              type: string
      500:
        description: API is unhealthy
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [unhealthy]
            error:
              type: string
            timestamp:
              type: string
    """
    try:
        # Test database connection
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM joke_requests')
        count = cursor.fetchone()[0]
        conn.close()
        
        # Test jokes file loading
        with open(JOKES_FILE, 'r') as f:
            jokes = [line.strip() for line in f.readlines() if line.strip()]
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'jokes_loaded': len(jokes),
            'total_requests': count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/get-joke')
def get_joke():
    """
    Get a random joke
    ---
    responses:
      200:
        description: A random joke and the number of requests made today by the user.
        schema:
          type: object
          properties:
            joke:
              type: string
              description: The random joke.
            requests_today:
              type: integer
              description: The number of jokes requested by the user today.
      500:
        description: Error fetching joke.
    """
    try:
        # Get user IP
        user_ip = request.remote_addr
        
        # Clean old requests and add current request
        clean_old_requests()
        add_joke_request(user_ip)
        
        # Fetch joke from local file
        with open(JOKES_FILE, 'r') as f:
            jokes = [line.strip() for line in f.readlines() if line.strip()]
        
        if not jokes:
            return "No jokes available", 404
            
        random_joke = random.choice(jokes)
        requests_count = get_requests_count_24h(user_ip)
        
        return jsonify({
            "joke": random_joke,
            "requests_today": requests_count
        })
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/joke-stats')
def joke_stats():
    """
    Endpoint to see how many jokes user has requested in past 24 hours
    ---
    responses:
      200:
        description: Statistics about joke requests in the last 24 hours.
        schema:
          type: object
          properties:
            user_ip:
              type: string
              description: The IP address of the user.
            jokes_requested_24h:
              type: integer
              description: The number of jokes requested by the user in the last 24 hours.
            timestamps:
              type: array
              items:
                type: number
              description: A list of timestamps for each joke request in the last 24 hours.
      500:
        description: Error fetching joke statistics.
    """
    try:
        user_ip = request.remote_addr
        clean_old_requests()
        
        requests_count = get_requests_count_24h(user_ip)
        timestamps = get_user_timestamps(user_ip)
        
        return jsonify({
            "user_ip": user_ip,
            "jokes_requested_24h": requests_count,
            "timestamps": timestamps
        })
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    app.run(host='0.0.0.0', port=51362)