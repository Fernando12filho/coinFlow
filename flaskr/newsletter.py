from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flaskr.db import get_db
from flask_cors import CORS

bp = Blueprint('newsletter', __name__, url_prefix = '/newsletter')
CORS(bp, origins=["http://localhost:3000"], supports_credentials=True)

@bp.post('/subscribe')
@jwt_required()
def subscribe():    
    db = get_db()
    user_id = get_jwt_identity()  
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()
    # Check if user is already subscribed on newsletter
    is_subscribed = db.execute(
        'SELECT * FROM subscribers WHERE user_id = ?', (user_id,)
    ).fetchone()
    
    if is_subscribed:
        return jsonify({"success": False, "message": "User is already subscribed"}), 200
    
    db.execute(
        'INSERT INTO subscribers (user_id, email) VALUES (?, ?)', (user_id, user['email'])
    )
    db.execute(
        'UPDATE user SET is_subscribed = 1 WHERE id = ?', (user_id,)
    )
    db.commit()
    return jsonify({"success": True, "message": "User subscribed successfully"}), 200


@bp.route('/verify-email', methods=['GET'])
def verify_email():
    # Future implementation for email verification
    pass

@bp.route('/confirm-subscription', methods=['GET'])
def confirm_subscription():
    # Future implementation for confirming subscription
    pass