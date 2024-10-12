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
    SELECT coin_name, id, amount, purchase_date, purchase_price, profit_loss 
    FROM investments 
    WHERE user_id = ?
    ORDER BY purchase_date DESC;
    '''
    cursor.execute(query, (user_id,))
    investments = cursor.fetchall()
    calculate_gain_losses(investments)
    db.close()

    return investments

def get_total_invested(investments):
    total_investment = 0
      
    for inv in investments:
        investment_amount = float(inv['purchase_price'])  
        total_investment += investment_amount
        
    return total_investment

#calculate gain or loses according to updated bitcoin price
#Calculate bitcoin price at the time user bought it: purchase_price / amount of bitcoin
#After calculation, function it will update database
def calculate_gain_losses(investments):
    btc_price_data = get_bitcoin_price()
    
    if btc_price_data is not None:
        current_btc_price = float(btc_price_data['data']['priceUsd'])  # Extracting the current price
        print(current_btc_price)
        # Open the database connection
        db = get_db()  # Ensure you have a valid function that opens a connection
        for inv in investments:
            purchase_unit_price = inv['purchase_price'] / inv['amount']  # Purchase price per unit
            profit_loss = (current_btc_price - purchase_unit_price) * inv['amount']  # Gain/Loss calculation
            profit_loss_formated = "{:.2f}".format(profit_loss)
            print("inside gain_losses for loop")
            print("Purchase Unite Price: ", purchase_unit_price)
            print("Profit or loss: ", profit_loss_formated)
            # Update the database with current price and profit/loss
            db.execute(
                '''
                UPDATE investments 
                SET profit_loss = ?
                WHERE id = ? 
                ''', 
                (profit_loss_formated, inv['id'],)
            )
            db.commit()  # Commit the changes after the loop
        
    else:
        print("Error fetching Bitcoin price")
        
#sends all data needed to the frontend
@bp.route('/')
@login_required
def index():   
    if g.user:
        user_id = g.user['id']
        investments_made = get_user_investments(user_id)
        #calculate_gain_losses(investments_made)
        total_invested = get_total_invested(investments_made)
        print(total_invested)
        return render_template('home/index.html', investments_made=investments_made, performance = total_invested) #here is where investments will be queried and sent to front end
    return redirect(url_for('auth.login'))
    
@bp.post('/create')
def create_investment():
    #TODO: It still do not accept the amount of decimals it should have. Need to be fixed
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
        db.close()
        print('Investment added sucessfully')
        print(coin_name)
        return redirect(url_for('home.index'))
  
  
@bp.post('/<int:id>/delete')
def delete_investment(id):
    #TODO: make sure the database is being properly updated
    print(id)
    db = get_db()
    db.execute(
        'DELETE FROM investments WHERE id = ?',
        (id,)
    )
    db.commit()
    db.close()
    print("inside delete function")
    return redirect(url_for('home.index'))
    

@bp.post('/update')
def update_investment(id):
    #TODO: finish the update function, think about how it can be properly set
    print("inside update function")
    return redirect(url_for('home.index'))