import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import requests
from dotenv import load_dotenv
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('home', __name__)

#database
'''
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount DECIMAL(16, 8) NOT NULL,
    purchase_date DATE NOT NULL,
    purchase_price DECIMAL(16, 2) NOT NULL,
    current_price DECIMAL(16, 2),
    profit_loss DECIMAL(16, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
    
'''

#loads api key
load_dotenv()
api_key = os.getenv("API_KEY")

#gets bitcoin price
def get_bitcoin_price():
        api_url = "https://api.coincap.io/v2/assets/bitcoin"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(api_url, headers=headers)
    
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None

#getting user investments
def get_user_investments(user_id):
    # Assuming a connection to SQLite is already set up
    db = get_db()  # Example function to get DB connection
    cursor = db.cursor()

    query = '''
    SELECT coin_name, id, amount, purchase_date, purchase_price 
    FROM investments 
    WHERE user_id = ?;
    '''
    cursor.execute(query, (user_id,))
    investments = cursor.fetchall()
    db.close()

    return investments

@bp.route('/')
@login_required
def index():
    
    if g.user:
        user_id = g.user['id']
        investments_made = get_user_investments(user_id)
        return render_template('home/index.html', investments_made=investments_made) #here is where investments will be queried and sent to front end
    return redirect(url_for('auth.login'))
    
@bp.post('/create')
def create_investment():
    print(g.user['id'])   
    print('Inside create route')
    #coin_name, investment_amount in dollars, cryptocurrency_amount (amount in bitcoin / sathoshis), purchase_date
    coin_name = request.form['coin_name']
    investment_amount = request.form['investment_amount']
    crypto_amount = request.form['crypto_amount']
    investment_date = request.form['investment_date']
    error = None
    
    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO investments (user_id, coin_name, amount, purchase_date, purchase_price)'
            'VALUES (?, ?, ?, ?, ?)',
            (g.user['id'], coin_name, crypto_amount, investment_date, investment_amount)
        )
        db.commit()
        print('Investment added sucessfully')
        print(coin_name)
        return redirect(url_for('home.index'))
    
