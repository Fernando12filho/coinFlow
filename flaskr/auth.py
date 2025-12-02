import functools
from flask import (
    Blueprint, g, jsonify, redirect, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, set_access_cookies, set_refresh_cookies, create_refresh_token, unset_jwt_cookies
from email_validator import validate_email as email_validate, EmailNotValidError
from flaskr.validators import validate_username, validate_password, validate_email

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
                "is_subscribed": user['is_subscribed'] # default to False if not present                 
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

    if request.method == 'OPTIONS':
        return jsonify({"message": "Preflight request"}), 200

    return jsonify({"logedin": False})

@bp.route('/register', methods=['GET', 'POST'])
def register(): 
    """
    Register a new user with validation.
    Prevents SQL injection and enforces strong passwords.
    """
    print("inside register route")
    
    if request.method == 'POST':
        try:
            data = request.json
            
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400
            
            username = data.get('username', '').strip()
            password = data.get('password', '')
            email = data.get('email', '').strip()
            
            # Validate username
            is_valid, error = validate_username(username)
            if not is_valid:
                return jsonify({'success': False, 'error': error}), 400
            
            # Validate password
            is_valid, error = validate_password(password)
            if not is_valid:
                return jsonify({'success': False, 'error': error}), 400
            
            # Validate email format (basic check)
            is_valid, error = validate_email(email)
            if not is_valid:
                return jsonify({'success': False, 'error': error}), 400
            
            # Validate email with email_validator library
            try:
                valid = email_validate(email)
                email = valid.email  # Normalized email
            except EmailNotValidError as e:
                return jsonify({'success': False, 'error': str(e)}), 400
            
            db = get_db()
            
            # Check if username already exists
            existing_user = db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
            ).fetchone()
            
            if existing_user:
                return jsonify({"success": False, "error": "Username already taken"}), 400
            
            # Check if email already exists
            existing_email = db.execute(
                'SELECT id FROM user WHERE email = ?', (email,)
            ).fetchone()
            
            if existing_email:
                return jsonify({"success": False, "error": "Email already registered"}), 400
            
            # Insert new user
            db.execute(
                "INSERT INTO user (username, password, email) VALUES (?, ?, ?)", 
                (username, generate_password_hash(password), email)
            )
            db.commit()
            
            return jsonify({"success": True, "message": "Registration complete"}), 201
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return jsonify({"success": False, "error": "Registration failed"}), 500
    
    else:
        return jsonify({"success": False, "error": "Method not allowed"}), 405

@bp.post('/logout')
def logout():
    resp = jsonify({"success": True, "message": "Logged out successfully"})
    unset_jwt_cookies(resp)
    session.clear()
    return resp, 200

def get_current_user_info():
    username = get_jwt_identity()
    if username is None:
        return None
    print("User not found: ", username)
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (username,)
    ).fetchone()
    
    print("User found: ", user)

    if user is None:
        return None

    return {
        "id": user['id'],
        "username": user['username'],
        "email": user['email'],
        "is_subscribed": user['is_subscribed' ] # default to False
    }
    
@bp.route('/refresh', methods=['GET'])
@jwt_required()
def refresh():
    print("inside refresh")
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    
    user_info = get_current_user_info()
    if not user_info:
        return jsonify({"error": "User not found"}), 404

    response = jsonify({
        "msg": "login successful",
        "access_token": new_access_token,
        "user": user_info,       
    })
    
    set_access_cookies(response, new_access_token)
    return response, 200
    
    

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

    
