import logging
import time
from datetime import datetime
from typing import List, Dict, Any

from agents.email_parser_agent import email_parser_agent
from agents.content_classifier_agent import content_classifier_agent
from agents.data_extractor_agent import data_extractor_agent
from agents.ledger_mapper_agent import ledger_mapper_agent
from agents.rag_reply_generator_agent import rag_reply_generator_agent
from database.mongo_client import mongo_client
from config import Config

logger = logging.getLogger(__name__)

class FinanceAgentOrchestrator:
    def __init__(self):
        self.agents = {
            'email_parser': email_parser_agent,
            'content_classifier': content_classifier_agent,
            'data_extractor': data_extractor_agent,
            'ledger_mapper': ledger_mapper_agent,
            'rag_reply_generator': rag_reply_generator_agent
        }
        
    def process_single_email(self, email_data):
        """Process a single email through the entire pipeline"""
        try:
            logger.info("Starting email processing pipeline")
            
            # Step 1: Email Parser Agent
            logger.info("Step 1: Parsing email...")
            parsed_email = email_parser_agent.parse_email(email_data)
            
            # Step 2: Content Classifier Agent
            logger.info("Step 2: Classifying email content...")
            classification = content_classifier_agent.classify_email(parsed_email)
            
            # Only process if intent is relevant
            allowed_intents = [
                "Invoice", "Payment Confirmation", "Bank Alert", "Payment Request",
                "Vendor Communication", "Client Communication", "Financial Report", "Expense Report",
                "Expense", "Bill", "Quotation"
            ]
            if (not classification.financial_relevance) or (classification.primary_intent not in allowed_intents):
                logger.info(f"Email intent '{classification.primary_intent}' is not relevant. Skipping.")
                return {
                    'email_id': parsed_email.message_id,
                    'classification': classification.dict(),
                    'processing_timestamp': datetime.now(),
                    'pipeline_status': 'not_relevant'
                }
            
            # Step 3: Data Extractor Agent
            logger.info("Step 3: Extracting financial data...")
            extracted_data = data_extractor_agent.extract_data(parsed_email, classification)
            
            # Step 4: Ledger Mapper Agent
            logger.info("Step 4: Mapping to ledger...")
            ledger_entry = ledger_mapper_agent.map_to_ledger(extracted_data, classification, parsed_email)
            
            # Step 5: RAG Reply Generator Agent
            logger.info("Step 5: Generating reply...")
            generated_reply, reply_attachments = rag_reply_generator_agent.generate_reply(parsed_email, classification, extracted_data)
            
            # Create comprehensive result
            result = {
                'email_id': parsed_email.message_id,
                'parsed_email': parsed_email.dict(),
                'classification': classification.dict(),
                'extracted_data': extracted_data.dict(),
                'ledger_entry': ledger_entry.dict(),
                'generated_reply': generated_reply.dict(),
                'reply_attachments': reply_attachments,
                'processing_timestamp': datetime.now(),
                'pipeline_status': 'completed'
            }
            
            logger.info("Email processing pipeline completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in email processing pipeline: {e}")
            return {
                'email_id': email_data.get('message_id', 'unknown'),
                'error': str(e),
                'processing_timestamp': datetime.now(),
                'pipeline_status': 'failed'
            }
    
    def process_batch_emails(self, limit=50):
        """Process a batch of all unread emails from Gmail"""
        try:
            logger.info(f"Starting batch processing of {limit} emails")
            # Step 1: Fetch and parse all unread emails
            logger.info("Step 1: Fetching and parsing emails...")
            parsed_emails = email_parser_agent.fetch_and_parse_emails(limit=limit)
            if not parsed_emails:
                logger.warning("No emails found to process")
                return []
            results = []
            for parsed_email in parsed_emails:
                try:
                    # Step 2: Classify email
                    classification = content_classifier_agent.classify_email(parsed_email)
                    allowed_intents = [
                        "Invoice", "Payment Confirmation", "Bank Alert", "Payment Request",
                        "Vendor Communication", "Client Communication", "Financial Report", "Expense Report",
                        "Expense", "Bill", "Quotation"
                    ]
                    if (not classification.financial_relevance) or (classification.primary_intent not in allowed_intents):
                        logger.info(f"Email intent '{classification.primary_intent}' is not relevant. Skipping.")
                        continue
                    # Step 3: Extract data
                    extracted_data = data_extractor_agent.extract_data(parsed_email, classification)
                    # Step 4: Map to ledger
                    ledger_entry = ledger_mapper_agent.map_to_ledger(extracted_data, classification, parsed_email)
                    # Step 5: Generate and send reply
                    generated_reply, reply_attachments = rag_reply_generator_agent.generate_reply(parsed_email, classification, extracted_data)
                    # Create result
                    result = {
                        'email_id': parsed_email.message_id,
                        'parsed_email': parsed_email.dict(),
                        'classification': classification.dict(),
                        'extracted_data': extracted_data.dict(),
                        'ledger_entry': ledger_entry,
                        'generated_reply': generated_reply.dict(),
                        'reply_attachments': reply_attachments,
                        'processing_timestamp': datetime.now(),
                        'pipeline_status': 'completed'
                    }
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing email in batch: {e}")
                    continue
            logger.info(f"Batch processing completed: {len(results)} emails processed")
            return results
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return []
    
    def get_pipeline_stats(self):
        """Get comprehensive pipeline statistics"""
        try:
            stats = {
                'total_emails': len(mongo_client.get_all_emails()),
                'total_transactions': len(mongo_client.get_all_transactions()),
                'classification_stats': content_classifier_agent.get_classification_stats(),
                'extraction_stats': data_extractor_agent.get_extraction_stats(),
                'mapping_stats': ledger_mapper_agent.get_mapping_stats(),
                'reply_stats': rag_reply_generator_agent.get_reply_stats()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting pipeline stats: {e}")
            return {}
    
    def export_ledger_entries(self, filename="ledger_entries.csv"):
        """Export ledger entries to CSV"""
        return ledger_mapper_agent.export_to_csv(filename)
    
    def test_pipeline(self):
        """Test the pipeline with sample data"""
        try:
            logger.info("Testing pipeline with sample data...")
            
            # Create sample email data
            sample_email = {
                'subject': 'Invoice #INV-2024-001',
                'from': 'vendor@example.com',
                'to': 'finance@company.com',
                'date': '2024-01-15',
                'message_id': 'test-001',
                'body': 'Please find attached invoice for services rendered. Amount: $1,500.00. Due date: 2024-02-15.',
                'attachments': []
            }
            
            # Process sample email
            result = self.process_single_email(sample_email)
            
            logger.info("Pipeline test completed")
            return result
            
        except Exception as e:
            logger.error(f"Error testing pipeline: {e}")
            return None

# Global orchestrator instance
orchestrator = FinanceAgentOrchestrator() 