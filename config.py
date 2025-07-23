import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gmail Configuration
    GMAIL_EMAIL = os.getenv('GMAIL_EMAIL')
    GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
    GMAIL_SMTP_SERVER = os.getenv('GMAIL_SMTP_SERVER', 'smtp.gmail.com')
    GMAIL_SMTP_PORT = int(os.getenv('GMAIL_SMTP_PORT', 587))
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'finance_agent')
    
    # Google AI Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Application Configuration
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Collections
    EMAILS_COLLECTION = 'emails'
    TRANSACTIONS_COLLECTION = 'transactions'
    TEMPLATES_COLLECTION = 'templates'
    RESPONSES_COLLECTION = 'responses' 