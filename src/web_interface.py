from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from ai_enhanced_bot import AICustomerServiceBot
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import logging
import asyncio
from typing import Dict, Optional
import sqlite3
from functools import wraps
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chat_logs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize bot
try:
    with open('company_config.json', 'r') as f:
        company_data = json.load(f)
    bot = AICustomerServiceBot(company_data)
except Exception as e:
    logger.error(f"Error initializing bot: {str(e)}")
    company_data = {}
    bot = None

# Database setup
def init_db():
    with sqlite3.connect('chat.db') as conn:
        c = conn.cursor()
        # Create users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT,
                    is_admin BOOLEAN, created_at TIMESTAMP)''')
        # Create chat history table
        c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                    (id INTEGER PRIMARY KEY, user_id TEXT, message TEXT,
                    response TEXT, timestamp TIMESTAMP, satisfaction INTEGER)''')
        # Create analytics table
        c.execute('''CREATE TABLE IF NOT EXISTS analytics
                    (id INTEGER PRIMARY KEY, event_type TEXT, data TEXT,
                    timestamp TIMESTAMP)''')
        conn.commit()

init_db()

# User Model
class User(UserMixin):
    def __init__(self, id, username, is_admin=False):
        self.id = id
        self.username = username
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect('chat.db') as conn:
        c = conn.cursor()
        user = c.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user:
            return User(user[0], user[1], user[3])
    return None

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        with sqlite3.connect('chat.db') as conn:
            c = conn.cursor()
            user = c.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                           (username, password)).fetchone()
            if user:
                login_user(User(user[0], user[1], user[3]))
                return redirect(url_for('dashboard' if user[3] else 'chat'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=current_user)

@app.route('/dashboard')
@admin_required
def dashboard():
    # Get analytics data
    with sqlite3.connect('chat.db') as conn:
        c = conn.cursor()
        chat_count = c.execute('SELECT COUNT(*) FROM chat_history').fetchone()[0]
        user_count = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        satisfaction = c.execute('''SELECT AVG(satisfaction) FROM chat_history 
                                  WHERE satisfaction IS NOT NULL''').fetchone()[0]
        recent_chats = c.execute('''SELECT * FROM chat_history 
                                  ORDER BY timestamp DESC LIMIT 10''').fetchall()
    
    return render_template('dashboard.html',
                         chat_count=chat_count,
                         user_count=user_count,
                         satisfaction=satisfaction,
                         recent_chats=recent_chats)

@app.route('/analytics')
@admin_required
def analytics():
    with sqlite3.connect('chat.db') as conn:
        c = conn.cursor()
        # Get various analytics data
        daily_chats = c.execute('''SELECT DATE(timestamp), COUNT(*) 
                                 FROM chat_history 
                                 GROUP BY DATE(timestamp)''').fetchall()
        satisfaction_dist = c.execute('''SELECT satisfaction, COUNT(*) 
                                       FROM chat_history 
                                       GROUP BY satisfaction''').fetchall()
        common_queries = c.execute('''SELECT message, COUNT(*) 
                                    FROM chat_history 
                                    GROUP BY message 
                                    ORDER BY COUNT(*) DESC 
                                    LIMIT 10''').fetchall()
    
    return render_template('analytics.html',
                         daily_chats=daily_chats,
                         satisfaction_dist=satisfaction_dist,
                         common_queries=common_queries)

# API Routes
@app.route('/api/chat', methods=['POST'])
async def chat_api():
    try:
        data = request.json
        user_id = current_user.id if current_user.is_authenticated else 'anonymous'
        
        # Log incoming message
        logger.info(f"Incoming message from {user_id}: {data['message']}")
        
        # Generate response
        response = await bot.handle_complex_query(
            data['message'],
            user_id,
            data.get('context')
        )
        
        # Save to database
        with sqlite3.connect('chat.db') as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO chat_history 
                        (user_id, message, response, timestamp) 
                        VALUES (?, ?, ?, ?)''',
                     (user_id, data['message'], json.dumps(response),
                      datetime.now()))
            conn.commit()
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
@login_required
def feedback():
    try:
        data = request.json
        with sqlite3.connect('chat.db') as conn:
            c = conn.cursor()
            c.execute('''UPDATE chat_history 
                        SET satisfaction = ? 
                        WHERE id = ?''',
                     (data['satisfaction'], data['chat_id']))
            conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('user_message')
def handle_message(data):
    response = bot.generate_response(data['message'])
    emit('bot_response', {'message': response})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

# Template filters
@app.template_filter('formatdate')
def format_date(value, format='%Y-%m-%d %H:%M:%S'):
    if value:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime(format)
    return ''

# Context processors
@app.context_processor
def utility_processor():
    def get_user_name(user_id):
        with sqlite3.connect('chat.db') as conn:
            c = conn.cursor()
            user = c.execute('SELECT username FROM users WHERE id = ?',
                           (user_id,)).fetchone()
            return user[0] if user else 'Anonymous'
    return dict(get_user_name=get_user_name)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Run the application
    socketio.run(app,
                host='0.0.0.0',
                port=int(os.getenv('PORT', 5000)),
                debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')