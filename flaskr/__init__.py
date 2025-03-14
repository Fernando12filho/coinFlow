import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

load_dotenv()


secret_key = os.getenv("SECRET_KEY")

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, supports_credentials=True)
    app.config.from_mapping(
        SECRET_KEY=secret_key,
        DATABASE=os.path.join(os.getcwd(), 'flaskr.sqlite'),
        JWT_SECRET_KEY = secret_key,  
        JWT_TOKEN_LOCATION = ['cookies'], 
        JWT_COOKIE_SECURE = True,
        JWT_COOKIE_SAMESITE = 'None', 
        JWT_COOKIE_CSRF_PROTECT = False         
    )
    
    jwt = JWTManager(app)
    
    jwt
    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import home
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app
