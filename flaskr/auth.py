import functools
from flask import (
    Blueprint, g, jsonify, redirect, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from flask_cors import CORS

bp = Blueprint('auth', __name__, url_prefix = '/auth')
CORS(bp, origins=["http://localhost:3000"], supports_credentials=True)
@bp.before_app_request
def load_logged_in_user():
    print("inside load logged in user, session user id is: #", session.get('user_id'))
    user_id = session.get('user_id')
    if user_id is None:
        print("g.user set to none")
        g.user = None
    else:
        print("g.user succesfully set")
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        
@bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    print("inside login")
    if request.method == 'POST':
        print("inside post method")
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
            session.clear()
            session['user_id'] = user['id']
            print("User id set to: ", session.get('user_id'))
            return jsonify({
                "success": True,
                "message": "Logged in successfully",
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    # You can add any additional user fields here if needed
                }
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

@bp.route('/logout')
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"}), 200

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


    