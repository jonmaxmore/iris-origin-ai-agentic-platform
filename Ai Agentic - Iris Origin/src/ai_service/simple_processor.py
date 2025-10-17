"""
Simplified AI Processing Engine - Production Ready
================================================

Simplified but fully functional AI processing engine that works immediately.
Uses lightweight models and proven approaches for immediate deployment.

Author: Iris Origin AI Team
Date: 2025-01-17
Version: 1.0.0 Production
"""

import asyncio
import logging
import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Simple imports without heavy dependencies
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

logger = logging.getLogger(__name__)

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

class SimpleAIProcessor:
    """
    Simplified AI processor that works immediately without complex model loading.
    Perfect for immediate testing and basic functionality.
    """
    
    def __init__(self):
        """Initialize simple AI processor"""
        self.thai_keywords = self._load_thai_keywords()
        self.english_keywords = self._load_english_keywords()
        self.response_templates = self._load_response_templates()
        
        logger.info("Simple AI Processor initialized successfully")
    
    def _load_thai_keywords(self) -> Dict[str, List[str]]:
        """Load Thai keyword patterns for intent classification"""
        return {
            'greeting': ['สวัสดี', 'หวัดดี', 'ดีครับ', 'ดีค่ะ', 'ยินดี', 'เฮ้', 'ฮัลโหล'],
            'product_inquiry': ['สินค้า', 'ผลิตภัณฑ์', 'ราคา', 'ค่าใช้จ่าย', 'เท่าไร', 'มี', 'จำหน่าย', 'ขาย'],
            'support_request': ['ช่วย', 'ช่วยเหลือ', 'แก้ไข', 'ปัญหา', 'ไม่ได้', 'เสีย', 'งาน', 'ทำ'],
            'complaint': ['บ่น', 'ร้องเรียน', 'แย่', 'ไม่ดี', 'แย่มาก', 'โง่', 'แป๊ด', 'ขยะ'],
            'compliment': ['ดี', 'เยี่ยม', 'สุดยอด', 'ยอดเยี่ยม', 'เจ๋ง', 'เลิศ', 'ประทับใจ', 'ชอบ'],
            'order_status': ['สถานะ', 'ออเดอร์', 'คำสั่งซื้อ', 'จัดส่ง', 'ส่งของ', 'ได้รับ', 'เมื่อไร'],
            'goodbye': ['ลาก่อน', 'บาย', 'แล้วเจอกัน', 'ไปก่อน', 'ขอบคุณ', 'จบ', 'เสร็จ']
        }
    
    def _load_english_keywords(self) -> Dict[str, List[str]]:
        """Load English keyword patterns for intent classification"""
        return {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'greetings'],
            'product_inquiry': ['product', 'price', 'cost', 'buy', 'purchase', 'available', 'sell'],
            'support_request': ['help', 'support', 'assist', 'problem', 'issue', 'fix', 'broken'],
            'complaint': ['complain', 'bad', 'terrible', 'awful', 'worst', 'hate', 'angry'],
            'compliment': ['good', 'great', 'excellent', 'amazing', 'wonderful', 'perfect', 'love'],
            'order_status': ['order', 'status', 'delivery', 'shipped', 'track', 'when', 'arrive'],
            'goodbye': ['bye', 'goodbye', 'see you', 'farewell', 'thanks', 'done', 'finished']
        }
    
    def _load_response_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Load response templates for different intents and languages"""
        return {
            'th': {
                'greeting': [
                    'สวัสดีครับ! ยินดีต้อนรับเข้าสู่ระบบ Iris Origin',
                    'หวัดดีค่ะ! มีอะไรให้ช่วยเหลือไหมคะ',
                    'สวัสดีครับ! ผมพร้อมช่วยเหลือคุณ'
                ],
                'product_inquiry': [
                    'เรามีสินค้าหลากหลายประเภท กรุณาระบุสินค้าที่สนใจครับ',
                    'ผลิตภัณฑ์ของเรามีให้เลือกมากมาย ต้องการทราบราคาสินค้าใดคะ',
                    'ยินดีให้ข้อมูลสินค้าครับ กรุณาบอกรายละเอียดที่ต้องการ'
                ],
                'support_request': [
                    'ผมพร้อมช่วยแก้ไขปัญหาครับ กรุณาอธิบายปัญหาที่พบ',
                    'เรายินดีช่วยเหลือค่ะ โปรดแจ้งรายละเอียดปัญหา',
                    'ทีมงานพร้อมให้ความช่วยเหลือครับ'
                ],
                'complaint': [
                    'ขออภัยครับ เราจะปรับปรุงและแก้ไขให้ดีขึ้น',
                    'เราเสียใจที่คุณไม่พอใจ จะนำไปพัฒนาให้ดีกว่านี้ค่ะ',
                    'ขอบคุณสำหรับข้อเสนอแนะครับ เราจะแก้ไขปรับปรุง'
                ],
                'compliment': [
                    'ขอบคุณมากครับ! เราดีใจที่คุณพอใจกับบริการ',
                    'ยินดีมากค่ะ! เราจะรักษามาตรฐานนี้ไว้',
                    'ขอบคุณครับ! กำลังใจนี้ช่วยเราพัฒนาต่อไป'
                ],
                'order_status': [
                    'กรุณาแจ้งหมายเลขคำสั่งซื้อครับ เราจะตรวจสอบสถานะให้',
                    'ต้องการเลขออเดอร์เพื่อตรวจสอบการจัดส่งค่ะ',
                    'ผมจะช่วยตรวจสอบสถานะการสั่งซื้อครับ'
                ],
                'goodbye': [
                    'ขอบคุณครับ! หวังว่าจะได้รับใช้อีก',
                    'ลาก่อนค่ะ! มีอะไรติดต่อได้เสมอ',
                    'แล้วเจอกันใหม่ครับ! สวัสดี'
                ],
                'unknown': [
                    'ขออภัยครับ ผมไม่เข้าใจคำถาม กรุณาอธิบายเพิ่มเติม',
                    'ขอโทษค่ะ ไม่เข้าใจ โปรดอธิบายใหม่',
                    'กรุณาอธิบายให้ชัดเจนกว่านี้ครับ'
                ]
            },
            'en': {
                'greeting': [
                    'Hello! Welcome to Iris Origin AI system',
                    'Hi there! How can I help you today?',
                    'Greetings! I\'m here to assist you'
                ],
                'product_inquiry': [
                    'We have various products available. Which one interests you?',
                    'I\'d be happy to help with product information. What are you looking for?',
                    'Please let me know which product you\'d like to know about'
                ],
                'support_request': [
                    'I\'m here to help! Please describe the issue you\'re facing',
                    'I\'ll assist you with that. Can you provide more details?',
                    'Our support team is ready to help. What\'s the problem?'
                ],
                'complaint': [
                    'I apologize for the inconvenience. We\'ll work to improve',
                    'Thank you for your feedback. We\'ll address this issue',
                    'I\'m sorry about that. We value your input for improvement'
                ],
                'compliment': [
                    'Thank you so much! We\'re glad you\'re satisfied',
                    'We appreciate your kind words! Thank you',
                    'That means a lot to us! Thanks for the feedback'
                ],
                'order_status': [
                    'I can help check your order status. Please provide your order number',
                    'Let me look up your order. What\'s your order ID?',
                    'I\'ll check the delivery status for you'
                ],
                'goodbye': [
                    'Goodbye! Feel free to reach out anytime',
                    'Thank you! Have a great day',
                    'See you next time! Take care'
                ],
                'unknown': [
                    'I didn\'t understand that. Could you please clarify?',
                    'I\'m not sure what you mean. Can you explain differently?',
                    'Please provide more details so I can help better'
                ]
            }
        }
    
    async def process_message(self, message_text: str, user_id: str = "test_user") -> SimpleProcessingResult:
        """Process message with simple but effective AI"""
        start_time = datetime.now()
        
        try:
            # Step 1: Language detection
            language = self._detect_language(message_text)
            
            # Step 2: Intent classification
            intent, intent_confidence = self._classify_intent(message_text, language)
            
            # Step 3: Sentiment analysis
            sentiment, sentiment_score = self._analyze_sentiment(message_text, language)
            
            # Step 4: Entity extraction
            entities = self._extract_entities(message_text)
            
            # Step 5: Generate response
            response = self._generate_response(intent, language, message_text)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return SimpleProcessingResult(
                intent=intent,
                confidence=intent_confidence,
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                language=language,
                entities=entities,
                suggested_response=response,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
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
        """Simple language detection"""
        # Count Thai characters
        thai_pattern = re.compile(r'[\u0E00-\u0E7F]')
        thai_chars = len(thai_pattern.findall(text))
        
        # Count English characters
        english_pattern = re.compile(r'[a-zA-Z]')
        english_chars = len(english_pattern.findall(text))
        
        # Simple heuristic
        if thai_chars > english_chars:
            return "th"
        elif english_chars > 0:
            return "en"
        else:
            return "unknown"
    
    def _classify_intent(self, text: str, language: str) -> tuple:
        """Simple keyword-based intent classification"""
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
                # Calculate confidence based on keyword matches
                confidence = min(0.9, score * 0.3)
                intent_scores[intent] = confidence
        
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
            return best_intent, confidence
        else:
            return "unknown", 0.5
    
    def _analyze_sentiment(self, text: str, language: str) -> tuple:
        """Simple sentiment analysis"""
        try:
            # Use TextBlob for basic sentiment analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            # Normalize score to 0-1 range
            score = (polarity + 1) / 2
            
            return sentiment, score
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return "neutral", 0.5
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Simple entity extraction"""
        entities = []
        
        # Extract numbers (potential prices, quantities, etc.)
        number_pattern = re.compile(r'\b\d+(?:\.\d+)?\b')
        numbers = number_pattern.findall(text)
        
        for number in numbers:
            entities.append({
                'text': number,
                'label': 'NUMBER',
                'confidence': 0.8
            })
        
        # Extract email addresses
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = email_pattern.findall(text)
        
        for email in emails:
            entities.append({
                'text': email,
                'label': 'EMAIL',
                'confidence': 0.9
            })
        
        # Extract phone numbers (basic pattern)
        phone_pattern = re.compile(r'\b(?:\+66|0)\d{8,9}\b')
        phones = phone_pattern.findall(text)
        
        for phone in phones:
            entities.append({
                'text': phone,
                'label': 'PHONE',
                'confidence': 0.9
            })
        
        return entities
    
    def _generate_response(self, intent: str, language: str, original_text: str) -> str:
        """Generate appropriate response based on intent"""
        try:
            templates = self.response_templates.get(language, self.response_templates['en'])
            responses = templates.get(intent, templates['unknown'])
            
            # Simple response selection (could be more sophisticated)
            import random
            selected_response = random.choice(responses)
            
            # Add personalization based on original text
            if 'ครับ' in original_text and language == 'th':
                if 'ครับ' not in selected_response:
                    selected_response += ' ครับ'
            elif 'ค่ะ' in original_text and language == 'th':
                if 'ค่ะ' not in selected_response:
                    selected_response = selected_response.replace('ครับ', 'ค่ะ')
            
            return selected_response
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            if language == 'th':
                return 'ขออภัยครับ ไม่สามารถสร้างคำตอบได้'
            else:
                return 'Sorry, I cannot generate a response right now'


# Export for use
__all__ = ['SimpleAIProcessor', 'SimpleProcessingResult']