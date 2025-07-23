from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from config import Config

logger = logging.getLogger(__name__)

class MongoDBClient:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client[Config.MONGODB_DATABASE]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def get_collection(self, collection_name):
        """Get a specific collection"""
        return self.db[collection_name]
    
    def insert_email(self, email_data):
        """Insert parsed email data"""
        collection = self.get_collection(Config.EMAILS_COLLECTION)
        return collection.insert_one(email_data)
    
    def insert_transaction(self, transaction_data):
        """Insert transaction data"""
        collection = self.get_collection(Config.TRANSACTIONS_COLLECTION)
        return collection.insert_one(transaction_data)
    
    def insert_template(self, template_data):
        """Insert response template"""
        collection = self.get_collection(Config.TEMPLATES_COLLECTION)
        return collection.insert_one(template_data)
    
    def insert_response(self, response_data):
        """Insert generated response"""
        collection = self.get_collection(Config.RESPONSES_COLLECTION)
        return collection.insert_one(response_data)
    
    def get_all_emails(self):
        """Get all emails"""
        collection = self.get_collection(Config.EMAILS_COLLECTION)
        return list(collection.find().sort('timestamp', -1))
    
    def get_all_transactions(self):
        """Get all transactions, sorted by mapping_timestamp if present, else extraction_timestamp, else timestamp"""
        collection = self.get_collection(Config.TRANSACTIONS_COLLECTION)
        # Try mapping_timestamp, then extraction_timestamp, then timestamp
        for field in ['mapping_timestamp', 'extraction_timestamp', 'timestamp']:
            if collection.find_one({field: {"$exists": True}}):
                return list(collection.find().sort(field, -1))
        return list(collection.find())
    
    def get_templates_by_type(self, template_type):
        """Get templates by type"""
        collection = self.get_collection(Config.TEMPLATES_COLLECTION)
        return list(collection.find({'type': template_type}))
    
    def get_all_responses(self):
        """Get all generated replies/responses, sorted by generation_timestamp if present, else timestamp"""
        collection = self.get_collection(Config.RESPONSES_COLLECTION)
        for field in ['generation_timestamp', 'timestamp']:
            if collection.find_one({field: {"$exists": True}}):
                return list(collection.find().sort(field, -1))
        return list(collection.find())
    
    def get_transaction_by_mail_id(self, mail_id):
        """Get a transaction by its Mail ID field"""
        collection = self.get_collection(Config.TRANSACTIONS_COLLECTION)
        return collection.find_one({'ledger_entry.Mail ID': mail_id})
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global MongoDB client instance
mongo_client = MongoDBClient() 