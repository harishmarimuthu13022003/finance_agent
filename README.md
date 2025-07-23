# 🤖 Agentic AI-Based Conversational Finance Inbox Agent

An intelligent AI-powered system that automatically processes financial emails, extracts structured data, maps to ledger entries, and generates contextual replies using a 5-agent pipeline.

## 🎯 Project Overview

This system bridges the gap between communication and accounting by:

- **Processing vendor, client, and finance-related emails** to extract financial data
- **Implementing a 5-agent pipeline** that parses content, classifies intent, extracts structured values, maps to ledger entries, and generates RAG-powered replies
- **Handling attachments** such as invoices or receipts in common formats (PDF, PNG, JPEG)
- **Displaying structured transaction logs** with tags, classifications, and status updates
- **Integrating with existing accounting tools** or export to CSV/JSON

## 🏗️ Architecture

### 5-Agent Pipeline

1. **Email Parser Agent** - Ingests and parses emails with attachments
2. **Content Classifier Agent** - Determines email intent and type
3. **Data Extractor Agent** - Extracts structured financial data
4. **Ledger Mapper Agent** - Maps data to appropriate ledger categories
5. **RAG-Enabled Reply Generator Agent** - Generates contextual replies using RAG

### Technology Stack

- **Backend**: Python, LangChain, Gemini 1.5 Flash
- **Database**: MongoDB
- **Frontend**: Streamlit
- **Email**: Gmail API integration
- **OCR**: PyPDF2, pytesseract for attachment processing
- **RAG**: FAISS vector store with Google Palm embeddings

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **MongoDB** (local installation or MongoDB Atlas)
3. **Google AI API Key** for Gemini 1.5 Flash
4. **Gmail App Password** for email integration
5. **Tesseract OCR** (for image processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finance_agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   # Gmail Configuration
   GMAIL_EMAIL=your_email@gmail.com
   GMAIL_PASSWORD=your_app_password
   GMAIL_SMTP_SERVER=smtp.gmail.com
   GMAIL_SMTP_PORT=587

   # MongoDB Configuration
   MONGODB_URI=mongodb://localhost:27017/
   MONGODB_DATABASE=finance_agent

   # Google AI Configuration
   GOOGLE_API_KEY=your_gemini_api_key

   # Application Configuration
   DEBUG=True
   LOG_LEVEL=INFO
   ```

4. **Set up Gmail App Password**
   - Go to Google Account settings
   - Enable 2-factor authentication
   - Generate an App Password for this application
   - Use the App Password in your `.env` file

5. **Install Tesseract OCR** (for Windows)
   ```bash
   # Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
   # Default installation path: C:\Program Files\Tesseract-OCR\
   ```

### Running the Application

1. **Start MongoDB** (if running locally)
   ```bash
   mongod
   ```

2. **Run the Streamlit application**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Access the dashboard**
   Open your browser and go to `http://localhost:8501`

## 📊 Features

### Dashboard
- Real-time email processing statistics
- Email classification distribution charts
- Currency and transaction analysis
- Recent activity feed

### Email Processing
- Batch email processing from Gmail
- Real-time processing status
- Pipeline testing capabilities
- Attachment processing (PDF, images)

### Transaction Logs
- Structured ledger entries
- Export to CSV functionality
- Transaction summary statistics
- Confidence scoring

### Reply Management
- RAG-powered reply generation
- Template management
- Missing field identification
- Professional communication standards

## 🔧 Configuration

### Gmail Setup
1. Enable IMAP in Gmail settings
2. Generate App Password
3. Update `.env` file with credentials

### MongoDB Setup
1. Install MongoDB locally or use MongoDB Atlas
2. Create database: `finance_agent`
3. Collections will be created automatically

### Google AI Setup
1. Get API key from Google AI Studio
2. Enable Gemini API
3. Add API key to `.env` file

## 📁 Project Structure

```
finance_agent/
├── agents/                          # 5 Agent implementations
│   ├── email_parser_agent.py       # Email parsing and attachment processing
│   ├── content_classifier_agent.py  # Email intent classification
│   ├── data_extractor_agent.py     # Financial data extraction
│   ├── ledger_mapper_agent.py      # Ledger entry mapping
│   └── rag_reply_generator_agent.py # RAG-powered reply generation
├── database/
│   └── mongo_client.py             # MongoDB connection and operations
├── utils/
│   ├── email_utils.py              # Gmail integration utilities
│   └── attachment_processor.py     # PDF and image processing
├── orchestrator.py                 # Main pipeline orchestrator
├── streamlit_app.py               # Streamlit frontend application
├── config.py                      # Configuration management
├── requirements.txt               # Python dependencies
└── README.md                     # Project documentation
```

## 🔄 Workflow

1. **Email arrives** in Gmail inbox
2. **Email Parser Agent** extracts body, metadata, and attachments
3. **Content Classifier Agent** tags the email (Invoice, Payment, etc.)
4. **Data Extractor Agent** pulls key fields (amount, vendor, date, etc.)
5. **Ledger Mapper Agent** maps to appropriate GL codes
6. **Reply Generator Agent** drafts contextual responses
7. **Dashboard** displays parsed data and processing status

## 📈 Sample Flow

```
Email: "Invoice #INV-2024-001 from ABC Corp - $1,500 due 2024-02-15"
↓
Email Parser Agent → Extracts body and metadata
↓
Content Classifier Agent → Tags as "Invoice"
↓
Data Extractor Agent → Extracts: $1,500, ABC Corp, INV-2024-001, 2024-02-15
↓
Ledger Mapper Agent → Maps to "Accounts Payable" (GL: 2100)
↓
Reply Generator Agent → Drafts: "Invoice received, processing according to policy"
↓
Dashboard → Shows transaction log and processing status
```

## 🧪 Testing

### Test the Pipeline
```python
from orchestrator import orchestrator

# Test with sample data
result = orchestrator.test_pipeline()
print(result)
```

### Process Emails
```python
# Process batch of emails
results = orchestrator.process_batch_emails(limit=10)

# Process single email
result = orchestrator.process_single_email(email_data)
```

## 📊 Monitoring

### Dashboard Metrics
- Total emails processed
- Transaction success rate
- Classification accuracy
- Currency distribution
- Processing time statistics

### Export Capabilities
- CSV export of ledger entries
- JSON export of transaction data
- Email processing logs

## 🔒 Security

- Gmail App Passwords for secure email access
- Environment variables for sensitive configuration
- MongoDB authentication (if configured)
- API key management for Google AI

## 🚨 Troubleshooting

### Common Issues

1. **Gmail Connection Failed**
   - Verify App Password is correct
   - Enable IMAP in Gmail settings
   - Check firewall settings

2. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Verify connection string in `.env`
   - Check network connectivity

3. **OCR Processing Failed**
   - Install Tesseract OCR
   - Verify installation path
   - Check image format support

4. **API Key Issues**
   - Verify Google AI API key is valid
   - Check API quota limits
   - Ensure Gemini API is enabled

### Logs
Check application logs for detailed error information:
```bash
# View Streamlit logs
streamlit run streamlit_app.py --logger.level debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LangChain for the agent framework
- Google AI for Gemini 1.5 Flash
- Streamlit for the dashboard interface
- MongoDB for data storage
- OpenCV and pytesseract for OCR processing

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

---

**Built with ❤️ using LangChain and Gemini 1.5 Flash** 

---

## How to Fix

1. **Open the `.cursorignore` file** in your project root (it works like `.gitignore`).
2. **Remove the line that says `.env`** (or any other file you want AI features enabled for).
3. **Save the `.cursorignore` file.**
4. **Restart your editor** (VS Code, Cursor, etc.) if needed.

---

### Example

If your `.cursorignore` looks like this:
```
.env
*.pyc
__pycache__/
```
Just remove or comment out the `.env` line:
```
<code_block_to_apply_changes_from>
```

---

After this, AI features should be enabled for your `.env` file and the restricted icon should disappear (after a restart if needed).

---

**Summary:**  
Remove `.env` from `.cursorignore` to enable AI features and remove the restricted icon.

Let me know if you need help finding or editing your `.cursorignore` file! 