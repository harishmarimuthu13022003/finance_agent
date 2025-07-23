#!/usr/bin/env python3
"""
Sample Email Formats for Finance Agent Testing
"""

# Sample Email 1: Invoice Email
SAMPLE_INVOICE_EMAIL = {
    'subject': 'Invoice #INV-2024-001 - ABC Corporation Services',
    'from': 'accounts@abccorp.com',
    'to': 'finance@yourcompany.com',
    'date': '2024-01-15 10:30:00',
    'message_id': 'invoice-001@abccorp.com',
    'body': '''
Dear Finance Team,

Please find attached our invoice for the consulting services provided in December 2024.

Invoice Details:
- Invoice Number: INV-2024-001
- Amount: $2,500.00 USD
- Due Date: February 15, 2024
- Payment Terms: Net 30

Services Rendered:
- Financial Analysis Consulting
- Process Optimization
- Documentation Review

Please process this invoice according to your standard procedures.

Best regards,
ABC Corporation
Accounts Department
Phone: +1-555-0123
Email: accounts@abccorp.com
    ''',
    'attachments': [
        {
            'filename': 'INV-2024-001.pdf',
            'content_type': 'application/pdf',
            'data': b'%PDF-1.4\n...',  # Mock PDF data
            'extracted_text': '''
INVOICE
ABC Corporation
123 Business Street
New York, NY 10001

Invoice #: INV-2024-001
Date: January 15, 2024
Due Date: February 15, 2024

Bill To:
Your Company Inc.
456 Finance Avenue
Business City, BC 12345

Description:
- Financial Analysis Consulting: $1,500.00
- Process Optimization: $750.00
- Documentation Review: $250.00

Subtotal: $2,500.00
Tax: $0.00
Total: $2,500.00 USD

Payment Terms: Net 30
            '''
        }
    ]
}

# Sample Email 2: Payment Confirmation
SAMPLE_PAYMENT_CONFIRMATION = {
    'subject': 'Payment Confirmation - Invoice INV-2024-001',
    'from': 'payments@abccorp.com',
    'to': 'finance@yourcompany.com',
    'date': '2024-02-10 14:15:00',
    'message_id': 'payment-conf-001@abccorp.com',
    'body': '''
Dear Finance Team,

We have received your payment for invoice INV-2024-001.

Payment Details:
- Invoice Number: INV-2024-001
- Amount Paid: $2,500.00 USD
- Payment Date: February 10, 2024
- Payment Method: Bank Transfer
- Reference: PAY-2024-001

Your account has been updated accordingly. Thank you for your prompt payment.

Best regards,
ABC Corporation
Accounts Receivable
    ''',
    'attachments': []
}

# Sample Email 3: Bank Alert
SAMPLE_BANK_ALERT = {
    'subject': 'Bank Alert - Large Transaction Detected',
    'from': 'alerts@yourbank.com',
    'to': 'finance@yourcompany.com',
    'date': '2024-01-20 09:45:00',
    'message_id': 'bank-alert-001@yourbank.com',
    'body': '''
Dear Account Holder,

We have detected a large transaction on your business account.

Transaction Details:
- Date: January 20, 2024
- Amount: $15,000.00 USD
- Type: Outgoing Transfer
- Recipient: ABC Corporation
- Reference: INV-2024-001

If this transaction is not authorized, please contact us immediately.

Best regards,
Your Bank
Security Team
    ''',
    'attachments': []
}

# Sample Email 4: Vendor Registration Request
SAMPLE_VENDOR_REQUEST = {
    'subject': 'New Vendor Registration - XYZ Supplies Ltd',
    'from': 'procurement@xyzsupplies.com',
    'to': 'finance@yourcompany.com',
    'date': '2024-01-25 11:20:00',
    'message_id': 'vendor-reg-001@xyzsupplies.com',
    'body': '''
Dear Finance Department,

We would like to register as a vendor for your company.

Company Information:
- Company Name: XYZ Supplies Ltd
- Tax ID: 12-3456789
- Address: 789 Supply Street, Industrial City, IC 67890
- Contact: procurement@xyzsupplies.com
- Phone: +1-555-0456

Services Offered:
- Office Supplies
- IT Equipment
- Maintenance Services

Please provide us with your vendor registration form and requirements.

Best regards,
XYZ Supplies Ltd
Procurement Team
    ''',
    'attachments': [
        {
            'filename': 'vendor_profile.pdf',
            'content_type': 'application/pdf',
            'data': b'%PDF-1.4\n...',  # Mock PDF data
            'extracted_text': '''
VENDOR PROFILE
XYZ Supplies Ltd
789 Supply Street
Industrial City, IC 67890

Tax ID: 12-3456789
Business Type: Limited Liability Company
Established: 2010

Services:
- Office Supplies
- IT Equipment
- Maintenance Services

Certifications:
- ISO 9001:2015
- Environmental Management
            '''
        }
    ]
}

