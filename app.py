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
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 24px;
            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
            min-height: 100vh;
            color: #374151;
        }
        .container {
            background-color: #f9fafb;
            padding: 48px;
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            border: 1px solid #e5e7eb;
        }
        h1 {
            text-align: center;
            color: #1f2937;
            margin-bottom: 40px;
            font-size: 3rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }
        .joke-form {
            text-align: center;
            margin-bottom: 40px;
        }
        .joke-button {
            background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
            color: #ffffff;
            padding: 18px 36px;
            font-size: 1.1rem;
            font-weight: 700;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            box-shadow: 0 4px 14px 0 rgba(236, 72, 153, 0.3);
        }
        .joke-button:hover {
            background: linear-gradient(135deg, #be185d 0%, #9d174d 100%);
            transform: translateY(-1px);
            box-shadow: 0 6px 20px 0 rgba(236, 72, 153, 0.4);
        }
        .joke-button:active {
            transform: translateY(0);
            box-shadow: 0 2px 8px 0 rgba(236, 72, 153, 0.3);
        }
        .joke-button:disabled {
            background: #9ca3af;
            cursor: not-allowed;
            transform: none;
            box-shadow: 0 4px 14px 0 rgba(156, 163, 175, 0.2);
        }
        .joke-box {
            background-color: #ffffff;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 32px;
            margin-top: 32px;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .joke-text {
            font-size: 1.25rem;
            line-height: 1.7;
            color: #374151;
            font-weight: 500;
            font-style: italic;
        }
        .loading {
            color: #6b7280;
            font-style: italic;
            font-weight: 500;
        }
        .error {
            color: #dc2626;
            background: #fef2f2;
            border: 2px solid #fecaca;
            border-radius: 12px;
            padding: 20px;
            margin: 24px 0;
            font-weight: 600;
        }
        .stats {
            margin-top: 32px;
            text-align: center;
            color: #6b7280;
            font-size: 1.1rem;
            font-weight: 600;
            background: #f3f4f6;
            padding: 24px;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
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
                    <h1>🦄 Joke Generator</h1>
                    
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