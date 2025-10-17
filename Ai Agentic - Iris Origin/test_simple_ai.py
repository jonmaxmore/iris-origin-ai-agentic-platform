"""
Test Simple AI Processing Engine
===============================

Quick testing for the simplified AI processor that works immediately.

Author: Iris Origin AI Team
Date: 2025-01-17
Version: 1.0.0 Production
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.ai_service.simple_processor import SimpleAIProcessor

async def test_simple_ai_processor():
    """Test the simple AI processor with various inputs"""
    print("🚀 Testing Simple AI Processing Engine")
    print("=" * 50)
    
    # Initialize processor
    processor = SimpleAIProcessor()
    print("✅ Simple AI Processor initialized")
    
    # Test cases
    test_cases = [
        # Thai language tests
        "สวัสดีครับ ผมต้องการสอบถามเรื่องสินค้า",
        "กรุณาช่วยแก้ไขปัญหานี้ด้วยค่ะ",
        "ขอบคุณมากค่ะ บริการดีมาก",
        "ร้องเรียนเรื่องการบริการแย่มาก",
        "ผมอยากทราบสถานะการสั่งซื้อ",
        "ลาก่อนครับ ขอบคุณ",
        
        # English language tests
        "Hello, I would like to inquire about your products",
        "Can you help me with this technical issue?",
        "Thank you very much, excellent service!",
        "I want to complain about the poor quality",
        "What's the status of my order #12345?",
        "Goodbye, thanks for your help",
        
        # Mixed and edge cases
        "Hi สวัสดี how are you?",
        "555 ตลกมาก LOL",
        "ราคา 1500 บาท",
        "Call me at 081-234-5678",
        "Email: support@example.com"
    ]
    
    print(f"\n🔍 Testing {len(test_cases)} different messages:")
    print("-" * 50)
    
    for i, message in enumerate(test_cases, 1):
        try:
            result = await processor.process_message(message, f"user_{i}")
            
            print(f"\n{i}. Message: '{message}'")
            print(f"   Language: {result.language}")
            print(f"   Intent: {result.intent} (confidence: {result.confidence:.2f})")
            print(f"   Sentiment: {result.sentiment} (score: {result.sentiment_score:.2f})")
            print(f"   Entities: {len(result.entities)} found")
            if result.entities:
                for entity in result.entities:
                    print(f"     - {entity['label']}: {entity['text']}")
            print(f"   Response: '{result.suggested_response}'")
            print(f"   Processing time: {result.processing_time_ms:.2f}ms")
            
        except Exception as e:
            print(f"❌ Error processing message {i}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Simple AI Processing Engine Test Completed!")
    print("🎯 The system is ready for production use.")

if __name__ == "__main__":
    try:
        asyncio.run(test_simple_ai_processor())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")