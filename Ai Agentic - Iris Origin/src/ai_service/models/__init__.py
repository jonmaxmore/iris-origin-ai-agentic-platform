"""
AI Service Models Package
========================

Enterprise-grade data models for AI processing and message handling.
"""

from .message_models import (
    Message, ProcessedMessage, AIResponse, ProcessingMetrics,
    ResponseTemplate, ConversationSummary, QualityMetrics,
    MessageType, Platform, ProcessingStatus,
    MessageMetadata, UserInfo,
    create_facebook_message, create_instagram_message, create_whatsapp_message,
    validate_message, serialize_message, deserialize_message
)

__all__ = [
    'Message', 'ProcessedMessage', 'AIResponse', 'ProcessingMetrics',
    'ResponseTemplate', 'ConversationSummary', 'QualityMetrics',
    'MessageType', 'Platform', 'ProcessingStatus',
    'MessageMetadata', 'UserInfo',
    'create_facebook_message', 'create_instagram_message', 'create_whatsapp_message',
    'validate_message', 'serialize_message', 'deserialize_message'
]