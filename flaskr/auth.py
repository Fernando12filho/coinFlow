import functools
from flask import (
    Blueprint, g, jsonify, redirect, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, set_access_cookies, set_refresh_cookies, create_refresh_token, unset_jwt_cookies
from email_validator import validate_email, EmailNotValidError

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

        if user is None or not check_password_hash(user['password'], password):
            error = 'Incorrect username or password.'
            return jsonify({"success": False, "error": error}), 400
             
        
        user_id = str(user['id'])
        print("user id is: ", user_id)
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

         # ✅ Prepare response (return the same one!)
        response = jsonify({
        "msg": "login successful",
        "access_token": access_token,  # optional if you return access token in JSON
        "refresh_token": refresh_token, # optional if you return refresh token in JSON
        "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                # is_subscribed
                "isSubscribed": user['isSubscribed']                  
            }
        })

        # ✅ Set JWT cookies (both access and refresh)
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=True,             # False in dev (must be True in production)
            samesite='None'           # None if cross-site (React on localhost:3000)
        )
        set_access_cookies(response, access_token)
        # set_refresh_cookies(response, refresh_token)

        return response, 200

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
        email = data['email']
        db = get_db()
        error = None
        
        
        # Check if the username is already taken
        # Check if the email is already taken
        
        
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required'
        elif not email:
            error = 'Email is required'
            
        try:
            valid = validate_email(email)
            email = valid.email  # replace with normalized email (e.g., lowercased)
        except EmailNotValidError as e:
            return jsonify({'error': str(e)}), 400
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, email) VALUES (?, ?, ?)", 
                    (username, generate_password_hash(password), email)
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
    resp = jsonify({"success": True, "message": "Logged out successfully"})
    unset_jwt_cookies(resp)
    session.clear()
    return resp, 200


@bp.route('/refresh', methods=['GET'])
@jwt_required()
def refresh():
    print("inside refresh")
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    
    response = jsonify({
        "msg": "login successful",
        "access_token": new_access_token,  # optional if you return access token in JSON
    })
    
    set_access_cookies(response, new_access_token)
    # set_refresh_cookies(response, refresh_token)
    return response, 200
    
    

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

    