# Sample Email 5: Expense Report
SAMPLE_EXPENSE_REPORT = {
    'subject': 'Expense Report - Business Travel January 2024',
    'from': 'employee@yourcompany.com',
    'to': 'finance@yourcompany.com',
    'date': '2024-01-30 16:30:00',
    'message_id': 'expense-001@yourcompany.com',
    'body': '''
Hi Finance Team,

Please find my expense report for the business trip to New York in January 2024.

Expense Summary:
- Airfare: $450.00
- Hotel: $800.00 (4 nights)
- Meals: $320.00
- Transportation: $150.00
- Total: $1,720.00

All receipts are attached. Please process for reimbursement.

Thanks,
John Employee
Sales Department
    ''',
    'attachments': [
        {
            'filename': 'receipts.pdf',
            'content_type': 'application/pdf',
            'data': b'%PDF-1.4\n...',  # Mock PDF data
            'extracted_text': '''
EXPENSE RECEIPTS
Employee: John Employee
Trip: New York Business Trip
Date: January 15-19, 2024

Receipts:
1. Airfare - $450.00
2. Hotel - $800.00
3. Meals - $320.00
4. Transportation - $150.00

Total: $1,720.00
            '''
        }
    ]
}

# Sample Email 6: Payment Reminder
SAMPLE_PAYMENT_REMINDER = {
    'subject': 'Payment Reminder - Invoice INV-2024-001 Overdue',
    'from': 'collections@abccorp.com',
    'to': 'finance@yourcompany.com',
    'date': '2024-02-20 10:00:00',
    'message_id': 'reminder-001@abccorp.com',
    'body': '''
Dear Finance Team,

This is a friendly reminder that invoice INV-2024-001 is now overdue.

Invoice Details:
- Invoice Number: INV-2024-001
- Original Amount: $2,500.00 USD
- Due Date: February 15, 2024
- Days Overdue: 5 days

Please process this payment as soon as possible to avoid any late fees.

If you have already made the payment, please disregard this reminder.

Best regards,
ABC Corporation
Collections Department
    ''',
    'attachments': []
}

# Sample Email 7: Financial Report
SAMPLE_FINANCIAL_REPORT = {
    'subject': 'Monthly Financial Report - January 2024',
    'from': 'reports@yourcompany.com',
    'to': 'finance@yourcompany.com',
    'date': '2024-02-01 09:00:00',
    'message_id': 'report-001@yourcompany.com',
    'body': '''
Dear Finance Team,

Please find attached the monthly financial report for January 2024.

Key Highlights:
- Revenue: $125,000.00
- Expenses: $85,000.00
- Net Profit: $40,000.00
- Outstanding Receivables: $15,000.00
- Outstanding Payables: $8,000.00

The detailed report is attached for your review.

Best regards,
Accounting Department
    ''',
    'attachments': [
        {
            'filename': 'financial_report_jan2024.pdf',
            'content_type': 'application/pdf',
            'data': b'%PDF-1.4\n...',  # Mock PDF data
            'extracted_text': '''
MONTHLY FINANCIAL REPORT
January 2024

Revenue:
- Product Sales: $100,000.00
- Services: $25,000.00
Total Revenue: $125,000.00

Expenses:
- Salaries: $50,000.00
- Rent: $15,000.00
- Utilities: $5,000.00
- Supplies: $10,000.00
- Other: $5,000.00
Total Expenses: $85,000.00

Net Profit: $40,000.00
            '''
        }
    ]
}

