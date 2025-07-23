import imaplib
import email
import base64
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class GmailClient:
    def __init__(self):
        self.imap_server = "imap.gmail.com"
        self.smtp_server = Config.GMAIL_SMTP_SERVER
        self.smtp_port = Config.GMAIL_SMTP_PORT
        self.email = Config.GMAIL_EMAIL
        self.password = Config.GMAIL_PASSWORD
        
    def connect_imap(self):
        """Connect to Gmail IMAP server"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email, self.password)
            return mail
        except Exception as e:
            logger.error(f"Failed to connect to Gmail IMAP: {e}")
            raise
    
    def fetch_emails(self, folder="INBOX", limit=10):
        """Fetch unread emails from Gmail"""
        mail = self.connect_imap()
        emails = []
        try:
            mail.select(folder)
            _, message_numbers = mail.search(None, 'UNSEEN')
            # Get the latest unread emails
            email_list = message_numbers[0].split()
            recent_emails = email_list[-limit:] if len(email_list) > limit else email_list
            for num in recent_emails:
                try:
                    _, msg_data = mail.fetch(num, '(RFC822)')
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    parsed_email = self.parse_email(email_message)
                    parsed_email['imap_uid'] = num  # Store UID for marking as read
                    emails.append(parsed_email)
                except Exception as e:
                    logger.error(f"Error parsing email {num}: {e}")
                    continue
        finally:
            mail.close()
            mail.logout()
        return emails

    def mark_as_read(self, uid, folder="INBOX"):
        """Mark an email as read by UID"""
        mail = self.connect_imap()
        try:
            mail.select(folder)
            mail.store(uid, '+FLAGS', '\\Seen')
        except Exception as e:
            logger.error(f"Failed to mark email {uid} as read: {e}")
        finally:
            mail.close()
            mail.logout()
    
    def parse_email(self, email_message):
        """Parse email message into structured format"""
        parsed_email = {
            'subject': email_message.get('subject', ''),
            'from': email_message.get('from', ''),
            'to': email_message.get('to', ''),
            'date': email_message.get('date', ''),
            'message_id': email_message.get('message-id', ''),
            'body': '',
            'attachments': [],
            'timestamp': datetime.now()
        }
        
        # Extract body
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    parsed_email['body'] = part.get_payload(decode=True).decode()
                    break
                elif part.get_content_type() == "text/html":
                    # Fallback to HTML if no plain text
                    if not parsed_email['body']:
                        parsed_email['body'] = part.get_payload(decode=True).decode()
        else:
            parsed_email['body'] = email_message.get_payload(decode=True).decode()
        
        # Extract attachments
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                
                filename = part.get_filename()
                if filename:
                    attachment_data = {
                        'filename': filename,
                        'content_type': part.get_content_type(),
                        'data': part.get_payload(decode=True)
                    }
                    parsed_email['attachments'].append(attachment_data)
        
        return parsed_email
    
    def send_email(self, to_email, subject, body, attachments=None):
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['data'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)
            
            # Send email
            import smtplib
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            text = msg.as_string()
            server.sendmail(self.email, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

def send_confirmation_email(to_email, transaction, base_url):
    """
    Send a confirmation email to the customer with Yes/No action links for a transaction.
    - to_email: recipient's email address
    - transaction: dict containing transaction info (should include a unique id)
    - base_url: the base URL of the webhook server (e.g., http://localhost:5000)
    """
    transaction_id = transaction.get('Mail ID') or transaction.get('id')
    if not transaction_id:
        raise ValueError('Transaction must have a unique Mail ID or id')
    
    yes_url = f"{base_url}/confirm?transaction_id={transaction_id}"
    no_url = f"{base_url}/cancel?transaction_id={transaction_id}"
    
    subject = "Please Confirm Your Transaction"
    body = f"""
    <p>Dear Customer,</p>
    <p>We have received your transaction request. Please confirm if you want to proceed.</p>
    <p>
        <a href='{yes_url}' style='background-color:#28a745;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;font-weight:bold;'>
            &#10003; Yes Confirm
        </a>
        &nbsp;
        <a href='{no_url}' style='background-color:#dc3545;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;font-weight:bold;'>
            &#10007; No, I Don\'t Want
        </a>
    </p>
    <p>If you click "No", your process will be cancelled and you will receive a confirmation email.</p>
    <p>If you click "Yes Confirm", your invoice or quotation will be created and sent to you as a PDF.</p>
    <p>Thank you!</p>
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = gmail_client.email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        import smtplib
        server = smtplib.SMTP(gmail_client.smtp_server, gmail_client.smtp_port)
        server.starttls()
        server.login(gmail_client.email, gmail_client.password)
        text = msg.as_string()
        server.sendmail(gmail_client.email, to_email, text)
        server.quit()
        logger.info(f"Confirmation email sent to {to_email} for transaction {transaction_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}")
        return False

# Global Gmail client instance
gmail_client = GmailClient() 