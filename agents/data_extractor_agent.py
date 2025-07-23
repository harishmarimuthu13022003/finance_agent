import logging
import re
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from database.mongo_client import mongo_client
from config import Config

logger = logging.getLogger(__name__)

class ExtractedData(BaseModel):
    """Extracted financial data model"""
    amount: Optional[float] = Field(description="Financial amount extracted")
    currency: Optional[str] = Field(description="Currency code (USD, INR, EUR, etc.)")
    vendor_name: Optional[str] = Field(description="Vendor or payee name")
    payer_name: Optional[str] = Field(description="Payer name")
    invoice_number: Optional[str] = Field(description="Invoice or reference number")
    payment_terms: Optional[str] = Field(description="Payment terms (Net 30, etc.)")
    due_date: Optional[str] = Field(description="Payment due date")
    transaction_date: Optional[str] = Field(description="Transaction date")
    description: Optional[str] = Field(description="Transaction description")
    category: Optional[str] = Field(description="Transaction category")
    confidence_score: float = Field(description="Extraction confidence score (0-1)")
    uncertain_fields: List[str] = Field(description="Fields with uncertain extraction")
    extraction_timestamp: datetime = Field(description="Extraction timestamp")

class DataExtractorAgent:
    def __init__(self):
        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.1
        )
        self.output_parser = PydanticOutputParser(pydantic_object=ExtractedData)
        
        self.extraction_prompt = PromptTemplate(
            input_variables=["email_content", "classification"],
            template="""
            You are an expert financial data extractor. Extract structured financial information from the following email content.
            
            Email Classification: {classification}
            Email Content: {email_content}
            
            Extract the following financial data:
            1. Amount (numerical value)
            2. Currency (USD, INR, EUR, etc.)
            3. Vendor/Customer name
            4. Payer name
            5. Invoice/Reference number
            6. Payment terms
            7. Due date
            8. Transaction date
            9. Description
            10. Category
            11. Quotation number
            12. Bill number
            13.Bill
            
            Handle:
            - Multiple currencies and formats
            - Partial or unclear information
            - Regional date formats
            - Various invoice formats
            
            For uncertain fields, mark them as uncertain and provide best guess.
            Return structured JSON with extracted data.
            """
        )
    
    def extract_amount(self, text):
        """Extract amount using regex patterns"""
        # Common currency patterns
        patterns = [
            r'[\$₹€£¥]\s*([\d,]+\.?\d*)',  # Currency symbols
            r'([\d,]+\.?\d*)\s*[\$₹€£¥]',  # Amount followed by currency
            r'Amount[:\s]*([\d,]+\.?\d*)',  # Amount keyword
            r'Total[:\s]*([\d,]+\.?\d*)',   # Total keyword
            r'Due[:\s]*([\d,]+\.?\d*)',     # Due keyword
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def extract_currency(self, text):
        """Extract currency from text"""
        currency_patterns = {
            r'\$': 'USD',
            r'₹': 'INR',
            r'€': 'EUR',
            r'£': 'GBP',
            r'¥': 'JPY',
            r'USD': 'USD',
            r'INR': 'INR',
            r'EUR': 'EUR',
            r'GBP': 'GBP',
        }
        
        for pattern, currency in currency_patterns.items():
            if re.search(pattern, text):
                return currency
        
        return None
    
    def extract_vendor_name(self, text, sender):
        """Extract vendor name from text and sender"""
        # Common vendor indicators
        vendor_keywords = ['vendor', 'supplier', 'company', 'ltd', 'inc', 'corp']
        
        # Extract from sender email
        if '@' in sender:
            domain = sender.split('@')[1]
            company_name = domain.split('.')[0].title()
            return company_name
        
        # Look for company names in text
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in vendor_keywords):
                return line.strip()
        
        return None
    
    def extract_data(self, parsed_email, classification):
        """Extract structured financial data from email"""
        try:
            logger.info(f"Extracting data from email: {parsed_email.subject}")
            
            # Combine email body and attachment text
            full_text = parsed_email.body_text
            for attachment in parsed_email.attachments:
                if attachment.get('extracted_text'):
                    full_text += "\n" + attachment.get('extracted_text', '')
            
            # Prepare content for LLM
            email_content = {
                'subject': parsed_email.subject,
                'sender': parsed_email.sender,
                'body': parsed_email.body_text,
                'full_text': full_text,
                'attachments': [att.get('filename', '') for att in parsed_email.attachments]
            }
            
            # Use LLM for extraction
            chain = self.extraction_prompt | self.llm | self.output_parser
            
            try:
                extracted_data = chain.invoke({
                    "email_content": json.dumps(email_content, indent=2),
                    "classification": classification.primary_intent
                })
            except Exception as e:
                logger.warning(f"LLM extraction failed, using fallback: {e}")
                extracted_data = self.fallback_extraction(parsed_email, classification)
            
            # Store extracted data in MongoDB
            extraction_doc = {
                'email_id': parsed_email.message_id,
                'extracted_data': extracted_data.dict(),
                'parsed_email': parsed_email.dict(),
                'classification': classification.dict(),
                'extraction_timestamp': datetime.now(),
                'agent_version': '1.0'
            }
            
            mongo_client.insert_transaction(extraction_doc)
            logger.info(f"Data extracted successfully")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            raise
    
    def fallback_extraction(self, parsed_email, classification):
        """Fallback extraction when LLM fails"""
        full_text = parsed_email.body_text
        for attachment in parsed_email.attachments:
            if attachment.get('extracted_text'):
                full_text += "\n" + attachment.get('extracted_text', '')
        
        # Basic extraction using regex
        amount = self.extract_amount(full_text)
        currency = self.extract_currency(full_text)
        vendor_name = self.extract_vendor_name(full_text, parsed_email.sender)
        
        # Extract invoice number
        invoice_match = re.search(r'Invoice[:\s]*([A-Z0-9-]+)', full_text, re.IGNORECASE)
        invoice_number = invoice_match.group(1) if invoice_match else None
        
        # Extract due date
        date_match = re.search(r'Due[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', full_text, re.IGNORECASE)
        due_date = date_match.group(1) if date_match else None
        
        return ExtractedData(
            amount=amount,
            currency=currency,
            vendor_name=vendor_name,
            payer_name=None,
            invoice_number=invoice_number,
            payment_terms=None,
            due_date=due_date,
            transaction_date=None,
            description=parsed_email.subject,
            category=classification.primary_intent,
            confidence_score=0.5,
            uncertain_fields=['payer_name', 'payment_terms', 'transaction_date'] if not amount else [],
            extraction_timestamp=datetime.now()
        )
    
    def extract_batch(self, parsed_emails, classifications):
        """Extract data from a batch of emails"""
        extracted_data = []
        
        for parsed_email, classification in zip(parsed_emails, classifications):
            try:
                data = self.extract_data(parsed_email, classification)
                extracted_data.append(data)
            except Exception as e:
                logger.error(f"Failed to extract data from email: {e}")
                continue
        
        logger.info(f"Successfully extracted data from {len(extracted_data)} out of {len(parsed_emails)} emails")
        return extracted_data
    
    def get_extraction_stats(self):
        """Get extraction statistics"""
        try:
            transactions = mongo_client.get_all_transactions()
            
            stats = {
                'total_transactions': len(transactions),
                'successful_extractions': 0,
                'average_confidence': 0.0,
                'currency_distribution': {},
                'category_distribution': {}
            }
            
            total_confidence = 0
            for transaction in transactions:
                if 'extracted_data' in transaction:
                    extracted_data = transaction['extracted_data']
                    
                    if extracted_data.get('amount'):
                        stats['successful_extractions'] += 1
                    
                    confidence = extracted_data.get('confidence_score', 0)
                    total_confidence += confidence
                    
                    currency = extracted_data.get('currency', 'Unknown')
                    stats['currency_distribution'][currency] = stats['currency_distribution'].get(currency, 0) + 1
                    
                    category = extracted_data.get('category', 'Unknown')
                    stats['category_distribution'][category] = stats['category_distribution'].get(category, 0) + 1
            
            if stats['total_transactions'] > 0:
                stats['average_confidence'] = total_confidence / stats['total_transactions']
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting extraction stats: {e}")
            return {}

# Global data extractor agent instance
data_extractor_agent = DataExtractorAgent() 