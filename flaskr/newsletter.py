from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flaskr.db import get_db
from flask_cors import CORS

bp = Blueprint('newsletter', __name__, url_prefix = '/newsletter')
CORS(bp, origins=["http://localhost:3000"], supports_credentials=True)

@bp.post('/subscribe')
@jwt_required()
def subscribe():
    """
    Subscribe authenticated user to newsletter.
    Validates user exists and prevents duplicate subscriptions.
    """
    try:
        db = get_db()
        user_id = get_jwt_identity()
        
        # Get user information
        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        # Check if user is already subscribed to newsletter
        is_subscribed = db.execute(
            'SELECT * FROM subscribers WHERE user_id = ?', (user_id,)
        ).fetchone()
        
        if is_subscribed:
            return jsonify({"success": False, "message": "User is already subscribed"}), 200
        
        # Add subscription
        db.execute(
            'INSERT INTO subscribers (user_id, email) VALUES (?, ?)', 
            (user_id, user['email'])
        )
        
        # Update user record
        db.execute(
            'UPDATE user SET is_subscribed = 1 WHERE id = ?', 
            (user_id,)
        )
        
        db.commit()
        
        return jsonify({"success": True, "message": "User subscribed successfully"}), 200
        
    except Exception as e:
        print(f"Error subscribing user: {str(e)}")
        return jsonify({"success": False, "message": "Failed to subscribe"}), 500


@bp.route('/verify-email', methods=['GET'])
def verify_email():
    # Future implementation for email verification
    pass

@bp.route('/confirm-subscription', methods=['GET'])
def confirm_subscription():
    # Future implementation for confirming subscription
    pass