from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('newsletter', __name__)

# Dummy storage for subscriptions
subscriptions = []

@bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    user = get_jwt_identity()
    
    if not user:
        return jsonify({"msg": "User not found"}), 404

    email = request.json.get('email', None)
    if not email:
        return jsonify({"msg": "Email is required"}), 400

    # Add email to subscriptions
    subscriptions.append(email)
    return jsonify({"msg": "Subscribed successfully"}), 200

@bp.route('/verify-email', methods=['GET'])
def verify_email():
    # Future implementation for email verification
    pass

@bp.route('/confirm-subscription', methods=['GET'])
def confirm_subscription():
    # Future implementation for confirming subscription
    pass