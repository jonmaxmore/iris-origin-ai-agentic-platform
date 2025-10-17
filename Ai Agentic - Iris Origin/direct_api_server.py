"""
Direct AI API Server
===================

Direct API server for AI processing without complex imports.

Author: Iris Origin AI Team
Date: 2025-01-17
Version: 1.0.0 Production
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Direct import of SimpleAIProcessor
import asyncio
import logging
import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Simple imports without heavy dependencies
try:
    from textblob import TextBlob
    import nltk
    from collections import Counter
    
    # Download required NLTK data
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('stopwords', quiet=True)
    except:
        pass
        
    print("✅ NLP libraries loaded successfully")
except Exception as e:
    print(f"⚠️ NLP libraries not available: {e}")
    TextBlob = None

# Initialize FastAPI
app = FastAPI(
    title="Iris Origin AI API",
    description="AI Processing API for customer service automation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@dataclass
class SimpleProcessingResult:
    """Simplified processing result"""
    intent: str
    confidence: float
    sentiment: str
    sentiment_score: float
    language: str
    entities: List[Dict[str, Any]]
    suggested_response: str
    processing_time_ms: float

class DirectAIProcessor:
    """Direct AI processor without heavy dependencies"""
    
    def __init__(self):
        self.thai_keywords = {
            'greeting': ['สวัสดี', 'หวัดดี', 'ดีครับ', 'ดีค่ะ', 'ยินดี', 'เฮ้', 'ฮัลโหล'],
            'product_inquiry': ['สินค้า', 'ผลิตภัณฑ์', 'ราคา', 'ค่าใช้จ่าย', 'เท่าไร', 'มี', 'จำหน่าย', 'ขาย'],
            'support_request': ['ช่วย', 'ช่วยเหลือ', 'แก้ไข', 'ปัญหา', 'ไม่ได้', 'เสีย', 'งาน', 'ทำ'],
            'complaint': ['บ่น', 'ร้องเรียน', 'แย่', 'ไม่ดี', 'แย่มาก', 'โง่', 'แป๊ด', 'ขยะ'],
            'compliment': ['ดี', 'เยี่ยม', 'สุดยอด', 'ยอดเยี่ยม', 'เจ๋ง', 'เลิศ', 'ประทับใจ', 'ชอบ'],
            'order_status': ['สถานะ', 'ออเดอร์', 'คำสั่งซื้อ', 'จัดส่ง', 'ส่งของ', 'ได้รับ', 'เมื่อไร'],
            'goodbye': ['ลาก่อน', 'บาย', 'แล้วเจอกัน', 'ไปก่อน', 'ขอบคุณ', 'จบ', 'เสร็จ']
        }
        
        self.english_keywords = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'greetings'],
            'product_inquiry': ['product', 'price', 'cost', 'buy', 'purchase', 'available', 'sell'],
            'support_request': ['help', 'support', 'assist', 'problem', 'issue', 'fix', 'broken'],
            'complaint': ['complain', 'bad', 'terrible', 'awful', 'worst', 'hate', 'angry'],
            'compliment': ['good', 'great', 'excellent', 'amazing', 'wonderful', 'perfect', 'love'],
            'order_status': ['order', 'status', 'delivery', 'shipped', 'track', 'when', 'arrive'],
            'goodbye': ['bye', 'goodbye', 'see you', 'farewell', 'thanks', 'done', 'finished']
        }
        
        self.response_templates = {
            'th': {
                'greeting': ['สวัสดีครับ! ยินดีต้อนรับเข้าสู่ระบบ Iris Origin', 'หวัดดีค่ะ! มีอะไรให้ช่วยเหลือไหมคะ'],
                'product_inquiry': ['เรามีสินค้าหลากหลายประเภท กรุณาระบุสินค้าที่สนใจครับ'],
                'support_request': ['ผมพร้อมช่วยแก้ไขปัญหาครับ กรุณาอธิบายปัญหาที่พบ'],
                'complaint': ['ขออภัยครับ เราจะปรับปรุงและแก้ไขให้ดีขึ้น'],
                'compliment': ['ขอบคุณมากครับ! เราดีใจที่คุณพอใจกับบริการ'],
                'order_status': ['กรุณาแจ้งหมายเลขคำสั่งซื้อครับ เราจะตรวจสอบสถานะให้'],
                'goodbye': ['ขอบคุณครับ! หวังว่าจะได้รับใช้อีก'],
                'unknown': ['ขออภัยครับ ผมไม่เข้าใจคำถาม กรุณาอธิบายเพิ่มเติม']
            },
            'en': {
                'greeting': ['Hello! Welcome to Iris Origin AI system', 'Hi there! How can I help you today?'],
                'product_inquiry': ['We have various products available. Which one interests you?'],
                'support_request': ['I\'m here to help! Please describe the issue you\'re facing'],
                'complaint': ['I apologize for the inconvenience. We\'ll work to improve'],
                'compliment': ['Thank you so much! We\'re glad you\'re satisfied'],
                'order_status': ['I can help check your order status. Please provide your order number'],
                'goodbye': ['Goodbye! Feel free to reach out anytime'],
                'unknown': ['I didn\'t understand that. Could you please clarify?']
            }
        }
        
        print("✅ Direct AI Processor initialized successfully")
    
    async def process_message(self, message_text: str, user_id: str = "test_user") -> SimpleProcessingResult:
        """Process message with direct AI"""
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
            
            return SimpleProcessingResult(
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
            return SimpleProcessingResult(
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
        if TextBlob:
            try:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                
                if polarity > 0.1:
                    sentiment = "positive"
                elif polarity < -0.1:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                
                score = (polarity + 1) / 2
                return sentiment, score
            except:
                pass
        
        # Fallback sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'ดี', 'เยี่ยม', 'ยอด']
        negative_words = ['bad', 'terrible', 'awful', 'แย่', 'ไม่ดี', 'เสีย']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "positive", 0.7
        elif neg_count > pos_count:
            return "negative", 0.3
        else:
            return "neutral", 0.5
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        entities = []
        
        # Extract numbers
        number_pattern = re.compile(r'\b\d+(?:\.\d+)?\b')
        numbers = number_pattern.findall(text)
        
        for number in numbers:
            entities.append({
                'text': number,
                'label': 'NUMBER',
                'confidence': 0.8
            })
        
        # Extract emails
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = email_pattern.findall(text)
        
        for email in emails:
            entities.append({
                'text': email,
                'label': 'EMAIL',
                'confidence': 0.9
            })
        
        return entities
    
    def _generate_response(self, intent: str, language: str) -> str:
        try:
            templates = self.response_templates.get(language, self.response_templates['en'])
            responses = templates.get(intent, templates['unknown'])
            
            import random
            return random.choice(responses)
        except:
            if language == 'th':
                return 'ขออภัยครับ ไม่สามารถสร้างคำตอบได้'
            else:
                return 'Sorry, I cannot generate a response right now'

# Initialize AI processor
try:
    ai_processor = DirectAIProcessor()
    print("✅ AI Processor ready for use")
except Exception as e:
    print(f"❌ Failed to initialize AI Processor: {e}")
    ai_processor = None

# Request/Response models
class MessageRequest(BaseModel):
    message: str
    user_id: str = "test_user"

class ProcessingResponse(BaseModel):
    success: bool
    intent: str
    confidence: float
    sentiment: str
    sentiment_score: float
    language: str
    entities: list
    suggested_response: str
    processing_time_ms: float

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Iris Origin AI API",
        "status": "running",
        "version": "1.0.0",
        "ai_processor": "available" if ai_processor else "unavailable"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_processor": "ready" if ai_processor else "error"
    }

@app.post("/api/process", response_model=ProcessingResponse)
async def process_message(request: MessageRequest):
    """Process message with AI engine"""
    
    if not ai_processor:
        raise HTTPException(status_code=503, detail="AI Processor not available")
    
    try:
        print(f"Processing: {request.message[:50]}...")
        
        result = await ai_processor.process_message(
            message_text=request.message,
            user_id=request.user_id
        )
        
        response = ProcessingResponse(
            success=True,
            intent=result.intent,
            confidence=result.confidence,
            sentiment=result.sentiment,
            sentiment_score=result.sentiment_score,
            language=result.language,
            entities=result.entities,
            suggested_response=result.suggested_response,
            processing_time_ms=result.processing_time_ms
        )
        
        print(f"✅ Result: {result.intent} ({result.language}) - {result.processing_time_ms:.1f}ms")
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Direct AI API Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")