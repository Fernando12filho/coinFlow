import os
from flask import Flask, g, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
"""
Oque falta ser feito:
    Criar 
    Adicionar templates
"""

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, supports_credentials=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(os.getcwd(), 'flaskr.sqlite')
    )
    
    
    @app.route('/myinvestments')
    def hello():
        return "home page"
    
    
    @app.route('/addInvestments')
    def add_investments():
        return "adding nothing yet"
    
    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import home
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app
