import os
from flask import (
    Blueprint, flash, g, jsonify, redirect, render_template, request, url_for
)
from dotenv import load_dotenv
from werkzeug.exceptions import abort
from flaskr.auth import login_required, refresh
from flaskr.db import get_db
from flask import request
import requests
from flask_jwt_extended import get_jwt_identity, jwt_required


bp = Blueprint('home', __name__)

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
    db = get_db() 
    cursor = db.cursor()

    query = '''
    SELECT coin_name, id, amount, purchase_date, purchase_price, profit_loss 
    FROM investments 
    WHERE user_id = ?
    ORDER BY purchase_date DESC;
    '''
    cursor.execute(query, (user_id,))
    investments = cursor.fetchall()
    
    investments = [dict(row) for row in investments]
    calculate_gain_losses(investments)
    db.close()

    return investments

def get_total_invested(investments):
    total_investment = 0
      
    for inv in investments:
        investment_amount = float(inv['purchase_price'])  
        total_investment += investment_amount
        total_investment_formatted = "{:.2f}".format(total_investment)
        
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
        db = get_db()  
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
        
# Set current investments value
def calculate_investments_value(investments):
    total_invested_value = get_total_invested(investments)
    for inv in investments:
        total_invested_value = total_invested_value + inv['profit_loss']
    print("total invested value is: ", total_invested_value)
    return total_invested_value
   
# set total amount of bitcoin user has 
def calculate_btc_amount(investments):
    total_btc_amount = 0
    for inv in investments:
        total_btc_amount = total_btc_amount + inv['amount'] 
    print("total amount of bitcoin: ", total_btc_amount) 
    return total_btc_amount   

#sends all data needed to the frontend
@bp.get('/')
@jwt_required()
def index(): 
    print("inside index route")
    current_user = get_jwt_identity()     
    user_id = current_user
    investments_made = [dict(row) for row in get_user_investments(user_id)]
    #calculate_gain_losses(investments_made)
    total_invested = get_total_invested(investments_made)
    total_investment_value = calculate_investments_value(investments_made)
    total_btc_amount = calculate_btc_amount(investments_made)
    print(total_invested)
    return jsonify({
        "user": current_user,
        "investments": investments_made,
        "total_invested": total_invested,
        "total_investment_value": total_investment_value,
        "total_btc_amount": total_btc_amount
    }), 200 #here is where investments will be queried and sent to front end
    

@bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "connected", "message": "API is reachable"}), 200

#route that takes user to its BRL transactions
@bp.route('/brl')
@login_required
def index_brl():
    if g.user:
        user_id = g.user['id']
        investments_made = get_user_investments(user_id)
        total_invested = get_total_invested(investments_made)
        return render_template('home/index_brl.html', investments_made=investments_made, performance=total_invested)
    return redirect(url_for('auth.login'))


    
@bp.post('/create')
def create_investment():

    #TODO: Profit/loss calculates only after re-render  
    print('Inside create route')
    data = request.json
    #coin_name, investment_amount in dollars, cryptocurrency_amount (amount in bitcoin / sathoshis), purchase_date
    coin_name = data['coin_name']
    investment_amount = data['investment_amount']
    crypto_amount = data['crypto_amount']
    investment_date = data['investment_date']
    error = None
    
    if error is not None:
        print(error)
        return jsonify({"success": False, "error": error}), 400
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
        return jsonify({"success": True, "message": "Investment added successfully"}), 201
  
  
@bp.post('/<int:id>/delete')
def delete_investment(id):
    print("transaction id to be deleted is", id)
    db = get_db()
    investment = db.execute(
        'SELECT * FROM investments WHERE id = ?',
        (id,)
    ).fetchone()

    if investment is None:
        return jsonify({"success": False, "message": "Investment not found"}), 404

    db.execute(
        'DELETE FROM investments WHERE id = ?',
        (id,)
    )
    db.commit()
    db.close()
    print(f"Deleted investment with ID: {id}")
    return jsonify({"success": True, "message": "Investment deleted"}), 200
    

@bp.post('/update')
def update_investment(id):
    #TODO: finish the update function, think about how it can be properly set
    print("inside update function")
    return redirect(url_for('home.index'))


@bp.route("/api/crypto-prices", methods=["GET"])
def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": "bitcoin,ethereum,solana",
        "order": "market_cap_desc",
        "per_page": 3,
        "page": 1,
        "sparkline": False,
    }
    response = requests.get(url, params=params)
    return jsonify(response.json())

@bp.route("/api/news", methods=["GET"])
def get_crypto_news():
    url = ""
    params = {
        
    }
    response = requests.get(url, params=params)
    return jsonify(response.json)