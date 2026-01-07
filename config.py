import os
import secrets

class Config:
    """Application configuration settings."""
    
    # Secret key for session management (generate a secure random key)
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Database configuration
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'voting.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # ==================== SMTP EMAIL CONFIGURATION ====================
    # Configure these settings to enable email OTP
    
    # For Gmail: Use smtp.gmail.com and create an "App Password"
    # (Gmail Settings > Security > 2-Step Verification > App Passwords)
    
    # For Outlook/Hotmail: Use smtp.office365.com
    
    # For College SMTP: Use your college's SMTP server
    
    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    SMTP_USER = os.environ.get('SMTP_USER') or 'shaikmaaz77zz@gmail.com'
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or 'ouay egsd huek vyev'
    
    # OTP Settings
    OTP_EXPIRY_MINUTES = 5
