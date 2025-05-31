from flask import Flask, jsonify, request, send_from_directory, Response
import random
import time
import os
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# HTML template for the React frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Joke Generator</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .joke-form {
            text-align: center;
            margin-bottom: 30px;
        }
        .joke-button {
            background-color: #4CAF50;
            color: white;
            padding: 15px 30px;
            font-size: 18px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .joke-button:hover {
            background-color: #45a049;
        }
        .joke-button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        .joke-box {
            background-color: #f9f9f9;
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        .joke-text {
            font-size: 16px;
            line-height: 1.5;
            color: #333;
        }
        .loading {
            color: #666;
            font-style: italic;
        }
        .error {
            color: #d32f2f;
        }
        .stats {
            margin-top: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        function JokeGenerator() {
            const [joke, setJoke] = useState('');
            const [loading, setLoading] = useState(false);
            const [error, setError] = useState('');
            const [requestsToday, setRequestsToday] = useState(0);

            const fetchJoke = async () => {
                setLoading(true);
                setError('');
                
                try {
                    const response = await fetch('/get-joke');
                    if (!response.ok) {
                        throw new Error('Failed to fetch joke');
                    }
                    const data = await response.json();
                    setJoke(data.joke);
                    setRequestsToday(data.requests_today);
                } catch (err) {
                    setError('Failed to load joke. Please try again.');
                    console.error('Error fetching joke:', err);
                } finally {
                    setLoading(false);
                }
            };

            return (
                <div className="container">
                    <h1>🎭 Joke Generator</h1>
                    
                    <div className="joke-form">
                        <button 
                            className="joke-button" 
                            onClick={fetchJoke}
                            disabled={loading}
                        >
                            {loading ? 'Loading...' : 'Request Joke'}
                        </button>
                    </div>

                    <div className="joke-box">
                        {loading && (
                            <div className="joke-text loading">
                                Getting a fresh joke for you...
                            </div>
                        )}
                        {error && (
                            <div className="joke-text error">
                                {error}
                            </div>
                        )}
                        {!loading && !error && joke && (
                            <div className="joke-text">
                                {joke}
                            </div>
                        )}
                        {!loading && !error && !joke && (
                            <div className="joke-text" style={{color: '#999'}}>
                                Click the button above to get a joke!
                            </div>
                        )}
                    </div>

                    {requestsToday > 0 && (
                        <div className="stats">
                            Jokes requested today: {requestsToday}
                        </div>
                    )}
                </div>
            );
        }

        ReactDOM.render(<JokeGenerator />, document.getElementById('root'));
    </script>
</body>
</html>
"""

# Path to local jokes file
JOKES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jokes.txt')

@app.route('/')
def index():
    """Serve the React frontend"""
    return Response(HTML_TEMPLATE, mimetype='text/html')

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

@app.route('/get-joke')
def get_joke():
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
    """Endpoint to see how many jokes user has requested in past 24 hours"""
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
    app.run(host='0.0.0.0', port=5000)