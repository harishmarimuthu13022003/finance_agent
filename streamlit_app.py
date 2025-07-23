import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

from orchestrator import orchestrator
from database.mongo_client import mongo_client
from config import Config
from utils.email_utils import send_confirmation_email

# Page configuration
st.set_page_config(
    page_title="Finance Agent Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🤖 Finance Agent Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Email Processing", "Transaction Logs", "Reply Management", "Settings"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Email Processing":
        show_email_processing()
    elif page == "Transaction Logs":
        show_transaction_logs()
    elif page == "Reply Management":
        show_reply_management()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    st.header("📊 Dashboard Overview")
    
    # Auto-refresh
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    # Get pipeline stats
    stats = orchestrator.get_pipeline_stats()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Emails",
            value=stats.get('total_emails', 0),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Transactions",
            value=stats.get('total_transactions', 0),
            delta=None
        )
    
    with col3:
        classification_stats = stats.get('classification_stats', {})
        financial_emails = classification_stats.get('financial_relevance_count', 0)
        st.metric(
            label="Financial Emails",
            value=financial_emails,
            delta=None
        )
    
    with col4:
        extraction_stats = stats.get('extraction_stats', {})
        success_rate = extraction_stats.get('successful_extractions', 0)
        total_extractions = extraction_stats.get('total_transactions', 1)
        success_percentage = (success_rate / total_extractions * 100) if total_extractions > 0 else 0
        st.metric(
            label="Extraction Success Rate",
            value=f"{success_percentage:.1f}%",
            delta=None
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Email Classification Distribution")
        classification_stats = stats.get('classification_stats', {})
        intent_distribution = classification_stats.get('intent_distribution', {})
        
        if intent_distribution:
            df_intent = pd.DataFrame(list(intent_distribution.items()), columns=['Intent', 'Count'])
            fig = px.pie(df_intent, values='Count', names='Intent', title="Email Intent Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No classification data available")
    
    with col2:
        st.subheader("💰 Currency Distribution")
        extraction_stats = stats.get('extraction_stats', {})
        currency_distribution = extraction_stats.get('currency_distribution', {})
        
        if currency_distribution:
            df_currency = pd.DataFrame(list(currency_distribution.items()), columns=['Currency', 'Count'])
            fig = px.bar(df_currency, x='Currency', y='Count', title="Currency Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No currency data available")
    
    # Recent activity
    st.subheader("🕒 Recent Activity")
    
    try:
        emails = mongo_client.get_all_emails()
        if emails:
            recent_emails = emails[:5]  # Show last 5 emails
            
            for email in recent_emails:
                with st.expander(f"📧 {email.get('parsed_email', {}).get('subject', 'No subject')}"):
                    parsed_email = email.get('parsed_email', {})
                    st.write(f"**From:** {parsed_email.get('sender', 'Unknown')}")
                    st.write(f"**Date:** {parsed_email.get('date', 'Unknown')}")
                    st.write(f"**Body:** {parsed_email.get('body_text', 'No body')[:200]}...")
        else:
            st.info("No recent emails found")
    except Exception as e:
        st.error(f"Error loading recent activity: {e}")

def show_email_processing():
    st.header("📧 Email Processing")
    
    # Processing options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔄 Process New Emails")
        email_limit = st.slider("Number of emails to process", 1, 50, 10)
        
        if st.button("🚀 Start Processing", type="primary"):
            with st.spinner("Processing emails..."):
                try:
                    results = orchestrator.process_batch_emails(limit=email_limit)
                    if results:
                        st.success(f"✅ Successfully processed {len(results)} emails!")
                        
                        # Show results summary
                        st.subheader("📋 Processing Results")
                        for result in results[:3]:  # Show first 3 results
                            with st.expander(f"📧 {result.get('parsed_email', {}).get('subject', 'No subject')}"):
                                st.json(result)
                    else:
                        st.warning("⚠️ No emails were processed")
                except Exception as e:
                    st.error(f"❌ Error processing emails: {e}")
    
    with col2:
        st.subheader("🧪 Test Pipeline")
        if st.button("🧪 Run Test"):
            with st.spinner("Running pipeline test..."):
                try:
                    result = orchestrator.test_pipeline()
                    if result:
                        st.success("✅ Pipeline test completed successfully!")
                        st.json(result)
                    else:
                        st.error("❌ Pipeline test failed")
                except Exception as e:
                    st.error(f"❌ Error during test: {e}")
    
    # Real-time processing status
    st.subheader("📊 Processing Status")
    
    # Create a placeholder for real-time updates
    status_placeholder = st.empty()
    
    # Simulate real-time updates
    if st.button("🔄 Start Real-time Monitoring"):
        for i in range(10):
            with status_placeholder.container():
                st.write(f"🔄 Processing email {i+1}/10...")
                st.progress((i+1)/10)
            time.sleep(1)
        st.success("✅ Real-time monitoring completed!")

def show_transaction_logs():
    st.header("📊 Transaction Logs")
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export to CSV"):
            try:
                filename = orchestrator.export_ledger_entries()
                if filename:
                    st.success(f"✅ Exported to {filename}")
                else:
                    st.error("❌ Export failed")
            except Exception as e:
                st.error(f"❌ Error exporting: {e}")
    
    with col2:
        if st.button("🔄 Refresh Logs"):
            st.rerun()
    
    # Display transaction logs
    try:
        transactions = mongo_client.get_all_transactions()
        
        if transactions:
            st.subheader("📋 Recent Transactions")
            
            # Create DataFrame for display and add a button for each row
            transaction_data = []
            ledger_entries = []
            for transaction in transactions:
                if 'ledger_entry' in transaction:
                    ledger_entry = transaction['ledger_entry']
                    transaction_data.append({
                        'Date': ledger_entry.get('Date', ''),
                        'Mail ID': ledger_entry.get('Mail ID', ''),
                        'Type': ledger_entry.get('Type', ''),
                        'Description': ledger_entry.get('Description', ''),
                        'Vendor / Customer': ledger_entry.get('Vendor / Customer', ''),
                        'Debit': ledger_entry.get('Debit', ''),
                        'Credit': ledger_entry.get('Credit', ''),
                    })
                    ledger_entries.append(ledger_entry)
            
            if transaction_data:
                df = pd.DataFrame(transaction_data)[['Date', 'Mail ID', 'Type', 'Description', 'Vendor / Customer', 'Debit', 'Credit']]
                # Add a button for each row
                for idx, row in df.iterrows():
                    cols = st.columns(len(row) + 1)
                    for i, value in enumerate(row):
                        cols[i].write(value)
                    # Print ledger entry for debugging
                    ledger_entry = ledger_entries[idx]
                    with cols[len(row)]:
                        if st.button("Send Confirmation Email", key=f"send_confirm_{idx}"):
                            st.write(f"Debug: Ledger entry = {ledger_entry}")
                            customer_email = (
                                ledger_entry.get('Mail ID') or
                                ledger_entry.get('Vendor / Customer Email') or
                                ledger_entry.get('Customer Email') or
                                ledger_entry.get('Email')
                            )
                            st.write(f"Debug: Attempted customer_email = {customer_email}")
                            if not customer_email:
                                st.error(f"Customer email not found in transaction. Ledger entry: {ledger_entry}")
                            else:
                                base_url = "http://localhost:5000"  # Update if running Flask elsewhere
                                result = send_confirmation_email(customer_email, ledger_entry, base_url)
                                if result:
                                    st.success("Confirmation email sent!")
                                else:
                                    st.error("Failed to send confirmation email.")
                
                # Summary statistics
                st.subheader("📈 Transaction Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_debit = pd.to_numeric(df['Debit'], errors='coerce').sum() if 'Debit' in df.columns else 0
                    st.metric("Total Debits", f"${total_debit:,.2f}")
                
                with col2:
                    total_credit = pd.to_numeric(df['Credit'], errors='coerce').sum() if 'Credit' in df.columns else 0
                    st.metric("Total Credits", f"${total_credit:,.2f}")
                
                with col3:
                    st.metric("Total Transactions", f"{len(df)}")
            else:
                st.info("No transaction data available")
        else:
            st.info("No transactions found")
    except Exception as e:
        st.error(f"Error loading transaction logs: {e}")

def show_reply_management():
    st.header("💬 Reply Management")
    
    # Reply templates
    st.subheader("📝 Reply Templates")
    
    try:
        templates = mongo_client.get_templates_by_type("template")
        
        if templates:
            for idx, template in enumerate(templates):
                with st.expander(f"📄 {template.get('title', 'Untitled')}"):
                    st.write(f"**Category:** {template.get('category', 'General')}")
                    st.write(f"**Content:** {template.get('content', 'No content')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✏️ Edit {template.get('title', 'Template')}", key=f"edit_{idx}"):
                            st.info("Edit functionality coming soon...")
                    with col2:
                        if st.button(f"🗑️ Delete {template.get('title', 'Template')}", key=f"delete_{idx}"):
                            st.info("Delete functionality coming soon...")
        else:
            st.info("No templates found")
    except Exception as e:
        st.error(f"Error loading templates: {e}")
    
    # Generated replies
    st.subheader("📤 Generated Replies")
    
    try:
        responses = mongo_client.get_all_responses()
        if responses:
            for idx, response in enumerate(responses[:5]):  # Show last 5 responses
                if 'generated_reply' in response:
                    reply = response['generated_reply']
                    parsed_email = response.get('parsed_email', {})
                    classification = response.get('classification', {})
                    extracted_data = response.get('extracted_data', {})
                    with st.expander(f"📧 {reply.get('reply_subject', 'No subject')}"):
                        st.write(f"**Type:** {reply.get('reply_type', 'Unknown')}")
                        st.write(f"**Tone:** {reply.get('tone', 'Unknown')}")
                        st.write(f"**Urgency:** {reply.get('urgency_level', 'Unknown')}")
                        st.write(f"**Body:** {reply.get('reply_body', 'No content')}")
                        missing_fields = reply.get('missing_fields', [])
                        if missing_fields:
                            st.write(f"**Missing Fields:** {', '.join(missing_fields)}")
                        if st.button("Send Reply", key=f"send_reply_{idx}"):
                            from agents.rag_reply_generator_agent import rag_reply_generator_agent
                            try:
                                rag_reply_generator_agent.send_reply_for_email(parsed_email, classification, extracted_data)
                                st.success("Reply sent!")
                            except Exception as e:
                                st.error(f"Failed to send reply: {e}")
        else:
            st.info("No generated replies found")
    except Exception as e:
        st.error(f"Error loading replies: {e}")

def show_settings():
    st.header("⚙️ Settings")
    
    # Configuration
    st.subheader("🔧 Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Gmail Settings**")
        st.write(f"Email: {Config.GMAIL_EMAIL or 'Not configured'}")
        st.write(f"SMTP Server: {Config.GMAIL_SMTP_SERVER}")
        st.write(f"SMTP Port: {Config.GMAIL_SMTP_PORT}")
    
    with col2:
        st.write("**Database Settings**")
        st.write(f"MongoDB URI: {Config.MONGODB_URI}")
        st.write(f"Database: {Config.MONGODB_DATABASE}")
    
    # Agent status
    st.subheader("🤖 Agent Status")
    
    agents = {
        "Email Parser Agent": "✅ Active",
        "Content Classifier Agent": "✅ Active", 
        "Data Extractor Agent": "✅ Active",
        "Ledger Mapper Agent": "✅ Active",
        "RAG Reply Generator Agent": "✅ Active"
    }
    
    for agent, status in agents.items():
        st.write(f"**{agent}:** {status}")
    
    # System information
    st.subheader("ℹ️ System Information")
    st.write(f"**Python Version:** {st.get_option('server.headless')}")
    st.write(f"**Streamlit Version:** {st.__version__}")
    st.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 