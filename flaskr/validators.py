"""
Input validation utilities for CoinFlow API.
Prevents SQL injection and ensures data integrity.
"""

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


def validate_username(username):
    """
    Validate username format.
    
    Rules:
    - 3-50 characters
    - Alphanumeric, underscores, hyphens only
    - Must start with alphanumeric
    
    Returns: (is_valid, error_message)
    """
    if not username or not isinstance(username, str):
        return False, "Username is required"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, None


def validate_password(password):
    """
    Validate password strength.
    
    Rules:
    - Minimum 8 characters
    - Maximum 128 characters (to prevent DOS)
    - At least one letter
    - At least one number
    
    Returns: (is_valid, error_message)
    """
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password is too long"
    
    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, None


def validate_email(email):
    """
    Basic email validation (used in addition to email_validator library).
    
    Returns: (is_valid, error_message)
    """
    if not email or not isinstance(email, str):
        return False, "Email is required"
    
    email = email.strip()
    
    if len(email) > 254:  # RFC 5321
        return False, "Email is too long"
    
    # Basic pattern check
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False, "Invalid email format"
    
    return True, None


def validate_amount(amount, field_name="Amount"):
    """
    Validate monetary/crypto amounts.
    
    Rules:
    - Must be positive
    - Maximum 16 digits total, 8 decimal places
    - No negative or zero values
    
    Returns: (is_valid, error_message, sanitized_value)
    """
    if amount is None:
        return False, f"{field_name} is required", None
    
    try:
        # Convert to Decimal for precise financial calculations
        decimal_amount = Decimal(str(amount))
        
        if decimal_amount <= 0:
            return False, f"{field_name} must be positive", None
        
        # Check maximum value (prevent overflow)
        if decimal_amount > Decimal('99999999.99999999'):
            return False, f"{field_name} is too large", None
        
        # Check decimal places
        if decimal_amount.as_tuple().exponent < -8:
            return False, f"{field_name} has too many decimal places (max 8)", None
        
        return True, None, float(decimal_amount)
        
    except (ValueError, InvalidOperation, TypeError):
        return False, f"Invalid {field_name.lower()} format", None


def validate_date(date_str, field_name="Date"):
    """
    Validate date string.
    
    Expected format: YYYY-MM-DD
    
    Returns: (is_valid, error_message, datetime_obj)
    """
    if not date_str:
        return False, f"{field_name} is required", None
    
    try:
        date_obj = datetime.strptime(str(date_str), "%Y-%m-%d")
        
        # Check reasonable date range (not in the future, not before Bitcoin existed)
        now = datetime.now()
        bitcoin_genesis = datetime(2009, 1, 3)  # Bitcoin genesis block
        
        if date_obj > now:
            return False, f"{field_name} cannot be in the future", None
        
        if date_obj < bitcoin_genesis:
            return False, f"{field_name} cannot be before Bitcoin existed (2009)", None
        
        return True, None, date_obj
        
    except ValueError:
        return False, f"Invalid {field_name.lower()} format. Use YYYY-MM-DD", None


def validate_coin_name(coin_name):
    """
    Validate cryptocurrency name.
    
    Rules:
    - 1-50 characters
    - Letters, numbers, spaces, hyphens only
    
    Returns: (is_valid, error_message, sanitized_name)
    """
    if not coin_name or not isinstance(coin_name, str):
        return False, "Coin name is required", None
    
    coin_name = coin_name.strip()
    
    if len(coin_name) < 1:
        return False, "Coin name cannot be empty", None
    
    if len(coin_name) > 50:
        return False, "Coin name is too long (max 50 characters)", None
    
    if not re.match(r'^[a-zA-Z0-9\s-]+$', coin_name):
        return False, "Coin name contains invalid characters", None
    
    return True, None, coin_name


def sanitize_integer(value, field_name="Value", min_val=None, max_val=None):
    """
    Sanitize and validate integer values (e.g., IDs).
    
    Returns: (is_valid, error_message, sanitized_value)
    """
    try:
        int_value = int(value)
        
        if min_val is not None and int_value < min_val:
            return False, f"{field_name} must be at least {min_val}", None
        
        if max_val is not None and int_value > max_val:
            return False, f"{field_name} must be at most {max_val}", None
        
        return True, None, int_value
        
    except (ValueError, TypeError):
        return False, f"Invalid {field_name.lower()}", None


def validate_investment_data(data):
    """
    Comprehensive validation for investment creation.
    
    Returns: (is_valid, errors_dict, sanitized_data)
    """
    errors = {}
    sanitized = {}
    
    # Validate coin name
    is_valid, error, coin_name = validate_coin_name(data.get('coin_name'))
    if not is_valid:
        errors['coin_name'] = error
    else:
        sanitized['coin_name'] = coin_name
    
    # Validate investment amount
    is_valid, error, amount = validate_amount(data.get('investment_amount'), "Investment amount")
    if not is_valid:
        errors['investment_amount'] = error
    else:
        sanitized['investment_amount'] = amount
    
    # Validate crypto amount
    is_valid, error, crypto_amount = validate_amount(data.get('crypto_amount'), "Crypto amount")
    if not is_valid:
        errors['crypto_amount'] = error
    else:
        sanitized['crypto_amount'] = crypto_amount
    
    # Validate date
    is_valid, error, date_obj = validate_date(data.get('investment_date'), "Investment date")
    if not is_valid:
        errors['investment_date'] = error
    else:
        sanitized['investment_date'] = date_obj.strftime("%Y-%m-%d")
    
    return len(errors) == 0, errors, sanitized
