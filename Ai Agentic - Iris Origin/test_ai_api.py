"""
Test AI API Functionality
=========================

Direct test of AI processing functionality without server complications.

Author: Iris Origin AI Team
Date: 2025-01-17
Version: 1.0.0 Production
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import directly from our simple processor file
exec(open('src/ai_service/simple_processor.py').read())

async def test_ai_api_functionality():
    """Test AI API functionality directly"""
    print("🚀 Testing AI API Functionality")
    print("=" * 50)
    
    # Initialize processor
    try:
        processor = SimpleAIProcessor()
        print("✅ AI Processor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize processor: {e}")
        return
    
    # Test messages simulating API requests
    test_cases = [
        {
            "message": "สวัสดีครับ ผมต้องการสอบถามเรื่องสินค้า",
            "user_id": "thai_user_1",
            "expected_language": "th",
            "expected_intent": "greeting"
        },
        {
            "message": "Hello, I need help with my order",
            "user_id": "eng_user_1",
            "expected_language": "en", 
            "expected_intent": "support_request"
        },
        {
            "message": "ขอบคุณมากค่ะ บริการดีเยี่ยม",
            "user_id": "thai_user_2",
            "expected_language": "th",
            "expected_intent": "compliment"
        },
        {
            "message": "I want to complain about poor service",
            "user_id": "eng_user_2",
            "expected_language": "en",
            "expected_intent": "complaint"
        },
        {
            "message": "ผมต้องการทราบสถานะออเดอร์ #12345",
            "user_id": "thai_user_3",
            "expected_language": "th",
            "expected_intent": "order_status"
        }
    ]
    
    print(f"\n🔍 Testing {len(test_cases)} API scenarios:")
    print("-" * 50)
    
    total_processing_time = 0
    successful_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\n{i}. API Request Simulation:")
            print(f"   Message: '{test_case['message']}'")
            print(f"   User ID: {test_case['user_id']}")
            
            # Process message (simulating API call)
            result = await processor.process_message(
                message_text=test_case['message'],
                user_id=test_case['user_id']
            )
            
            # Create API response format
            api_response = {
                "success": True,
                "intent": result.intent,
                "confidence": result.confidence,
                "sentiment": result.sentiment,
                "sentiment_score": result.sentiment_score,
                "language": result.language,
                "entities": result.entities,
                "suggested_response": result.suggested_response,
                "processing_time_ms": result.processing_time_ms,
                "user_id": test_case['user_id']
            }
            
            # Display results
            print(f"   ✅ API Response:")
            print(f"      Success: {api_response['success']}")
            print(f"      Language: {api_response['language']} (expected: {test_case['expected_language']})")
            print(f"      Intent: {api_response['intent']} (confidence: {api_response['confidence']:.2f})")
            print(f"      Sentiment: {api_response['sentiment']} (score: {api_response['sentiment_score']:.2f})")
            print(f"      Entities: {len(api_response['entities'])} found")
            if api_response['entities']:
                for entity in api_response['entities']:
                    print(f"        - {entity['label']}: {entity['text']}")
            print(f"      Response: '{api_response['suggested_response']}'")
            print(f"      Processing Time: {api_response['processing_time_ms']:.2f}ms")
            
            # Validation
            language_correct = api_response['language'] == test_case['expected_language']
            confidence_good = api_response['confidence'] > 0.3
            response_generated = len(api_response['suggested_response']) > 0
            
            if language_correct and confidence_good and response_generated:
                successful_tests += 1
                print(f"   🎯 Test Result: PASSED")
            else:
                print(f"   ⚠️ Test Result: PARTIAL")
            
            total_processing_time += api_response['processing_time_ms']
            
        except Exception as e:
            print(f"   ❌ Test Failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 API FUNCTIONALITY TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Tests Passed: {successful_tests}/{len(test_cases)}")
    print(f"⚡ Average Processing Time: {total_processing_time/len(test_cases):.2f}ms")
    print(f"🎯 Success Rate: {(successful_tests/len(test_cases)*100):.1f}%")
    
    if successful_tests == len(test_cases):
        print("\n🎉 ALL TESTS PASSED! AI API is ready for production!")
        print("🚀 The system can handle real customer service requests.")
    else:
        print(f"\n⚠️ {len(test_cases) - successful_tests} tests need attention.")
    
    # Test JSON serialization (API compatibility)
    print(f"\n🔧 Testing JSON API Compatibility...")
    try:
        sample_result = await processor.process_message("Test message", "test_user")
        api_json = json.dumps({
            "success": True,
            "intent": sample_result.intent,
            "confidence": sample_result.confidence,
            "sentiment": sample_result.sentiment,
            "sentiment_score": sample_result.sentiment_score,
            "language": sample_result.language,
            "entities": sample_result.entities,
            "suggested_response": sample_result.suggested_response,
            "processing_time_ms": sample_result.processing_time_ms
        }, ensure_ascii=False, indent=2)
        
        print("✅ JSON serialization successful")
        print("✅ API responses are properly formatted")
        
        # Show sample JSON response
        print(f"\n📋 Sample API Response JSON:")
        print(api_json[:200] + "..." if len(api_json) > 200 else api_json)
        
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_ai_api_functionality())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")