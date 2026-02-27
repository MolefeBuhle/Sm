import os

class Config:
    # Get secret key from environment variable, with fallback for development
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Database configuration - use environment variable if available (for Render), otherwise SQLite for local
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///smartmed.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False