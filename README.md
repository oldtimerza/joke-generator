# Joke Generator

A Flask web application with a React frontend that serves random jokes from a local file and tracks usage statistics using SQLite.

## Features

- **Random Joke API**: Get random jokes from a curated collection of 30 classic jokes
- **Usage Tracking**: SQLite database tracks joke requests with timestamps and IP addresses
- **Statistics Endpoint**: View joke request statistics for the last 24 hours
- **React Frontend**: Interactive web interface with a "Request Joke" button
- **Real-time Counter**: Shows total jokes requested today

## Project Structure

```
.
├── app.py              # Flask application with API endpoints
├── jokes.txt           # Collection of 30 jokes
├── hello.sh            # Simple bash script that prints "hello world!"
├── jokes.db            # SQLite database (created automatically)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## API Endpoints

### `GET /`
Serves the React frontend interface

### `GET /get-joke`
Returns a random joke from the jokes.txt file
```json
{
  "joke": "Why did the cookie go to the doctor? Because it felt crumbly!"
}
```

### `GET /joke-stats`
Returns statistics about joke requests in the last 24 hours
```json
{
  "jokes_requested_24h": 5,
  "timestamps": [1748692200.35, 1748692207.99, ...],
  "user_ip": "127.0.0.1"
}
```

## Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install flask
   ```

2. **Run the Application**
   ```bash
   python3 app.py
   ```

3. **Access the Application**
   - Frontend: http://localhost:5000
   - API: http://localhost:5000/get-joke

## Usage

### Web Interface
1. Open http://localhost:5000 in your browser
2. Click the "Request Joke" button to get a random joke
3. The counter shows how many jokes have been requested today

### API Usage
```bash
# Get a random joke
curl http://localhost:5000/get-joke

# Get usage statistics
curl http://localhost:5000/joke-stats
```

### Bash Script
```bash
# Make executable and run
chmod +x hello.sh
./hello.sh
```

## Database Schema

The SQLite database (`jokes.db`) contains a single table:

```sql
CREATE TABLE joke_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_ip TEXT NOT NULL,
    timestamp REAL NOT NULL
);
```

## Technical Details

- **Backend**: Flask (Python)
- **Frontend**: React 18 with Babel for JSX transformation
- **Database**: SQLite3
- **Styling**: CSS with modern design and responsive layout
- **Error Handling**: Comprehensive error handling for API requests and database operations

## Development

The application automatically:
- Creates the SQLite database and table on first run
- Loads jokes from the local `jokes.txt` file
- Tracks all joke requests with IP addresses and timestamps
- Serves a fully functional React frontend

## Features Implemented

✅ Flask application with /get-joke endpoint  
✅ Local jokes.txt file with 30 jokes  
✅ SQLite database for request tracking  
✅ React frontend with "Request Joke" button  
✅ Real-time statistics and counter  
✅ Error handling and loading states  
✅ Responsive design  
✅ Bash script (hello.sh)  

## License

This project is open source and available under the MIT License.