from flask import Flask, request, jsonify
from database.mongo_client import mongo_client
from utils.email_utils import gmail_client
from utils.email_utils import send_confirmation_email
from utils.pdf_invoice_generator import generate_invoice_pdf
from agents.rag_reply_generator_agent import rag_reply_generator_agent

app = Flask(__name__)

@app.route('/confirm', methods=['GET'])
def confirm_transaction():
    transaction_id = request.args.get('transaction_id')
    if not transaction_id:
        return 'Missing transaction_id', 400
    # Find the transaction in the database
    transaction = mongo_client.get_transaction_by_mail_id(transaction_id)
    if not transaction:
        return 'Transaction not found', 404
    # Generate PDF invoice/quotation
    ledger_entry = transaction.get('ledger_entry', {})
    # You may need to map ledger_entry to the required invoice_data format
    invoice_data = map_ledger_to_invoice_data(ledger_entry)
    pdf_bytes = generate_invoice_pdf(invoice_data)
    # Get parsed_email, classification, and extracted_data if available
    parsed_email = transaction.get('parsed_email')
    classification = transaction.get('classification')
    extracted_data = transaction.get('extracted_data')
    # Only send reply if all required data is present
    if parsed_email and classification and extracted_data:
        # The reply agent will generate and send the reply in the same thread, with PDF attached
        try:
            rag_reply_generator_agent.send_reply_for_email(parsed_email, classification, extracted_data)
            return 'Reply and invoice sent successfully!'
        except Exception as e:
            return f'Error sending reply: {e}', 500
    else:
        # Fallback: just send the PDF as a normal email if reply agent data is missing
        customer_email = ledger_entry.get('Mail ID')
        if not customer_email:
            return 'Customer email not found in transaction', 400
        subject = 'Your Invoice or Quotation is Created Successfully'
        body = 'Dear Customer,\n\nYour invoice or quotation has been created successfully. Please find the PDF attached.\n\nThank you!'
        attachments = [{'filename': 'invoice.pdf', 'data': pdf_bytes}]
        gmail_client.send_email(customer_email, subject, body, attachments)
        return 'Invoice/Quotation sent successfully (fallback)!'

@app.route('/cancel', methods=['GET'])
def cancel_transaction():
    transaction_id = request.args.get('transaction_id')
    if not transaction_id:
        return 'Missing transaction_id', 400
    # Find the transaction in the database
    transaction = mongo_client.get_transaction_by_mail_id(transaction_id)
    if not transaction:
        return 'Transaction not found', 404
    ledger_entry = transaction.get('ledger_entry', {})
    customer_email = ledger_entry.get('Mail ID')
    # Delete the ledger entry
    mongo_client.get_collection('transactions').delete_one({'ledger_entry.Mail ID': transaction_id})
    # Do not send any reply or invoice if No is clicked
    return 'Process cancelled and ledger entry deleted.'

def map_ledger_to_invoice_data(ledger_entry):
    # Map your ledger_entry fields to the required invoice_data format for PDF generation
    # This is a placeholder; you should adjust field mappings as needed
    return {
        'company_name': 'Your Company',
        'company_address': 'Company Address',
        'company_phone': '1234567890',
        'company_email': 'company@email.com',
        'company_gstin': 'GSTIN123',
        'invoice_number': ledger_entry.get('Mail ID', 'INV-001'),
        'invoice_date': ledger_entry.get('Date', ''),
        'due_date': ledger_entry.get('Date', ''),
        'billed_to_name': ledger_entry.get('Vendor / Customer', ''),
        'billed_to_address': 'Customer Address',
        'billed_to_gstin': 'GSTIN456',
        'description': ledger_entry.get('Description', ''),
        'quantity': 1,
        'rate': ledger_entry.get('Debit', 0) or ledger_entry.get('Credit', 0),
        'subtotal': ledger_entry.get('Debit', 0) or ledger_entry.get('Credit', 0),
        'gst_percent': 18,
        'gst_amount': 0,
        'total_amount': ledger_entry.get('Debit', 0) or ledger_entry.get('Credit', 0),
        'bank_name': 'Bank Name',
        'account_name': 'Account Name',
        'account_no': '0000000000',
        'ifsc_code': 'IFSC0000',
    }

if __name__ == '__main__':
    app.run(port=5000) 