import logging
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import re
from email.utils import parseaddr

from database.mongo_client import mongo_client
from config import Config

logger = logging.getLogger(__name__)

class LedgerEntry(BaseModel):
    """Ledger entry model"""
    gl_code: str = Field(description="General Ledger code")
    account_name: str = Field(description="Account name")
    account_type: str = Field(description="Account type (Asset, Liability, Equity, Revenue, Expense)")
    debit_amount: Optional[float] = Field(description="Debit amount")
    credit_amount: Optional[float] = Field(description="Credit amount")
    description: str = Field(description="Transaction description")
    reference: Optional[str] = Field(description="Reference number")
    date: str = Field(description="Transaction date")
    vendor_payee: Optional[str] = Field(description="Vendor or payee name")
    category: str = Field(description="Transaction category")
    confidence_score: float = Field(description="Mapping confidence score (0-1)")
    mapping_rules_applied: List[str] = Field(description="Rules applied for mapping")
    timestamp: datetime = Field(description="Mapping timestamp")

class LedgerMapperAgent:
    def __init__(self):
        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.1
        )
        self.output_parser = PydanticOutputParser(pydantic_object=LedgerEntry)
        
        # Standard GL codes and account mappings
        self.gl_mappings = {
            'accounts_payable': {
                'gl_code': '2100',
                'account_name': 'Accounts Payable',
                'account_type': 'Liability'
            },
            'accounts_receivable': {
                'gl_code': '1100',
                'account_name': 'Accounts Receivable',
                'account_type': 'Asset'
            },
            'cash': {
                'gl_code': '1000',
                'account_name': 'Cash',
                'account_type': 'Asset'
            },
            'expenses': {
                'gl_code': '5000',
                'account_name': 'Operating Expenses',
                'account_type': 'Expense'
            },
            'revenue': {
                'gl_code': '4000',
                'account_name': 'Revenue',
                'account_type': 'Revenue'
            },
            'bank_charges': {
                'gl_code': '5200',
                'account_name': 'Bank Charges',
                'account_type': 'Expense'
            },
            'utilities': {
                'gl_code': '5300',
                'account_name': 'Utilities',
                'account_type': 'Expense'
            },
            'office_supplies': {
                'gl_code': '5400',
                'account_name': 'Office Supplies',
                'account_type': 'Expense'
            }
        }
        
        self.mapping_prompt = PromptTemplate(
            input_variables=["extracted_data", "classification"],
            template="""
            You are an expert accounting ledger mapper. Map the following financial transaction to the appropriate ledger entry.
            
            Transaction Classification: {classification}
            Extracted Data: {extracted_data}
            
            Map to appropriate:
            1. GL Code (General Ledger code)
            2. Account Name
            3. Account Type (Asset, Liability, Equity, Revenue, Expense)
            4. Debit/Credit amounts
            5. Transaction description
            6. Category
            
            Consider:
            - Transaction type (Invoice, Payment, Expense, Revenue)
            - Amount and direction (debit/credit)
            - Vendor/Payee information
            - Industry standards for GL codes
            
            Return structured ledger entry.
            """
        )
    
    def determine_account_type(self, classification, amount, vendor_name):
        """Determine account type based on classification and context"""
        classification_lower = classification.lower()
        
        if 'invoice' in classification_lower:
            return 'accounts_payable'
        elif 'payment' in classification_lower and 'confirmation' in classification_lower:
            return 'cash'
        elif 'expense' in classification_lower:
            return 'expenses'
        elif 'revenue' in classification_lower or 'income' in classification_lower:
            return 'revenue'
        elif 'bank' in classification_lower:
            return 'bank_charges'
        else:
            # Default based on amount direction
            return 'expenses' if amount else 'accounts_payable'
    
    def map_to_ledger(self, extracted_data, classification, parsed_email=None):
        """Map extracted data to custom ledger entry format for dashboard display."""
        try:
            logger.info(f"Mapping transaction to ledger: {extracted_data.description}")
            # Dynamically determine type from subject/body
            type_keywords = ['invoice', 'bill', 'expense', 'quotation']
            type_value = ''
            subject = parsed_email.subject.lower() if parsed_email and hasattr(parsed_email, 'subject') else ''
            body = parsed_email.body_text.lower() if parsed_email and hasattr(parsed_email, 'body_text') else ''
            for keyword in type_keywords:
                if keyword in subject or keyword in body:
                    type_value = keyword.capitalize()
                    break
            if not type_value:
                type_value = classification.primary_intent.capitalize() if classification.primary_intent else ''
            # Vendor/Customer
            vendor_customer = extracted_data.vendor_name or extracted_data.payer_name or ''
            # Description as subject
            description = parsed_email.subject if parsed_email else extracted_data.description
            # Mail ID (just the email address)
            mail_id = ''
            if parsed_email and hasattr(parsed_email, 'sender'):
                mail_id = parseaddr(parsed_email.sender)[1]
            # Date (format as dd/mm/yy)
            date_raw = extracted_data.transaction_date or (parsed_email.date if parsed_email else '')
            date_fmt = ''
            if date_raw:
                try:
                    from dateutil import parser
                    dt = parser.parse(date_raw)
                    date_fmt = dt.strftime('%d/%m/%y')
                except Exception:
                    date_fmt = date_raw[:10]  # fallback to first 10 chars
            # Amount logic
            credit = debit = ''
            if type_value in ['Invoice', 'Quotation']:
                credit = extracted_data.amount or ''
            elif type_value in ['Bill', 'Expense']:
                debit = extracted_data.amount or ''
            ledger_entry = {
                'Date': date_fmt,
                'Mail ID': mail_id,
                'Type': type_value,
                'Description': description,
                'Vendor / Customer': vendor_customer,
                'Debit': debit,
                'Credit': credit,
            }
            ledger_doc = {
                'email_id': extracted_data.extraction_timestamp,
                'ledger_entry': ledger_entry,
                'extracted_data': extracted_data.dict(),
                'classification': classification.dict(),
                'mapping_timestamp': datetime.now(),
                'agent_version': '1.0'
            }
            mongo_client.insert_transaction(ledger_doc)
            logger.info(f"Ledger entry mapped successfully.")
            return ledger_entry
        except Exception as e:
            logger.error(f"Error mapping to ledger: {e}")
            raise
    
    def fallback_mapping(self, extracted_data, classification):
        """Fallback mapping when LLM fails"""
        amount = extracted_data.amount or 0
        account_type = self.determine_account_type(
            classification.primary_intent,
            amount,
            extracted_data.vendor_name
        )
        
        account_info = self.gl_mappings.get(account_type, self.gl_mappings['expenses'])
        
        # Determine debit/credit based on account type
        if account_info['account_type'] in ['Asset', 'Expense']:
            debit_amount = amount
            credit_amount = None
        else:
            debit_amount = None
            credit_amount = amount
        
        return LedgerEntry(
            gl_code=account_info['gl_code'],
            account_name=account_info['account_name'],
            account_type=account_info['account_type'],
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            description=extracted_data.description or "Transaction",
            reference=extracted_data.invoice_number,
            date=extracted_data.transaction_date or datetime.now().strftime("%Y-%m-%d"),
            vendor_payee=extracted_data.vendor_name,
            category=extracted_data.category,
            confidence_score=0.6,
            mapping_rules_applied=["fallback_mapping"],
            timestamp=datetime.now()
        )
    
    def map_batch(self, extracted_data_list, classifications):
        """Map a batch of extracted data to ledger entries"""
        ledger_entries = []
        
        for extracted_data, classification in zip(extracted_data_list, classifications):
            try:
                ledger_entry = self.map_to_ledger(extracted_data, classification)
                ledger_entries.append(ledger_entry)
            except Exception as e:
                logger.error(f"Failed to map transaction to ledger: {e}")
                continue
        
        logger.info(f"Successfully mapped {len(ledger_entries)} out of {len(extracted_data_list)} transactions")
        return ledger_entries
    
    def get_mapping_stats(self):
        """Get mapping statistics"""
        try:
            transactions = mongo_client.get_all_transactions()
            
            stats = {
                'total_mappings': len(transactions),
                'successful_mappings': 0,
                'average_confidence': 0.0,
                'account_type_distribution': {},
                'gl_code_distribution': {}
            }
            
            total_confidence = 0
            for transaction in transactions:
                if 'ledger_entry' in transaction:
                    ledger_entry = transaction['ledger_entry']
                    
                    if ledger_entry.get('gl_code'):
                        stats['successful_mappings'] += 1
                    
                    confidence = ledger_entry.get('confidence_score', 0)
                    total_confidence += confidence
                    
                    account_type = ledger_entry.get('account_type', 'Unknown')
                    stats['account_type_distribution'][account_type] = stats['account_type_distribution'].get(account_type, 0) + 1
                    
                    gl_code = ledger_entry.get('gl_code', 'Unknown')
                    stats['gl_code_distribution'][gl_code] = stats['gl_code_distribution'].get(gl_code, 0) + 1
            
            if stats['total_mappings'] > 0:
                stats['average_confidence'] = total_confidence / stats['total_mappings']
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting mapping stats: {e}")
            return {}
    
    def export_to_csv(self, filename="ledger_entries.csv"):
        """Export ledger entries to CSV"""
        try:
            import pandas as pd
            
            transactions = mongo_client.get_all_transactions()
            ledger_data = []
            
            for transaction in transactions:
                if 'ledger_entry' in transaction:
                    ledger_entry = transaction['ledger_entry']
                    ledger_data.append({
                        'Date': ledger_entry.get('date', ''),
                        'GL_Code': ledger_entry.get('gl_code', ''),
                        'Account_Name': ledger_entry.get('account_name', ''),
                        'Account_Type': ledger_entry.get('account_type', ''),
                        'Debit': ledger_entry.get('debit_amount', ''),
                        'Credit': ledger_entry.get('credit_amount', ''),
                        'Description': ledger_entry.get('description', ''),
                        'Reference': ledger_entry.get('reference', ''),
                        'Vendor_Payee': ledger_entry.get('vendor_payee', ''),
                        'Category': ledger_entry.get('category', ''),
                        'Confidence': ledger_entry.get('confidence_score', '')
                    })
            
            df = pd.DataFrame(ledger_data)
            df.to_csv(filename, index=False)
            logger.info(f"Ledger entries exported to {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return None

# Global ledger mapper agent instance
ledger_mapper_agent = LedgerMapperAgent() 