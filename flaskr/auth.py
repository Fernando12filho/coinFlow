import functools
from flask import (
    Blueprint, g, jsonify, redirect, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, set_access_cookies, set_refresh_cookies, create_refresh_token

bp = Blueprint('auth', __name__, url_prefix = '/auth')
CORS(bp, origins=["http://localhost:3000"], supports_credentials=True)

        
@bp.route('/login', methods=['POST', 'OPTIONS'])
def login():

    if request.method == 'POST':
        data = request.json
        username = data['username']
        password = data['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        print("Inside login")
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            
            user_id = str(user['id'])
        
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)
            response = jsonify({"msg": "login successful"})
            response.set_cookie(
                'access_token', 
                httponly=True,
                secure=False, 
                samesite='None'
            )
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 200

        return jsonify({"success": False, "error": error}), 400
    if request.method == 'OPTIONS':
        return jsonify({"message": "Preflight request"}), 200 
    return jsonify({"logedin": False})

@bp.route('/register', methods=['GET', 'POST'])
def register(): 
    print("inside register route")
    if request.method == 'POST':
        data = request.json
        username = data['username']
        password = data['password']
        db = get_db()
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)", 
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                return jsonify({"success": False, "error": error}), 400
            else:
                return jsonify({"success": True, "message": "Registration complete"})
            
        return jsonify({"success": False, "error": "Not Registered"}), 400
    else:
        return jsonify({"success": False, "error": "Method not allowed"})

@bp.post('/logout')
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"}), 200


@bp.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({'access_token': new_access_token})

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


    