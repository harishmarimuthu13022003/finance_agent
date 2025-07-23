import logging
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import json

from database.mongo_client import mongo_client
from config import Config

logger = logging.getLogger(__name__)

class EmailClassification(BaseModel):
    """Email classification model"""
    primary_intent: str = Field(description="Primary email intent (Invoice, Payment, Alert, Request, etc.)")
    secondary_intent: Optional[str] = Field(description="Secondary intent if applicable")
    confidence_score: float = Field(description="Classification confidence score (0-1)")
    classification_reason: str = Field(description="Reason for classification")
    financial_relevance: bool = Field(description="Whether email is financially relevant")
    urgency_level: str = Field(description="Urgency level (Low, Medium, High, Critical)")
    tags: List[str] = Field(description="Additional tags for categorization")
    timestamp: datetime = Field(description="Classification timestamp")

class ContentClassifierAgent:
    def __init__(self):
        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.1
        )
        self.output_parser = PydanticOutputParser(pydantic_object=EmailClassification)
        
        self.classification_prompt = PromptTemplate(
            input_variables=["email_content"],
            template="""
            You are an expert financial email classifier. Analyze the following email and classify its intent and type.
            
            Email Content:
            {email_content}
            
            Classify the email based on:
            1. Primary Intent: Invoice, Payment Confirmation, Bank Alert, Payment Request, Vendor Communication, Client Communication, Financial Report, Expense Report, etc.
            2. Secondary Intent: If the email has multiple purposes
            3. Financial Relevance: Whether this email contains financial information
            4. Urgency Level: Low, Medium, High, Critical
            5. Tags: Additional categorization tags
            
            Consider:
            - Keywords in subject and body
            - Attachment types (invoices, receipts, etc.)
            - Sender domain and context
            - Financial terms and amounts mentioned
            - Time sensitivity indicators
            
            Return the classification in structured format.
            """
        )
    
    def classify_email(self, parsed_email):
        """Classify email content and determine intent"""
        try:
            logger.info(f"Classifying email: {parsed_email.subject}")
            
            # Prepare email content for classification
            email_content = {
                'subject': parsed_email.subject,
                'sender': parsed_email.sender,
                'body': parsed_email.body_text,
                'attachments': [att.get('filename', '') for att in parsed_email.attachments],
                'attachment_texts': [att.get('extracted_text', '') for att in parsed_email.attachments]
            }
            
            # Use LLM for classification
            chain = self.classification_prompt | self.llm | self.output_parser
            
            try:
                classification = chain.invoke({"email_content": json.dumps(email_content, indent=2)})
            except Exception as e:
                logger.warning(f"LLM classification failed, using fallback: {e}")
                classification = self.fallback_classification(parsed_email)
            
            # Store classification in MongoDB
            classification_doc = {
                'email_id': parsed_email.message_id,
                'classification': classification.dict(),
                'parsed_email': parsed_email.dict(),
                'classification_timestamp': datetime.now(),
                'agent_version': '1.0'
            }
            
            mongo_client.insert_email(classification_doc)
            logger.info(f"Email classified successfully: {classification.primary_intent}")
            
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            raise
    
    def fallback_classification(self, parsed_email):
        """Fallback classification when LLM fails"""
        subject_lower = parsed_email.subject.lower()
        body_lower = parsed_email.body_text.lower()
        
        # Simple keyword-based classification
        if any(word in subject_lower or word in body_lower for word in ['invoice', 'bill', 'payment due']):
            primary_intent = "Invoice"
            financial_relevance = True
            urgency_level = "Medium"
        elif any(word in subject_lower or word in body_lower for word in ['payment', 'paid', 'confirmation']):
            primary_intent = "Payment Confirmation"
            financial_relevance = True
            urgency_level = "Low"
        elif any(word in subject_lower or word in body_lower for word in ['alert', 'warning', 'urgent']):
            primary_intent = "Alert"
            financial_relevance = True
            urgency_level = "High"
        else:
            primary_intent = "General Communication"
            financial_relevance = False
            urgency_level = "Low"
        
        return EmailClassification(
            primary_intent=primary_intent,
            secondary_intent=None,
            confidence_score=0.6,
            classification_reason="Fallback keyword-based classification",
            financial_relevance=financial_relevance,
            urgency_level=urgency_level,
            tags=["fallback_classification"],
            timestamp=datetime.now()
        )
    
    def classify_batch(self, parsed_emails):
        """Classify a batch of parsed emails"""
        classifications = []
        
        for parsed_email in parsed_emails:
            try:
                classification = self.classify_email(parsed_email)
                classifications.append(classification)
            except Exception as e:
                logger.error(f"Failed to classify email: {e}")
                continue
        
        logger.info(f"Successfully classified {len(classifications)} out of {len(parsed_emails)} emails")
        return classifications
    
    def get_classification_stats(self):
        """Get classification statistics"""
        try:
            emails = mongo_client.get_all_emails()
            
            stats = {
                'total_emails': len(emails),
                'intent_distribution': {},
                'financial_relevance_count': 0,
                'urgency_distribution': {}
            }
            
            for email in emails:
                if 'classification' in email:
                    classification = email['classification']
                    
                    # Intent distribution
                    primary_intent = classification.get('primary_intent', 'Unknown')
                    stats['intent_distribution'][primary_intent] = stats['intent_distribution'].get(primary_intent, 0) + 1
                    
                    # Financial relevance
                    if classification.get('financial_relevance', False):
                        stats['financial_relevance_count'] += 1
                    
                    # Urgency distribution
                    urgency = classification.get('urgency_level', 'Unknown')
                    stats['urgency_distribution'][urgency] = stats['urgency_distribution'].get(urgency, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting classification stats: {e}")
            return {}

# Global content classifier agent instance
content_classifier_agent = ContentClassifierAgent() 