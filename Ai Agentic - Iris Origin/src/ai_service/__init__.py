"""
AI Service Package
==================

Enterprise-grade AI processing service for customer service automation.
"""

from .core import EnterpriseAIProcessor, ProcessingResult, IntentResult, SentimentResult
from .models import Message, ProcessedMessage, AIResponse, MessageType, Platform
from .utils import LanguageDetector, ConversationContextManager

__all__ = [
    'EnterpriseAIProcessor', 'ProcessingResult', 'IntentResult', 'SentimentResult',
    'Message', 'ProcessedMessage', 'AIResponse', 'MessageType', 'Platform',
    'LanguageDetector', 'ConversationContextManager'
]