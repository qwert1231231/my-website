from flask import Blueprint, request, jsonify
from db import get_db

data_bp = Blueprint('data', __name__)

@data_bp.route('/save_chat', methods=['POST'])
def save_chat():
    data = request.json
    user_id = data.get('user_id')
    chat_text = data.get('chat_text')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO user_data (user_id, data_type, data_text) VALUES (%s, %s, %s)",
                   (user_id, "chat", chat_text))
    db.commit()
    return jsonify({"status": "success", "message": "Chat saved"})

@data_bp.route('/get_chats/<int:user_id>', methods=['GET'])
def get_chats(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT data_text FROM user_data WHERE user_id=%s AND data_type='chat'", (user_id,))
    chats = [row[0] for row in cursor.fetchall()]
    return jsonify({"user_id": user_id, "chats": chats})
