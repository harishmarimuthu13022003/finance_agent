#!/usr/bin/env python3
"""
Test script for Finance Agent Pipeline
"""

import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_individual_agents():
    """Test each agent individually"""
    print("🧪 Testing Individual Agents...")
    
    try:
        # Test Email Parser Agent
        print("\n1. Testing Email Parser Agent...")
        from agents.email_parser_agent import email_parser_agent
        
        sample_email = {
            'subject': 'Test Invoice #INV-001',
            'from': 'test@vendor.com',
            'to': 'finance@company.com',
            'date': '2024-01-15',
            'message_id': 'test-001',
            'body': 'Please find attached invoice for services. Amount: $500.00',
            'attachments': []
        }
        
        parsed_email = email_parser_agent.parse_email(sample_email)
        print(f"✅ Email Parser: Parsed email with subject '{parsed_email.subject}'")
        
        # Test Content Classifier Agent
        print("\n2. Testing Content Classifier Agent...")
        from agents.content_classifier_agent import content_classifier_agent
        
        classification = content_classifier_agent.classify_email(parsed_email)
        print(f"✅ Content Classifier: Classified as '{classification.primary_intent}' with confidence {classification.confidence_score}")
        
        # Test Data Extractor Agent
        print("\n3. Testing Data Extractor Agent...")
        from agents.data_extractor_agent import data_extractor_agent
        
        extracted_data = data_extractor_agent.extract_data(parsed_email, classification)
        print(f"✅ Data Extractor: Extracted amount '{extracted_data.amount}' and vendor '{extracted_data.vendor_name}'")
        
        # Test Ledger Mapper Agent
        print("\n4. Testing Ledger Mapper Agent...")
        from agents.ledger_mapper_agent import ledger_mapper_agent
        
        ledger_entry = ledger_mapper_agent.map_to_ledger(extracted_data, classification)
        # print(f"✅ Ledger Mapper: Mapped to GL code '{ledger_entry.gl_code}' - {ledger_entry.account_name}")
        
        # Test RAG Reply Generator Agent
        print("\n5. Testing RAG Reply Generator Agent...")
        from agents.rag_reply_generator_agent import rag_reply_generator_agent
        
        generated_reply = rag_reply_generator_agent.generate_reply(parsed_email, classification, extracted_data)
        print(f"✅ RAG Reply Generator: Generated reply with subject '{generated_reply.reply_subject}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing individual agents: {e}")
        return False

def test_full_pipeline():
    """Test the complete pipeline"""
    print("\n🧪 Testing Full Pipeline...")
    
    try:
        from orchestrator import orchestrator
        
        # Test with sample data
        result = orchestrator.test_pipeline()
        
        if result and result.get('pipeline_status') == 'completed':
            print("✅ Full pipeline test completed successfully!")
            print(f"   - Email ID: {result.get('email_id')}")
            print(f"   - Classification: {result.get('classification', {}).get('primary_intent', 'Unknown')}")
            print(f"   - Extracted Amount: {result.get('extracted_data', {}).get('amount', 'Unknown')}")
            # print(f"   - GL Code: {result.get('ledger_entry', {}).get('gl_code', 'Unknown')}")
            return True
        else:
            print("❌ Full pipeline test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing full pipeline: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🧪 Testing Database Connection...")
    
    try:
        from database.mongo_client import mongo_client
        
        # Test connection
        emails = mongo_client.get_all_emails()
        transactions = mongo_client.get_all_transactions()
        
        print(f"✅ Database connection successful!")
        print(f"   - Emails in database: {len(emails)}")
        print(f"   - Transactions in database: {len(transactions)}")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n🧪 Testing Configuration...")
    
    try:
        from config import Config
        
        print("✅ Configuration loaded successfully!")
        print(f"   - Gmail Email: {Config.GMAIL_EMAIL or 'Not configured'}")
        print(f"   - MongoDB URI: {Config.MONGODB_URI}")
        print(f"   - Google API Key: {'Configured' if Config.GOOGLE_API_KEY else 'Not configured'}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Finance Agent Pipeline Test")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Database Connection", test_database_connection),
        ("Individual Agents", test_individual_agents),
        ("Full Pipeline", test_full_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration and dependencies.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 