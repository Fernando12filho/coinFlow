import os
from flask import (
    Blueprint, flash, g, jsonify, redirect, render_template, request, url_for, session
)
from dotenv import load_dotenv
from werkzeug.exceptions import abort
from flaskr.auth import login_required, refresh
from flaskr.db import get_db
from flask import request
import requests
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime
from flaskr.validators import validate_investment_data, sanitize_integer


bp = Blueprint('home', __name__)

#loads api key
load_dotenv()
api_key = os.getenv("API_KEY")

#gets bitcoin price
def get_bitcoin_price():
    api_url = "https://rest.coincap.io/v3/assets/bitcoin"  # Updated API URL
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(api_url, headers=headers)   
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching BTC price: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching BTC price: {e}")
        return None
      
#getting user investments
def get_user_investments(user_id):
    """
    Fetch all investments for a given user.
    Uses Flask's g object for connection management - don't close manually.
    """
    print("user id is:", user_id)
    db = get_db()
    
    # Use db.execute directly - no need for cursor
    investments = db.execute(
        '''
        SELECT coin_name, id, amount, purchase_date, purchase_price, profit_loss 
        FROM investments 
        WHERE user_id = ?
        ORDER BY purchase_date DESC
        ''',
        (user_id,)
    ).fetchall()
    
    # Convert Row objects to dictionaries
    investments = [dict(row) for row in investments]
    calculate_gain_losses(investments)
    # Don't close db here - Flask's g object handles it automatically

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
    """
    Calculate profit/loss for each investment based on current Bitcoin price.
    Updates database with calculated values.
    """
    btc_price_data = get_bitcoin_price()
    
    if btc_price_data is not None:
        current_btc_price = float(btc_price_data['data']['priceUsd'])
        db = get_db()
        
        # Update all investments in a single transaction
        for inv in investments:
            # Avoid division by zero
            if inv['amount'] == 0:
                continue
                
            purchase_unit_price = inv['purchase_price'] / inv['amount']
            profit_loss = (current_btc_price - purchase_unit_price) * inv['amount']
            profit_loss_formatted = "{:.2f}".format(profit_loss)
            
            print(f"Investment ID {inv['id']}: Purchase price ${purchase_unit_price:.2f}, P/L: ${profit_loss_formatted}")
            
            # Update the database with profit/loss
            db.execute(
                'UPDATE investments SET profit_loss = ? WHERE id = ?', 
                (profit_loss_formatted, inv['id'])
            )
        
        # Commit once after all updates
        db.commit()
        # Don't close db here - Flask's g object handles it automatically
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

def validate_iso_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Date must be in format YYYY-MM-DD")

#sends all data needed to the frontend
@bp.get('/')
@jwt_required()
def index(): 
    print("inside index route")
    current_user = get_jwt_identity()     
    investments_made = get_user_investments(current_user)
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
@jwt_required()
def create_investment():
    """
    Create a new investment record.
    Validates all inputs and prevents SQL injection via parameterized queries.
    """
    print('Inside create route')
    
    try:
        data = request.json
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Comprehensive validation
        is_valid, errors, sanitized_data = validate_investment_data(data)
        
        if not is_valid:
            return jsonify({"success": False, "errors": errors}), 400
        
        user = get_jwt_identity()
        
        db = get_db()
        db.execute(
            'INSERT INTO investments (user_id, coin_name, amount, purchase_date, purchase_price) '
            'VALUES (?, ?, ?, ?, ?)',
            (
                user,
                sanitized_data['coin_name'],
                sanitized_data['crypto_amount'],
                sanitized_data['investment_date'],
                sanitized_data['investment_amount']
            )
        )
        db.commit()
        
        # Get updated investments list
        update_investment = get_user_investments(user)
        print(f'Investment added successfully: {sanitized_data["coin_name"]}')
        
        return jsonify({
            "success": True, 
            "message": "Investment added successfully", 
            "investments": update_investment
        }), 200
        
    except Exception as e:
        print(f"Error creating investment: {str(e)}")
        return jsonify({"success": False, "error": "Failed to create investment"}), 500
  
  
@bp.route('/delete/<int:id>', methods=["DELETE"])
@jwt_required()
def delete_investment(id):
    """
    Delete an investment by ID.
    Validates that the investment belongs to the authenticated user.
    """
    print(f"Transaction ID to be deleted: {id}")
    
    try:
        current_user = get_jwt_identity()
        db = get_db()
        
        # First, verify the investment belongs to this user
        investment = db.execute(
            'SELECT user_id FROM investments WHERE id = ?',
            (id,)
        ).fetchone()
        
        if not investment:
            return jsonify({"success": False, "error": "Investment not found"}), 404
        
        if str(investment['user_id']) != str(current_user):
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        # Delete the investment
        db.execute('DELETE FROM investments WHERE id = ?', (id,))
        db.commit()
        
        # Get updated investments list
        update_investment = get_user_investments(current_user)
        print(f"Deleted investment with ID: {id}")
        
        return jsonify({
            "success": True, 
            "message": "Investment deleted", 
            "investments": update_investment
        }), 200
        
    except Exception as e:
        print(f"Error deleting investment: {str(e)}")
        return jsonify({"success": False, "error": "Failed to delete investment"}), 500
    

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