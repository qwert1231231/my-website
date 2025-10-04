from flask import Blueprint, request, jsonify
from db import get_db

bank_bp = Blueprint('bank', __name__)

@bank_bp.route('/balance/<int:user_id>', methods=['GET'])
def balance(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT balance FROM bank_accounts WHERE user_id=%s", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = float(result[0])
        return jsonify({"user_id": user_id, "balance": balance})
    return jsonify({"status": "error", "message": "Bank account not found"})

@bank_bp.route('/deposit', methods=['POST'])
def deposit():
    data = request.json
    user_id = data.get('user_id')
    amount = float(data.get('amount'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE bank_accounts SET balance = balance + %s WHERE user_id=%s", (amount, user_id))
    cursor.execute("INSERT INTO transactions (user_id, type, amount) VALUES (%s, 'deposit', %s)", (user_id, amount))
    db.commit()
    return jsonify({"status": "success", "message": f"${amount} deposited for user {user_id}"})
