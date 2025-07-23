import logging
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import json

from utils.email_utils import gmail_client
from utils.attachment_processor import attachment_processor
from database.mongo_client import mongo_client
from config import Config

logger = logging.getLogger(__name__)

class ParsedEmail(BaseModel):
    """Structured email data model"""
    subject: str = Field(description="Email subject")
    sender: str = Field(description="Email sender")
    recipient: str = Field(description="Email recipient")
    date: str = Field(description="Email date")
    message_id: str = Field(description="Email message ID")
    body_text: str = Field(description="Cleaned email body text")
    html_body: Optional[str] = Field(description="HTML body if available")
    attachments: List[dict] = Field(description="List of processed attachments")
    metadata: dict = Field(description="Additional metadata")
    timestamp: datetime = Field(description="Processing timestamp")

class EmailParserAgent:
    def __init__(self):
        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.1
        )
        self.output_parser = PydanticOutputParser(pydantic_object=ParsedEmail)
        
        self.parsing_prompt = PromptTemplate(
            input_variables=["email_content"],
            template="""
            You are an expert email parser. Parse the following email and extract structured information.
            
            Email Content:
            {email_content}
            
            Extract and structure the following information:
            1. Subject line
            2. Sender information
            3. Recipient information
            4. Date
            5. Message ID
            6. Clean body text (remove HTML tags, formatting)
            7. HTML body (if available)
            8. Any additional metadata
            
            Return the data in a structured JSON format.
            """
        )
    
    def clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove HTML tags
        import re
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # Remove special characters but keep basic punctuation
        clean_text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', '', clean_text)
        
        return clean_text.strip()
    
    def parse_email(self, email_data):
        """Parse email and extract structured information"""
        try:
            logger.info(f"Parsing email: {email_data.get('subject', 'No subject')}")
            
            # Process attachments first
            processed_attachments = attachment_processor.process_email_attachments(email_data)
            
            # Prepare email content for LLM processing
            email_content = {
                'subject': email_data.get('subject', ''),
                'from': email_data.get('from', ''),
                'to': email_data.get('to', ''),
                'date': email_data.get('date', ''),
                'message_id': email_data.get('message_id', ''),
                'body': email_data.get('body', ''),
                'attachments': processed_attachments
            }
            
            # Use LLM to extract structured information
            chain = self.parsing_prompt | self.llm | self.output_parser
            
            try:
                parsed_result = chain.invoke({"email_content": json.dumps(email_content, indent=2)})
            except Exception as e:
                logger.warning(f"LLM parsing failed, using fallback: {e}")
                parsed_result = self.fallback_parsing(email_data, processed_attachments)
            
            # Store in MongoDB
            email_doc = {
                'original_email': email_data,
                'parsed_email': parsed_result.dict(),
                'processed_attachments': processed_attachments,
                'processing_timestamp': datetime.now(),
                'agent_version': '1.0'
            }
            
            mongo_client.insert_email(email_doc)
            logger.info(f"Email parsed and stored successfully")
            
            return parsed_result
            
        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            raise
    
    def fallback_parsing(self, email_data, processed_attachments):
        """Fallback parsing when LLM fails"""
        return ParsedEmail(
            subject=email_data.get('subject', ''),
            sender=email_data.get('from', ''),
            recipient=email_data.get('to', ''),
            date=email_data.get('date', ''),
            message_id=email_data.get('message_id', ''),
            body_text=self.clean_text(email_data.get('body', '')),
            html_body=email_data.get('body', ''),
            attachments=processed_attachments,
            metadata={
                'parsing_method': 'fallback',
                'original_attachments_count': len(email_data.get('attachments', []))
            },
            timestamp=datetime.now()
        )
    
    def fetch_and_parse_emails(self, limit=50):
        """Fetch all unread emails from Gmail and parse them, including attachments."""
        try:
            emails = gmail_client.fetch_emails(limit=limit)
            parsed_emails = []
            for email_data in emails:
                try:
                    parsed_email = self.parse_email(email_data)
                    parsed_emails.append(parsed_email)
                    # Mark as read if processed
                    if 'imap_uid' in email_data:
                        gmail_client.mark_as_read(email_data['imap_uid'])
                except Exception as e:
                    logger.error(f"Failed to parse email: {e}")
                    continue
            logger.info(f"Successfully parsed {len(parsed_emails)} out of {len(emails)} emails (all unread)")
            return parsed_emails
        except Exception as e:
            logger.error(f"Error fetching and parsing emails: {e}")
            raise

# Global email parser agent instance
email_parser_agent = EmailParserAgent() 