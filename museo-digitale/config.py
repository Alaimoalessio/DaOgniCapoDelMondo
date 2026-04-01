"""
Configuration settings for Da ogni capo del mondo - Digital Museum
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    # Development: SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{BASE_DIR / "museo.db"}'
    
    # Production: PostgreSQL (uncomment and configure when ready)
    # SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/museo_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Pagination
    ITEMS_PER_PAGE = 12
    
    # File uploads (for future enhancements)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'images'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Internationalization
    LANGUAGES = {
        'it': 'Italiano',
        'en': 'English',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch'
    }
    BABEL_DEFAULT_LOCALE = 'it'
    BABEL_DEFAULT_TIMEZONE = 'Europe/Rome'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
