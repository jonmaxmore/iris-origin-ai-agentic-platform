"""
Iris Origin - Simple AI API Server
==================================

Lightweight production-ready API server using SimpleAIProcessor.
No heavy dependencies, immediate deployment ready.

Author: Iris Origin AI Team
Date: 2025-01-17
Version: 1.0.0 Production-Lite
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import asyncio
import uvicorn
import json
import re
from datetime import datetime
from dataclasses import dataclass
import logging

# Production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("iris-origin-simple-api")

# ===== EMBEDDED SIMPLE AI PROCESSOR =====
@dataclass
class ProcessingResult:
    """Processing result"""
    intent: str
    confidence: float
    sentiment: str
    sentiment_score: float
    language: str
    entities: List[Dict[str, Any]]
    suggested_response: str
    processing_time_ms: float

class SimpleAIProcessor:
    """Lightweight AI processor for production"""
    
    def __init__(self):
        self.thai_keywords = {
            'greeting': ['สวัสดี', 'หวัดดี', 'ดีครับ', 'ดีค่ะ', 'ยินดี', 'เฮ้ย', 'หวัดดี'],
            'product_inquiry': ['สินค้า', 'ผลิตภัณฑ์', 'ราคา', 'ค่าใช้จ่าย', 'เท่าไร', 'ขาย', 'ซื้อ'],
            'support_request': ['ช่วย', 'ช่วยเหลือ', 'แก้ไข', 'ปัญหา', 'ไม่ได้', 'ขัดข้อง', 'เสีย'],
            'complaint': ['บ่น', 'ร้องเรียน', 'แย่', 'ไม่ดี', 'แย่มาก', 'ผิดหวัง', 'โกรธ'],
            'compliment': ['ดี', 'เยี่ยม', 'สุดยอด', 'ยอดเยี่ยม', 'เจ๋ง', 'ชอบ', 'ประทับใจ'],
            'order_status': ['สถานะ', 'ออเดอร์', 'คำสั่งซื้อ', 'จัดส่ง', 'ส่งของ', 'ติดตาม'],
            'goodbye': ['ลาก่อน', 'บาย', 'แล้วเจอกัน', 'ขอบคุณ', 'จบ', 'เสร็จ']
        }
        
        self.english_keywords = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'greetings', 'welcome'],
            'product_inquiry': ['product', 'price', 'cost', 'buy', 'purchase', 'sell', 'item'],
            'support_request': ['help', 'support', 'assist', 'problem', 'issue', 'trouble', 'error'],
            'complaint': ['complain', 'bad', 'terrible', 'awful', 'worst', 'angry', 'disappointed'],
            'compliment': ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'impressed'],
            'order_status': ['order', 'status', 'delivery', 'shipped', 'track', 'shipping'],
            'goodbye': ['bye', 'goodbye', 'farewell', 'thanks', 'done', 'finished']
        }
        
        self.response_templates = {
            'th': {
                'greeting': 'สวัสดีครับ! ยินดีต้อนรับเข้าสู่ระบบลูกค้า Iris Origin 🙏 ผมพร้อมช่วยเหลือคุณครับ',
                'product_inquiry': 'เรามีสินค้าหลากหลายประเภท กรุณาระบุสินค้าที่สนใจ หรือดูรายละเอียดเพิ่มเติมได้ที่เว็บไซต์ครับ 🛍️',
                'support_request': 'ผมพร้อมช่วยแก้ไขปัญหาครับ กรุณาอธิบายปัญหาที่พบเป็นรายละเอียด เราจะดำเนินการแก้ไขให้เร็วที่สุด 🔧',
                'complaint': 'ขออภัยครับสำหรับปัญหาที่เกิดขึ้น เราจะนำข้อเสนะแนะของคุณไปปรับปรุงและแก้ไขให้ดีขึ้น 🙏',
                'compliment': 'ขอบคุณมากครับ! เราดีใจที่คุณพอใจกับบริการ เราจะพยายามให้บริการที่ดีต่อไป 😊',
                'order_status': 'กรุณาแจ้งหมายเลขคำสั่งซื้อครับ เราจะตรวจสอบสถานะการจัดส่งให้ทันที 📦',
                'goodbye': 'ขอบคุณครับ! หวังว่าจะได้รับใช้อีก หากมีคำถามเพิ่มเติม ติดต่อมาได้ตลอดเวลา 🙏',
                'unknown': 'ขออภัยครับ ผมไม่เข้าใจคำถาม กรุณาอธิบายเพิ่มเติม หรือติดต่อเจ้าหน้าที่ได้ครับ 🤔'
            },
            'en': {
                'greeting': 'Hello! Welcome to Iris Origin customer service 🙏 How can I assist you today?',
                'product_inquiry': 'We have various products available. Which one interests you? You can also check our website for more details 🛍️',
                'support_request': 'I\'m here to help! Please describe the issue you\'re facing in detail, and we\'ll resolve it quickly 🔧',
                'complaint': 'I sincerely apologize for the inconvenience. We\'ll take your feedback seriously and work to improve 🙏',
                'compliment': 'Thank you so much! We\'re delighted that you\'re satisfied with our service. We\'ll continue to serve you well 😊',
                'order_status': 'I can help check your order status. Please provide your order number and I\'ll track it immediately 📦',
                'goodbye': 'Goodbye! Feel free to reach out anytime if you have more questions. Thank you for choosing us 🙏',
                'unknown': 'I didn\'t quite understand that. Could you please clarify or contact our staff for assistance? 🤔'
            }
        }
        
        logger.info("✅ Simple AI Processor initialized successfully")
    
    async def initialize(self):
        """Async initialization if needed"""
        await asyncio.sleep(0.1)  # Simulate init
        logger.info("🚀 AI Processor fully initialized")
    
    async def process_message(self, message_text: str, user_id: str = "user") -> ProcessingResult:
        """Process message with lightweight AI"""
        start_time = datetime.now()
        
        try:
            # Language detection
            language = self._detect_language(message_text)
            
            # Intent classification
            intent, confidence = self._classify_intent(message_text, language)
            
            # Sentiment analysis
            sentiment, sentiment_score = self._analyze_sentiment(message_text)
            
            # Entity extraction
            entities = self._extract_entities(message_text)
            
            # Generate response
            response = self._generate_response(intent, language)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ProcessingResult(
                intent=intent,
                confidence=confidence,
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                language=language,
                entities=entities,
                suggested_response=response,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"❌ Processing error: {e}")
            return ProcessingResult(
                intent="error",
                confidence=0.0,
                sentiment="neutral", 
                sentiment_score=0.5,
                language="unknown",
                entities=[],
                suggested_response="ขออภัยครับ เกิดข้อผิดพลาด / Sorry, an error occurred",
                processing_time_ms=processing_time
            )
    
    def _detect_language(self, text: str) -> str:
        thai_pattern = re.compile(r'[\u0E00-\u0E7F]')
        thai_chars = len(thai_pattern.findall(text))
        english_pattern = re.compile(r'[a-zA-Z]')
        english_chars = len(english_pattern.findall(text))
        
        if thai_chars > english_chars:
            return "th"
        elif english_chars > 0:
            return "en"
        else:
            return "unknown"
    
    def _classify_intent(self, text: str, language: str) -> tuple:
        text_lower = text.lower()
        
        if language == "th":
            keywords = self.thai_keywords
        else:
            keywords = self.english_keywords
        
        intent_scores = {}
        
        for intent, intent_keywords in keywords.items():
            score = 0
            for keyword in intent_keywords:
                if keyword in text_lower:
                    score += 1
            
            if score > 0:
                confidence = min(0.9, score * 0.3)
                intent_scores[intent] = confidence
        
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
            return best_intent, confidence
        else:
            return "unknown", 0.5
    
    def _analyze_sentiment(self, text: str) -> tuple:
        positive_words = ['good', 'great', 'excellent', 'ดี', 'เยี่ยม', 'ยอด', 'ขอบคุณ', 'thank', 'love', 'like', 'ชอบ']
        negative_words = ['bad', 'terrible', 'awful', 'แย่', 'ไม่ดี', 'เสีย', 'บ่น', 'ร้องเรียน', 'angry', 'hate', 'เกลียด']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "positive", 0.7 + (pos_count * 0.1)
        elif neg_count > pos_count:
            return "negative", 0.3 - (neg_count * 0.1)
        else:
            return "neutral", 0.5
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        entities = []
        
        # Extract numbers (including Thai numbers)
        number_pattern = re.compile(r'\b\d+(?:\.\d+)?\b')
        numbers = number_pattern.findall(text)
        
        for number in numbers:
            entities.append({
                'text': number,
                'label': 'NUMBER',
                'confidence': 0.9
            })
        
        # Extract emails
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = email_pattern.findall(text)
        
        for email in emails:
            entities.append({
                'text': email,
                'label': 'EMAIL',
                'confidence': 0.95
            })
        
        # Extract phone numbers
        phone_pattern = re.compile(r'\b(?:\+?66|0)[\s-]?[0-9][\s-]?[0-9]{4}[\s-]?[0-9]{4}\b')
        phones = phone_pattern.findall(text)
        
        for phone in phones:
            entities.append({
                'text': phone,
                'label': 'PHONE',
                'confidence': 0.85
            })
        
        return entities
    
    def _generate_response(self, intent: str, language: str) -> str:
        try:
            templates = self.response_templates.get(language, self.response_templates['en'])
            return templates.get(intent, templates['unknown'])
        except:
            if language == 'th':
                return 'ขออภัยครับ ไม่สามารถสร้างคำตอบได้ในขณะนี้'
            else:
                return 'Sorry, I cannot generate a response right now'

# ===== PYDANTIC MODELS =====
class MessageRequest(BaseModel):
    """Customer message request"""
    message: str = Field(..., description="Customer message text", min_length=1, max_length=2000)
    user_id: str = Field(..., description="Customer user ID", min_length=1, max_length=100)
    platform: Optional[str] = Field("facebook", description="Platform (facebook, instagram, whatsapp)")

class ProcessingResponse(BaseModel):
    """AI processing response"""
    success: bool
    message_id: str
    intent: str
    confidence: float
    sentiment: str
    sentiment_score: float
    language: str
    entities: List[Dict[str, Any]]
    suggested_response: str
    processing_time_ms: float
    timestamp: str
    user_id: str
    platform: str

# ===== FASTAPI APPLICATION =====
app = FastAPI(
    title="Iris Origin - Simple AI Customer Service API",
    description="Lightweight AI customer service automation for Facebook Fan Pages",
    version="1.0.0-lite",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Variables
ai_processor = None
startup_time = datetime.now()

@app.on_event("startup")
async def startup_event():
    """Initialize AI processor on startup"""
    global ai_processor
    try:
        logger.info("🚀 Starting Iris Origin Simple AI API Server...")
        ai_processor = SimpleAIProcessor()
        await ai_processor.initialize()
        logger.info("✅ Simple AI Processor ready for production!")
        logger.info("🎯 Server ready at http://localhost:8000")
    except Exception as e:
        logger.error(f"❌ Failed to initialize AI processor: {e}")
        ai_processor = None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Iris Origin - Simple AI Customer Service API",
        "version": "1.0.0-lite",
        "status": "running",
        "description": "Lightweight AI customer service automation for Facebook Fan Pages",
        "features": [
            "Thai & English language support",
            "Intent classification",
            "Sentiment analysis",
            "Entity extraction",
            "Auto-response generation"
        ],
        "endpoints": {
            "process": "POST /api/v1/process - Process customer messages",
            "health": "GET /api/v1/health - Health check",
            "test": "GET /api/v1/test - Quick test endpoint",
            "docs": "GET /docs - API documentation"
        },
        "languages": ["Thai (ไทย)", "English"],
        "platforms": ["Facebook", "Instagram", "WhatsApp"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - startup_time).total_seconds()
    
    return {
        "status": "healthy" if ai_processor else "error",
        "version": "1.0.0-lite",
        "ai_processor": "ready" if ai_processor else "not_available",
        "uptime_seconds": uptime,
        "memory_usage": "lightweight",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """Quick test endpoint"""
    if not ai_processor:
        raise HTTPException(status_code=503, detail="AI processor not available")
    
    test_message = "สวัสดีครับ ผมต้องการทราบข้อมูลสินค้า"
    result = await ai_processor.process_message(test_message, "test_user")
    
    return {
        "success": True,
        "test_message": test_message,
        "result": {
            "intent": result.intent,
            "confidence": result.confidence,
            "language": result.language,
            "sentiment": result.sentiment,
            "response": result.suggested_response,
            "processing_time_ms": result.processing_time_ms
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/process", response_model=ProcessingResponse)
async def process_message(request: MessageRequest):
    """
    Process customer message with AI
    
    This endpoint handles customer service messages and returns:
    - Intent classification (greeting, product_inquiry, support_request, etc.)
    - Sentiment analysis (positive, negative, neutral)
    - Language detection (Thai, English)
    - Entity extraction (numbers, emails, phones)
    - AI-generated response
    """
    if not ai_processor:
        logger.error("❌ AI processor not available")
        raise HTTPException(
            status_code=503, 
            detail="AI processor not available. Please try again later."
        )
    
    try:
        # Generate unique message ID
        message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.user_id}"
        
        # Process with AI
        logger.info(f"🔄 Processing message for user: {request.user_id}")
        result = await ai_processor.process_message(
            message_text=request.message,
            user_id=request.user_id
        )
        
        # Create response
        response = ProcessingResponse(
            success=True,
            message_id=message_id,
            intent=result.intent,
            confidence=result.confidence,
            sentiment=result.sentiment,
            sentiment_score=result.sentiment_score,
            language=result.language,
            entities=result.entities,
            suggested_response=result.suggested_response,
            processing_time_ms=result.processing_time_ms,
            timestamp=datetime.now().isoformat(),
            user_id=request.user_id,
            platform=request.platform or "facebook"
        )
        
        logger.info(f"✅ Message processed successfully: {message_id} ({result.processing_time_ms:.2f}ms)")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

# Development Server
if __name__ == "__main__":
    print("🚀 Starting Iris Origin Simple AI API Server...")
    print("=" * 60)
    print("📋 Production-Lite Configuration:")
    print(f"   🌐 Host: 0.0.0.0")
    print(f"   🔌 Port: 8000") 
    print(f"   📖 Docs: http://localhost:8000/docs")
    print(f"   🔗 API: http://localhost:8000/api/v1/")
    print(f"   🧪 Test: http://localhost:8000/api/v1/test")
    print(f"   📊 Version: 1.0.0-lite (Lightweight)")
    print(f"   🇹🇭 Languages: Thai & English")
    print(f"   📱 Platforms: Facebook, Instagram, WhatsApp")
    print("=" * 60)
    
    uvicorn.run(
        "simple_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )