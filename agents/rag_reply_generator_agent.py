import logging
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os

from database.mongo_client import mongo_client
from config import Config
from utils.pdf_invoice_generator import generate_invoice_pdf
from utils.email_utils import gmail_client
import re
from email.utils import parseaddr

logger = logging.getLogger(__name__)

class GeneratedReply(BaseModel):
    """Generated reply model"""
    reply_subject: str = Field(description="Reply subject line")
    reply_body: str = Field(description="Reply body content")
    reply_type: str = Field(description="Type of reply (Request, Confirmation, Follow-up, etc.)")
    missing_fields: List[str] = Field(description="List of missing fields that need clarification")
    policy_references: List[str] = Field(description="Policy references included in reply")
    tone: str = Field(description="Reply tone (Professional, Friendly, Formal, etc.)")
    urgency_level: str = Field(description="Urgency level of reply")
    confidence_score: float = Field(description="Reply generation confidence score (0-1)")
    generation_timestamp: datetime = Field(description="Generation timestamp")

class RAGReplyGeneratorAgent:
    def __init__(self):
        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.3
        )
        self.output_parser = PydanticOutputParser(pydantic_object=GeneratedReply)
        
        # Initialize embeddings
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=Config.GOOGLE_API_KEY
            )
        except:
            logger.warning("Google AI embeddings not available, using fallback")
            self.embeddings = None
        
        # Initialize vector store
        self.vector_store = None
        self.initialize_knowledge_base()
        
        self.reply_prompt = PromptTemplate(
            input_variables=["email_content", "classification", "extracted_data", "rag_context", "missing_fields"],
            template="""
            You are an expert financial communication assistant. Generate a professional reply to the following email.
            
            Original Email Classification: {classification}
            Extracted Data: {extracted_data}
            Missing Fields: {missing_fields}
            Relevant Context from Knowledge Base: {rag_context}
            
            Generate a reply that:
            1. Addresses the email appropriately
            2. Requests missing information if needed
            3. References relevant company policies
            4. Maintains professional tone
            5. Includes clear next steps
            
            Consider:
            - Email type and urgency
            - Missing required information
            - Company policies and procedures
            - Professional communication standards
            
            Return structured reply with subject and body.
            """
        )
    
    def initialize_knowledge_base(self):
        """Initialize the knowledge base with company templates and policies"""
        try:
            # Create sample templates and policies
            self.create_sample_templates()
            
            # Load templates from MongoDB
            templates = mongo_client.get_templates_by_type("policy")
            
            if templates and self.embeddings:
                # Create vector store from templates
                documents = []
                for template in templates:
                    doc_text = f"Title: {template.get('title', '')}\nContent: {template.get('content', '')}\nType: {template.get('type', '')}"
                    documents.append(doc_text)
                
                if documents:
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    texts = text_splitter.create_documents(documents)
                    
                    self.vector_store = FAISS.from_documents(texts, self.embeddings)
                    logger.info("Knowledge base initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
    
    def create_sample_templates(self):
        """Create sample response templates"""
        sample_templates = [
            {
                'title': 'Invoice Processing Policy',
                'content': 'All invoices must include vendor name, amount, invoice number, and due date. Missing information will delay processing.',
                'type': 'policy',
                'category': 'invoice'
            },
            {
                'title': 'Payment Confirmation Template',
                'content': 'Thank you for your payment. We have received your payment of {amount} for invoice {invoice_number}. Your account has been updated accordingly.',
                'type': 'template',
                'category': 'payment'
            },
            {
                'title': 'Missing Information Request',
                'content': 'We require the following information to process your request: {missing_fields}. Please provide this information within 3 business days.',
                'type': 'template',
                'category': 'request'
            },
            {
                'title': 'Vendor Registration Policy',
                'content': 'New vendors must complete vendor registration form and provide tax identification number before any payments can be processed.',
                'type': 'policy',
                'category': 'vendor'
            }
        ]
        
        for template in sample_templates:
            try:
                mongo_client.insert_template(template)
            except Exception as e:
                logger.error(f"Error inserting template: {e}")
    
    def retrieve_relevant_context(self, email_content, classification):
        """Retrieve relevant context from knowledge base using RAG"""
        try:
            if not self.vector_store:
                return "No knowledge base available"
            
            # Create query from email content and classification
            query = f"Email: {email_content}\nClassification: {classification}"
            
            # Search for relevant documents
            docs = self.vector_store.similarity_search(query, k=3)
            
            # Combine relevant context
            context = "\n".join([doc.page_content for doc in docs])
            
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return "Context retrieval failed"
    
    def identify_missing_fields(self, extracted_data, classification):
        """No longer used: always send reply with available fields."""
        return []

    def generate_reply(self, parsed_email, classification, extracted_data):
        """Generate contextual reply using RAG. Always send reply with available fields, no required field checks. Also send the reply email to the sender."""
        try:
            logger.info(f"Generating reply for email: {parsed_email.subject}")
            missing_fields = []
            email_content = f"Subject: {parsed_email.subject}\nBody: {parsed_email.body_text}"
            rag_context = self.retrieve_relevant_context(email_content, classification.primary_intent)
            reply_data = {
                'email_content': email_content,
                'classification': classification.primary_intent,
                'extracted_data': extracted_data.dict(),
                'rag_context': rag_context,
                'missing_fields': missing_fields
            }
            chain = self.reply_prompt | self.llm | self.output_parser
            try:
                generated_reply = chain.invoke(reply_data)
            except Exception as e:
                logger.warning(f"LLM reply generation failed, using fallback: {e}")
                generated_reply = self.fallback_reply(parsed_email, classification, extracted_data, missing_fields)
            attachments = []
            if classification.primary_intent == "Invoice":
                invoice_data = self.prepare_invoice_data(parsed_email, extracted_data)
                pdf_bytes = generate_invoice_pdf(invoice_data)
                pdf_filename = f"{invoice_data['invoice_number']}_{invoice_data['billed_to_name'].replace(' ', '_')}.pdf"
                attachments.append({
                    'filename': pdf_filename,
                    'content_type': 'application/pdf',
                    'data': pdf_bytes
                })
            # Extract just the email address from the sender field
            to_email = parseaddr(parsed_email.sender)[1]
            subject = generated_reply.reply_subject
            body = generated_reply.reply_body

            # If you want to send HTML, use 'html' instead of 'plain'
            email_sent = gmail_client.send_email(to_email, subject, body, attachments=attachments)
            if email_sent:
                logger.info(f"Reply email sent successfully to {to_email}")
            else:
                logger.error(f"Failed to send reply email to {to_email}")
            # Store generated reply in MongoDB (with attachments)
            reply_doc = {
                'email_id': parsed_email.message_id,
                'generated_reply': generated_reply.dict(),
                'parsed_email': parsed_email.dict(),
                'classification': classification.dict(),
                'extracted_data': extracted_data.dict(),
                'attachments': attachments,
                'generation_timestamp': datetime.now(),
                'agent_version': '1.0'
            }
            mongo_client.insert_response(reply_doc)
            logger.info(f"Reply generated and sent successfully")
            return generated_reply, attachments
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            raise
    def prepare_invoice_data(self, parsed_email, extracted_data):
        """Prepare invoice data dict for PDF generation from extracted data and email context"""
        # This should be customized to your org's details or loaded from config
        return {
            'company_name': 'Your Company Name',
            'company_address': '123 Business Lane, City, State - ZIP',
            'company_phone': '+91-XXXXXXXXXX',
            'company_email': 'billing@yourcompany.com',
            'company_gstin': '29ABCDE1234F1Z5',
            'invoice_number': extracted_data.invoice_number or 'INV-XXXX',
            'invoice_date': parsed_email.date or datetime.now().strftime('%Y-%m-%d'),
            'due_date': extracted_data.due_date or '',
            'billed_to_name': extracted_data.vendor_name or '',
            'billed_to_address': '3rd Floor, Tech Park, Bangalore - 560102',
            'billed_to_gstin': '29XYZ9876L1A9',
            'description': extracted_data.description or 'Consulting Services',
            'quantity': 1,
            'rate': int(extracted_data.amount or 0),
            'subtotal': int(extracted_data.amount or 0),
            'gst_percent': 18,
            'gst_amount': int((extracted_data.amount or 0) * 0.18),
            'total_amount': int((extracted_data.amount or 0) * 1.18),
            'bank_name': 'HDFC Bank',
            'account_name': 'Your Company Name',
            'account_no': 'XXXXXXXX',
            'ifsc_code': 'HDFC000XXXX',
        }
    
    def fallback_reply(self, parsed_email, classification, extracted_data, missing_fields):
        """Fallback reply generation when LLM fails"""
        subject = f"Re: {parsed_email.subject}"
        
        if missing_fields:
            body = f"Thank you for your email. To process your request, we need the following information: {', '.join(missing_fields)}. Please provide this information at your earliest convenience."
            reply_type = "Request"
        elif classification.primary_intent == "Invoice":
            body = "Thank you for your invoice. We have received it and it is being processed according to our standard procedures."
            reply_type = "Confirmation"
        elif classification.primary_intent == "Payment Confirmation":
            body = "Thank you for your payment. We have received your payment and your account has been updated."
            reply_type = "Confirmation"
        else:
            body = "Thank you for your email. We have received your message and will respond accordingly."
            reply_type = "Acknowledgment"
        
        return GeneratedReply(
            reply_subject=subject,
            reply_body=body,
            reply_type=reply_type,
            missing_fields=missing_fields,
            policy_references=[],
            tone="Professional",
            urgency_level="Normal",
            confidence_score=0.7,
            generation_timestamp=datetime.now()
        )
    
    def generate_batch_replies(self, parsed_emails, classifications, extracted_data_list):
        """Generate replies for a batch of emails"""
        generated_replies = []
        
        for parsed_email, classification, extracted_data in zip(parsed_emails, classifications, extracted_data_list):
            try:
                reply, attachments = self.generate_reply(parsed_email, classification, extracted_data)
                generated_replies.append(reply)
            except Exception as e:
                logger.error(f"Failed to generate reply: {e}")
                continue
        
        logger.info(f"Successfully generated {len(generated_replies)} out of {len(parsed_emails)} replies")
        return generated_replies
    
    def get_reply_stats(self):
        """Get reply generation statistics"""
        try:
            responses = mongo_client.get_all_transactions()  # Assuming responses are stored in transactions collection
            
            stats = {
                'total_replies': len(responses),
                'successful_replies': 0,
                'average_confidence': 0.0,
                'reply_type_distribution': {},
                'missing_fields_distribution': {}
            }
            
            total_confidence = 0
            for response in responses:
                if 'generated_reply' in response:
                    reply = response['generated_reply']
                    
                    if reply.get('reply_body'):
                        stats['successful_replies'] += 1
                    
                    confidence = reply.get('confidence_score', 0)
                    total_confidence += confidence
                    
                    reply_type = reply.get('reply_type', 'Unknown')
                    stats['reply_type_distribution'][reply_type] = stats['reply_type_distribution'].get(reply_type, 0) + 1
                    
                    missing_fields = reply.get('missing_fields', [])
                    for field in missing_fields:
                        stats['missing_fields_distribution'][field] = stats['missing_fields_distribution'].get(field, 0) + 1
            
            if stats['total_replies'] > 0:
                stats['average_confidence'] = total_confidence / stats['total_replies']
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting reply stats: {e}")
            return {}

    def send_reply_for_email(self, parsed_email, classification, extracted_data):
        """Send the reply email for a specific email, using the same logic as generate_reply."""
        try:
            generated_reply, attachments = self.generate_reply(parsed_email, classification, extracted_data)
            return generated_reply, attachments
        except Exception as e:
            logger.error(f"Error sending reply for email: {e}")
            raise

# Global RAG reply generator agent instance
rag_reply_generator_agent = RAGReplyGeneratorAgent() 