# Sample Email 8: Utility Bill
SAMPLE_UTILITY_BILL = {
    'subject': 'Utility Bill - January 2024 - Account #12345',
    'from': 'billing@utilitycompany.com',
    'to': 'finance@yourcompany.com',
    'date': '2024-01-31 12:00:00',
    'message_id': 'utility-001@utilitycompany.com',
    'body': '''
Dear Customer,

Your utility bill for January 2024 is now available.

Bill Details:
- Account Number: 12345
- Billing Period: January 1-31, 2024
- Due Date: February 15, 2024
- Amount Due: $1,250.00

Breakdown:
- Electricity: $800.00
- Water: $300.00
- Gas: $150.00

Please pay by the due date to avoid late fees.

Best regards,
Utility Company
Billing Department
    ''',
    'attachments': [
        {
            'filename': 'utility_bill_jan2024.pdf',
            'content_type': 'application/pdf',
            'data': b'%PDF-1.4\n...',  # Mock PDF data
            'extracted_text': '''
UTILITY BILL
Account: 12345
Period: January 1-31, 2024
Due Date: February 15, 2024

Charges:
- Electricity: $800.00
- Water: $300.00
- Gas: $150.00

Total Amount Due: $1,250.00
            '''
        }
    ]
}

# Sample Email 9: Comprehensive Finance Officer Email
SAMPLE_FINANCE_OFFICER_EMAIL = {
    'subject': 'Q4 2024 Financial Review & Budget Approval Request - $2.5M Project',
    'from': 'cfo@techinnovate.com',
    'to': 'finance@yourcompany.com',
    'date': '2024-12-15 14:30:00',
    'message_id': 'finance-review-001@techinnovate.com',
    'body': '''
Dear Finance Team,

I hope this email finds you well. I'm writing to request your review and approval for our Q4 2024 financial performance and the upcoming Q1 2025 budget allocation.

**Q4 2024 Financial Summary:**
- Total Revenue: $8,750,000.00
- Operating Expenses: $5,200,000.00
- Net Profit: $3,550,000.00
- EBITDA Margin: 40.6%
- Cash Flow from Operations: $3,200,000.00

**Key Financial Metrics:**
- Accounts Receivable: $1,250,000.00 (45 days average)
- Accounts Payable: $850,000.00 (30 days average)
- Inventory Value: $2,100,000.00
- Capital Expenditures: $1,500,000.00

**Q1 2025 Budget Request:**
We're requesting approval for a new technology infrastructure project with the following breakdown:

1. **IT Infrastructure Upgrade:**
   - Server Hardware: $750,000.00
   - Software Licenses: $450,000.00
   - Network Equipment: $300,000.00
   - Subtotal: $1,500,000.00

2. **Marketing Campaign:**
   - Digital Advertising: $400,000.00
   - Content Creation: $200,000.00
   - Event Sponsorships: $300,000.00
   - Subtotal: $900,000.00

3. **Operational Expenses:**
   - Office Expansion: $100,000.00
   - Total Budget Request: $2,500,000.00

**Risk Assessment:**
- Expected ROI: 25% over 18 months
- Payback Period: 3.2 years
- Risk Level: Medium (mitigated by phased implementation)

**Vendor Information:**
- Primary Vendor: TechSolutions Inc.
- Contract Value: $1,200,000.00
- Payment Terms: 50% upfront, 50% upon completion
- Expected Timeline: 6 months

Please review the attached detailed financial analysis and provide your feedback by December 20th, 2024. I'm available for a meeting next week to discuss any concerns or questions.

Best regards,
Sarah Johnson
Chief Financial Officer
TechInnovate Inc.
Phone: +1-555-0123
Email: cfo@techinnovate.com

P.S. Please note that this budget request is time-sensitive as we need to secure vendor commitments before year-end.
    ''',
    'attachments': [
        {
            'filename': 'Q4_Financial_Review_2024.pdf',
            'content_type': 'application/pdf',
            'data': b'%PDF-1.4\n...',  # Mock PDF data
            'extracted_text': '''
Q4 2024 FINANCIAL REVIEW
TechInnovate Inc.

EXECUTIVE SUMMARY
Total Revenue: $8,750,000.00
Operating Expenses: $5,200,000.00
Net Profit: $3,550,000.00
EBITDA: $3,550,000.00

DETAILED BREAKDOWN

Revenue Streams:
- Product Sales: $6,500,000.00
- Services: $1,750,000.00
- Licensing: $500,000.00

Operating Expenses:
- Salaries & Benefits: $2,800,000.00
- Rent & Utilities: $450,000.00
- Marketing: $750,000.00
- Technology: $600,000.00
- Other: $600,000.00

Cash Flow Analysis:
- Operating Cash Flow: $3,200,000.00
- Investing Cash Flow: -$1,500,000.00
- Financing Cash Flow: $500,000.00
- Net Cash Flow: $2,200,000.00

Q1 2025 BUDGET REQUEST
Total Request: $2,500,000.00

Breakdown:
1. IT Infrastructure: $1,500,000.00
2. Marketing Campaign: $900,000.00
3. Operational: $100,000.00

Expected ROI: 25%
Payback Period: 3.2 years
            '''
        },
        {
            'filename': 'Vendor_Proposal_TechSolutions.pdf',
            'content_type': 'application/pdf',
            'data': b'%PDF-1.4\n...',  # Mock PDF data
            'extracted_text': '''
VENDOR PROPOSAL
TechSolutions Inc.

PROJECT SCOPE
IT Infrastructure Upgrade for TechInnovate Inc.

SERVICES INCLUDED:
1. Server Hardware Installation: $750,000.00
   - 50 High-performance servers
   - Storage arrays
   - Backup systems

2. Software Licenses: $450,000.00
   - Enterprise software packages
   - Security licenses
   - Support contracts

3. Network Equipment: $300,000.00
   - Switches and routers
   - Wireless infrastructure
   - Security appliances

TOTAL CONTRACT VALUE: $1,500,000.00

PAYMENT TERMS:
- 50% upfront: $750,000.00
- 50% upon completion: $750,000.00

TIMELINE: 6 months
            '''
        }
    ]
}

