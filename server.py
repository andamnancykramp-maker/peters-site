from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = 'peter_secret_key_2026'
CORS(app, supports_credentials=True)

# ===== DATABASE =====
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        date TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        comment TEXT NOT NULL,
        date TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        date TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        count INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS visitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        date TEXT NOT NULL
    )''')

    c.execute('SELECT COUNT(*) FROM likes')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO likes (count) VALUES (0)')

    conn.commit()
    conn.close()

# ===== SERVE HOMEPAGE =====
@app.route('/')
def home():
    return app.send_static_file('index.html')

# ===== REGISTER =====
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name', '')
    email = data.get('email', '')
    password = data.get('password', '')
    date = datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Please fill all fields!'})

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (name, email, password, date) VALUES (?, ?, ?, ?)',
                  (name, email, password, date))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Account created!'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Email already exists!'})

# ===== LOGIN =====
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email FROM users WHERE email=? AND password=?',
              (email, password))
    user = c.fetchone()

    # Log visitor
    date = datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')
    if user:
        c.execute('INSERT INTO visitors (name, date) VALUES (?, ?)', (user[1], date))
        conn.commit()

    conn.close()

    if user:
        return jsonify({'success': True, 'user': {'id': user[0], 'name': user[1], 'email': user[2]}})
    return jsonify({'success': False, 'message': 'Wrong email or password!'})

# ===== SAVE COMMENT =====
@app.route('/api/comment', methods=['POST'])
def save_comment():
    data = request.json
    name = data.get('name', 'Anonymous')
    comment = data.get('comment', '')
    date = datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')
    if not comment:
        return jsonify({'success': False, 'message': 'Comment is empty!'})
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO comments (name, comment, date) VALUES (?, ?, ?)',
              (name, comment, date))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Comment saved!'})

# ===== GET COMMENTS =====
@app.route('/api/comments', methods=['GET'])
def get_comments():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, name, comment, date FROM comments ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    comments = [{'id': r[0], 'name': r[1], 'comment': r[2], 'date': r[3]} for r in rows]
    return jsonify({'success': True, 'comments': comments})

# ===== SAVE MESSAGE =====
@app.route('/api/message', methods=['POST'])
def save_message():
    data = request.json
    name = data.get('name', '')
    email = data.get('email', '')
    subject = data.get('subject', '')
    message = data.get('message', '')
    date = datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')
    if not name or not email or not message:
        return jsonify({'success': False, 'message': 'Please fill all fields!'})
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (name, email, subject, message, date) VALUES (?, ?, ?, ?, ?)',
              (name, email, subject, message, date))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Message saved!'})

# ===== LIKE =====
@app.route('/api/like', methods=['POST'])
def add_like():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE likes SET count = count + 1 WHERE id = 1')
    conn.commit()
    c.execute('SELECT count FROM likes WHERE id = 1')
    count = c.fetchone()[0]
    conn.close()
    return jsonify({'success': True, 'likes': count})

# ===== GET LIKES =====
@app.route('/api/likes', methods=['GET'])
def get_likes():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT count FROM likes WHERE id = 1')
    count = c.fetchone()[0]
    conn.close()
    return jsonify({'success': True, 'likes': count})

# ===== DASHBOARD DATA (ADMIN) =====
@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM comments')
    total_comments = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM messages')
    total_messages = c.fetchone()[0]

    c.execute('SELECT count FROM likes WHERE id = 1')
    total_likes = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM visitors')
    total_visitors = c.fetchone()[0]

    c.execute('SELECT name, comment, date FROM comments ORDER BY id DESC LIMIT 5')
    recent_comments = [{'name': r[0], 'comment': r[1], 'date': r[2]} for r in c.fetchall()]

    c.execute('SELECT name, email, subject, message, date FROM messages ORDER BY id DESC LIMIT 5')
    recent_messages = [{'name': r[0], 'email': r[1], 'subject': r[2], 'message': r[3], 'date': r[4]} for r in c.fetchall()]

    c.execute('SELECT name, date FROM visitors ORDER BY id DESC LIMIT 5')
    recent_visitors = [{'name': r[0], 'date': r[1]} for r in c.fetchall()]

    conn.close()

    return jsonify({
        'success': True,
        'stats': {
            'users': total_users,
            'comments': total_comments,
            'messages': total_messages,
            'likes': total_likes,
            'visitors': total_visitors
        },
        'recent_comments': recent_comments,
        'recent_messages': recent_messages,
        'recent_visitors': recent_visitors
    })

if __name__ == '__main__':
    init_db()
    print("✅ Server running at http://localhost:5000")
    print("📊 Dashboard at http://localhost:5000/dashboard.html")
    app.run(debug=True, port=5000)