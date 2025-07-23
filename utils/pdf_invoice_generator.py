from fpdf import FPDF
import io

def generate_invoice_pdf(invoice_data):
    """
    Generate a PDF invoice using the provided invoice_data dict.
    Returns PDF as bytes.
    Required fields in invoice_data:
        - company_name
        - company_address
        - company_phone
        - company_email
        - company_gstin
        - invoice_number
        - invoice_date
        - due_date
        - billed_to_name
        - billed_to_address
        - billed_to_gstin
        - description
        - quantity
        - rate
        - subtotal
        - gst_percent
        - gst_amount
        - total_amount
        - bank_name
        - account_name
        - account_no
        - ifsc_code
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'INVOICE', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(5)
    pdf.cell(0, 8, invoice_data['company_name'], ln=True)
    pdf.cell(0, 8, invoice_data['company_address'], ln=True)
    pdf.cell(0, 8, f"Phone: {invoice_data['company_phone']}", ln=True)
    pdf.cell(0, 8, f"Email: {invoice_data['company_email']}", ln=True)
    pdf.cell(0, 8, f"GSTIN: {invoice_data['company_gstin']}", ln=True)
    pdf.ln(5)
    pdf.cell(0, 8, f"Invoice Number: {invoice_data['invoice_number']}", ln=True)
    pdf.cell(0, 8, f"Invoice Date: {invoice_data['invoice_date']}", ln=True)
    pdf.cell(0, 8, f"Due Date: {invoice_data['due_date']}", ln=True)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Billed To:', ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, invoice_data['billed_to_name'], ln=True)
    pdf.cell(0, 8, invoice_data['billed_to_address'], ln=True)
    pdf.cell(0, 8, f"GSTIN: {invoice_data['billed_to_gstin']}", ln=True)
    pdf.ln(5)
    # Table header
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(10, 8, '#', border=1)
    pdf.cell(80, 8, 'Description', border=1)
    pdf.cell(25, 8, 'Quantity', border=1)
    pdf.cell(35, 8, 'Rate (INR)', border=1)
    pdf.cell(35, 8, 'Amount (INR)', border=1, ln=True)
    # Table row
    pdf.set_font('Arial', '', 12)
    pdf.cell(10, 8, '1', border=1)
    pdf.cell(80, 8, invoice_data['description'], border=1)
    pdf.cell(25, 8, str(invoice_data['quantity']), border=1)
    pdf.cell(35, 8, f"{invoice_data['rate']:,}", border=1)
    pdf.cell(35, 8, f"{invoice_data['subtotal']:,}", border=1, ln=True)
    # Subtotal, GST, Total
    pdf.cell(150, 8, 'Subtotal', border=0)
    pdf.cell(35, 8, f"{invoice_data['subtotal']:,}", border=1, ln=True)
    pdf.cell(150, 8, f"GST @{invoice_data['gst_percent']}%", border=0)
    pdf.cell(35, 8, f"{invoice_data['gst_amount']:,}", border=1, ln=True)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(150, 8, 'Total Amount', border=0)
    pdf.cell(35, 8, f"{invoice_data['total_amount']:,}", border=1, ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.ln(5)
    pdf.cell(0, 8, 'Payment Instructions:', ln=True)
    pdf.cell(0, 8, f"Bank Name: {invoice_data['bank_name']}", ln=True)
    pdf.cell(0, 8, f"Account Name: {invoice_data['account_name']}", ln=True)
    pdf.cell(0, 8, f"Account No: {invoice_data['account_no']}", ln=True)
    pdf.cell(0, 8, f"IFSC Code: {invoice_data['ifsc_code']}", ln=True)
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 8, 'Note: Kindly make the payment on or before the due date.\nLate payment may attract interest at 1.5% per month.\nThank you for your business!')
    # Output as bytes
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes 