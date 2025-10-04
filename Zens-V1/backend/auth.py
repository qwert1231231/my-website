from flask import Blueprint, request, jsonify, g
from db import get_db

auth_bp = Blueprint('auth', __name__)

# REGISTER
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')  # In production: hash this!

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        db.commit()
        return jsonify({"status": "success", "message": f"User {username} registered"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# LOGIN
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()

    if user:
        user_id, db_password = user
        if password == db_password:  # In production: compare hashed passwords
            return jsonify({"status": "success", "message": f"Logged in as {username}", "user_id": user_id})
    return jsonify({"status": "error", "message": "Invalid username or password"})