# Function to get all sample emails
def get_sample_emails():
    """Return all sample emails for testing"""
    return {
        'invoice': SAMPLE_INVOICE_EMAIL,
        'payment_confirmation': SAMPLE_PAYMENT_CONFIRMATION,
        'bank_alert': SAMPLE_BANK_ALERT,
        'vendor_request': SAMPLE_VENDOR_REQUEST,
        'expense_report': SAMPLE_EXPENSE_REPORT,
        'payment_reminder': SAMPLE_PAYMENT_REMINDER,
        'financial_report': SAMPLE_FINANCIAL_REPORT,
        'utility_bill': SAMPLE_UTILITY_BILL,
        'finance_officer': SAMPLE_FINANCE_OFFICER_EMAIL
    }

# Function to test email processing
def test_email_processing():
    """Test email processing with sample data"""
    try:
        from orchestrator import orchestrator
        
        print("🧪 Testing Email Processing with Sample Data")
        print("=" * 60)
        
        sample_emails = get_sample_emails()
        
        for email_type, email_data in sample_emails.items():
            print(f"\n📧 Processing {email_type.upper()} email...")
            
            try:
                result = orchestrator.process_single_email(email_data)
                
                if result and result.get('pipeline_status') == 'completed':
                    print(f"✅ {email_type} processed successfully!")
                    
                    # Show key extracted information
                    extracted_data = result.get('extracted_data', {})
                    classification = result.get('classification', {})
                    ledger_entry = result.get('ledger_entry', {})
                    
                    print(f"   Classification: {classification.get('primary_intent', 'Unknown')}")
                    print(f"   Amount: {extracted_data.get('amount', 'Not found')}")
                    print(f"   Vendor: {extracted_data.get('vendor_name', 'Not found')}")
                    # print(f"   GL Code: {ledger_entry.get('gl_code', 'Not found')}")
                    
                else:
                    print(f"❌ {email_type} processing failed")
                    
            except Exception as e:
                print(f"❌ Error processing {email_type}: {e}")
        
        print("\n🎉 Sample email processing test completed!")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")

if __name__ == "__main__":
    test_email_processing() 