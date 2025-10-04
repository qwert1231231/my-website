import os
import sqlite3
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from flask_session import Session
from dotenv import load_dotenv
import openai

# Load environment
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
DB_PATH = os.getenv("DATABASE_PATH", "db/chat.sql")

# Flask setup
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# --- DB Helpers ---
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Chats
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_message TEXT,
        ai_reply TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("chatpage"))
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username, password = data.get("username"), data.get("password")
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Username already exists"})
    finally:
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username, password = data.get("username"), data.get("password")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        session["user_id"] = user["id"]
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid login"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/chatpage")
def chatpage():
    if "user_id" not in session:
        return redirect("/")
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"})

    data = request.json
    user_message = data.get("message", "")

    # Call OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are Zenno AI, a helpful assistant."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=200
    )
    reply = response["choices"][0]["message"]["content"].strip()

    # Save to DB
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (user_id, user_message, ai_reply) VALUES (?, ?, ?)",
        (session["user_id"], user_message, reply)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "reply": reply})

@app.route("/history", methods=["GET"])
def history():
    if "user_id" not in session:
        return jsonify([])
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_message, ai_reply, timestamp FROM chats WHERE user_id=? ORDER BY id DESC LIMIT 20",
        (session["user_id"],)
    )
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    os.makedirs("db", exist_ok=True)
    app.run(port=5000, debug=True)
