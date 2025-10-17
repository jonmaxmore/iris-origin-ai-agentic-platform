"""
Test AI Processing Engine
========================

Enterprise-grade testing for AI processing capabilities.
Tests all core functionality with real-world scenarios.

Author: Iris Origin AI Team
Date: 2025-01-17
Version: 1.0.0 Enterprise
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import AI service components
from src.ai_service.core.ai_processor import EnterpriseAIProcessor
from src.ai_service.models.message_models import Message, MessageType, Platform
from src.ai_service.utils.language_detector import LanguageDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_language_detection():
    """Test language detection with various inputs"""
    print("\n=== Testing Language Detection ===")
    
    detector = LanguageDetector()
    
    test_cases = [
        ("สวัสดีครับ ผมต้องการสอบถามเรื่องสินค้า", "th"),
        ("Hello, I would like to inquire about your products", "en"),
        ("กรุณาช่วยแก้ไขปัญหานี้ด้วยค่ะ", "th"),
        ("Can you help me with this issue please?", "en"),
        ("ขอบคุณมากค่ะ บริการดีมาก", "th"),
        ("Thank you very much, excellent service!", "en"),
        ("555 ตลกมาก", "th"),
        ("LOL that's hilarious", "en")
    ]
    
    for text, expected_lang in test_cases:
        try:
            result = await detector.detect_language_with_confidence(text)
            status = "✅" if result.language == expected_lang else "❌"
            print(f"{status} Text: '{text[:30]}...'")
            print(f"   Detected: {result.language} (confidence: {result.confidence:.2f})")
            print(f"   Method: {result.detection_method}")
            print(f"   Cultural context: {result.cultural_context}")
            print()
        except Exception as e:
            print(f"❌ Error testing '{text[:30]}...': {e}")

async def test_ai_processor_initialization():
    """Test AI processor initialization"""
    print("\n=== Testing AI Processor Initialization ===")
    
    try:
        processor = EnterpriseAIProcessor()
        print("✅ AI Processor created successfully")
        
        # Test model initialization (this might take a while)
        print("🔄 Initializing AI models... (this may take several minutes)")
        await processor.initialize_models()
        print("✅ AI models initialized successfully")
        
        return processor
        
    except Exception as e:
        print(f"❌ AI Processor initialization failed: {e}")
        logger.error(f"AI Processor initialization error: {e}")
        return None

async def test_message_processing(processor):
    """Test complete message processing pipeline"""
    if not processor:
        print("\n❌ Skipping message processing tests - processor not available")
        return
    
    print("\n=== Testing Message Processing Pipeline ===")
    
    test_messages = [
        {
            "text": "สวัสดีครับ ผมต้องการสอบถามเรื่องราคาสินค้า",
            "user_id": "test_user_thai_1",
            "platform": Platform.FACEBOOK,
            "expected_intent": "product_inquiry",
            "expected_language": "th"
        },
        {
            "text": "Hello, I have a complaint about your service",
            "user_id": "test_user_eng_1", 
            "platform": Platform.INSTAGRAM,
            "expected_intent": "complaint",
            "expected_language": "en"
        },
        {
            "text": "ขอบคุณมากค่ะ บริการดีเยี่ยม",
            "user_id": "test_user_thai_2",
            "platform": Platform.WHATSAPP,
            "expected_intent": "compliment",
            "expected_language": "th"
        },
        {
            "text": "Can you help me with my order status?",
            "user_id": "test_user_eng_2",
            "platform": Platform.WEB,
            "expected_intent": "order_status",
            "expected_language": "en"
        }
    ]
    
    for i, test_case in enumerate(test_messages, 1):
        try:
            print(f"\n--- Test Case {i} ---")
            print(f"Input: '{test_case['text']}'")
            
            # Create message object
            message = Message(
                user_id=test_case['user_id'],
                text=test_case['text'],
                platform=test_case['platform'],
                message_type=MessageType.TEXT
            )
            
            # Process message
            start_time = datetime.now()
            processed_message = await processor.process_message(message)
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Check results
            result = processed_message.processing_result
            
            print(f"✅ Processing completed in {processing_time:.2f}ms")
            print(f"   Language: {result.language} (expected: {test_case['expected_language']})")
            print(f"   Intent: {result.intent} (confidence: {result.confidence:.2f})")
            print(f"   Sentiment: {result.sentiment} (score: {result.sentiment_score:.2f})")
            print(f"   Entities: {len(result.entities)} found")
            print(f"   Response: '{result.suggested_response[:50]}...'")
            
            # Validate results
            language_ok = result.language == test_case['expected_language']
            confidence_ok = result.confidence > 0.3
            response_ok = len(result.suggested_response) > 0
            
            print(f"   Language Match: {'✅' if language_ok else '❌'}")
            print(f"   Confidence OK: {'✅' if confidence_ok else '❌'}")
            print(f"   Response Generated: {'✅' if response_ok else '❌'}")
            
        except Exception as e:
            print(f"❌ Error processing test case {i}: {e}")
            logger.error(f"Message processing error: {e}")

async def test_performance_metrics(processor):
    """Test performance metrics and monitoring"""
    if not processor:
        print("\n❌ Skipping performance tests - processor not available")
        return
        
    print("\n=== Testing Performance Metrics ===")
    
    try:
        metrics = await processor.get_performance_metrics()
        
        print("✅ Performance metrics retrieved successfully")
        print(f"   Total messages processed: {metrics['processing_stats']['total_processed']}")
        print(f"   Average processing time: {metrics['processing_stats']['average_processing_time']:.2f}ms")
        print(f"   Average accuracy: {metrics['processing_stats']['accuracy_score']:.2f}")
        print(f"   Model health: {len(metrics['model_status'])} models checked")
        print(f"   System uptime: {metrics['uptime']:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Error getting performance metrics: {e}")

async def main():
    """Main test function"""
    print("🚀 Starting Iris Origin AI Processing Engine Tests")
    print("=" * 60)
    
    # Test 1: Language Detection
    await test_language_detection()
    
    # Test 2: AI Processor Initialization
    processor = await test_ai_processor_initialization()
    
    # Test 3: Message Processing Pipeline
    await test_message_processing(processor)
    
    # Test 4: Performance Metrics
    await test_performance_metrics(processor)
    
    print("\n" + "=" * 60)
    print("🎉 AI Processing Engine Tests Completed")
    print("Check the results above for any issues that need attention.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error during testing: {e}")
        logger.error(f"Critical test error: {e}")
        sys.exit(1)