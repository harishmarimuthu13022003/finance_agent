import PyPDF2
import io
import base64
import logging
from PIL import Image
import pytesseract
import cv2
import numpy as np
from config import Config

logger = logging.getLogger(__name__)

class AttachmentProcessor:
    def __init__(self):
        # Configure pytesseract path for Windows
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        except:
            logger.warning("Tesseract not found, OCR functionality may not work")
    
    def process_attachment(self, attachment_data):
        """Process attachment and extract text"""
        filename = attachment_data['filename']
        content_type = attachment_data['content_type']
        data = attachment_data['data']
        
        try:
            if content_type == 'application/pdf':
                return self.extract_pdf_text(data)
            elif content_type.startswith('image/'):
                return self.extract_image_text(data)
            else:
                logger.warning(f"Unsupported content type: {content_type}")
                return ""
                
        except Exception as e:
            logger.error(f"Error processing attachment {filename}: {e}")
            return ""
    
    def extract_pdf_text(self, pdf_data):
        """Extract text from PDF"""
        try:
            pdf_file = io.BytesIO(pdf_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_image_text(self, image_data):
        """Extract text from image using OCR"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to get black text on white background
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(thresh)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting image text: {e}")
            return ""
    
    def process_email_attachments(self, email_data):
        """Process all attachments in an email"""
        processed_attachments = []
        
        for attachment in email_data.get('attachments', []):
            text_content = self.process_attachment(attachment)
            
            processed_attachment = {
                'filename': attachment['filename'],
                'content_type': attachment['content_type'],
                'extracted_text': text_content,
                'original_data': attachment['data']  # Keep original for storage
            }
            
            processed_attachments.append(processed_attachment)
        
        return processed_attachments

# Global attachment processor instance
attachment_processor = AttachmentProcessor() 