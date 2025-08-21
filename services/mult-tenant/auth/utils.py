import hashlib
import time
import random
import string

def generate_simple_token(user_id: int) -> str:
    """
    Generate a simple token without UUID using user ID and timestamp
    
    Args:
        user_id: User ID
        
    Returns:
        Simple token string
    """
    # Create a unique token using user ID, timestamp, and random string
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    token_string = f"{user_id}_{timestamp}_{random_str}"
    
    # Create MD5 hash
    return hashlib.md5(token_string.encode()).hexdigest()

def generate_account_number(account_id: int) -> str:
    """
    Generate account number using ID
    
    Args:
        account_id: Account ID
        
    Returns:
        Account number string
    """
    return f"ACC{str(account_id).zfill(8)}"

def generate_verification_token(user_id: int) -> str:
    """
    Generate verification token for account verification
    
    Args:
        user_id: User ID
        
    Returns:
        Verification token string
    """
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.digits, k=6))
    token_string = f"VERIFY_{user_id}_{timestamp}_{random_str}"
    
    return hashlib.md5(token_string.encode()).hexdigest()[:12].upper()
