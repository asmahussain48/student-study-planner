import hashlib
import os
import binascii

def hash_password(password):
    """Hash password using PBKDF2"""
    salt = os.urandom(32)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    pwdhash_hex = binascii.hexlify(pwdhash)
    return binascii.hexlify(salt).decode('ascii') + ':' + pwdhash_hex.decode('ascii')

def verify_password(password, stored_hash):
    """Verify password against stored hash"""
    try:
        salt_hex, pwdhash_hex = stored_hash.split(':')
        salt = binascii.unhexlify(salt_hex)
        pwdhash = binascii.unhexlify(pwdhash_hex)
        pwdhash_check = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return pwdhash == pwdhash_check
    except:
        return False

def is_logged_in(session):
    """Check if user is logged in"""
    return 'user_id' in session and 'user_name' in session and 'user_email' in session
