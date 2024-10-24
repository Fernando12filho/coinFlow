import os
from flask import Flask
import requests
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint
"""
Oque falta ser feito:
    Criar 
    Adicionar templates
"""

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(os.getcwd(), 'flaskr.sqlite')
    )
    
    # Swagger UI setup
    SWAGGER_URL = '/swagger'  # URL for accessing the swagger UI
    API_URL = '/static/swagger.json'  # Path to your API's swagger file (JSON)
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "CoinFlow API"})
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
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
