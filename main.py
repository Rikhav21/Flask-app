import flask
import sqlite3
import os
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

app = flask.Flask(
    __name__,
    static_folder="static",
    static_url_path="/"
)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day"],
    storage_uri="memory://",
)

def init_db():
    """Initialize database on first access"""
    conn = sqlite3.connect('gifts.db') 
    cursor = conn.cursor()  
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gift TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()  
    conn.close()

# Initialize DB when app starts
with app.app_context():
    init_db()

@app.get("/")
@limiter.exempt
def index():
    return flask.send_from_directory("static", "index.html")

@app.post("/gifts")
def create_gift():
    data = flask.request.get_json()
    password = data.get('password')
    
    # Check if password is correct
    correct_password = os.getenv('GIFT_PASSWORD')
    if password != correct_password:
        return {'error': 'Invalid password'}, 401
    
    name = data.get('name')
    gift = data.get('gift')
    
    conn = sqlite3.connect('gifts.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO gifts (name, gift) VALUES (?, ?)', (name, gift))
    conn.commit()
    conn.close()

    return '', 201
    
@app.get("/gifts")
def get_gifts():
    conn = sqlite3.connect('gifts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, gift, completed FROM gifts')
    rows = cursor.fetchall()
    conn.close()
    
    gifts = [{'id': row[0], 'name': row[1], 'gift': row[2], 'completed': row[3]} for row in rows]
    return flask.jsonify(gifts)

@app.patch("/gifts/<int:gift_id>")
def complete_gift(gift_id):
    data = flask.request.get_json()
    password = data.get('password')
    
    correct_password = os.getenv('GIFT_PASSWORD')
    if password != correct_password:
        return {'error': 'Invalid password'}, 401
    
    conn = sqlite3.connect('gifts.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE gifts SET completed = 1 WHERE id = ?', (gift_id,))
    conn.commit()
    conn.close()
    
    return '', 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
