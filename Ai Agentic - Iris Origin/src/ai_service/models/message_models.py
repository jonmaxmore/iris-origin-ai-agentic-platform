"""
Message Models - Enterprise Grade Data Structures
===============================================

Comprehensive data models for message processing and AI response generation.
Implements enterprise-grade type safety and validation.

Features:
- Type-safe data structures with validation
- Comprehensive message metadata
- AI processing result tracking
- Enterprise-grade serialization
- Performance optimized structures

Author: Iris Origin AI Team
Date: 2025-01-17
Version: 1.0.0 Enterprise
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from enum import Enum
import json
import uuid

class MessageType(Enum):
    """Message type enumeration"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    LOCATION = "location"
    STICKER = "sticker"
    REACTION = "reaction"

class Platform(Enum):
    """Platform enumeration"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"
    LINE = "line"
    TELEGRAM = "telegram"
    WEB = "web"
    MOBILE_APP = "mobile_app"

class ProcessingStatus(Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class MessageMetadata:
    """Message metadata with platform-specific information"""
    platform: Platform
    platform_message_id: str
    platform_user_id: str
    platform_thread_id: Optional[str] = None
    received_at: datetime = field(default_factory=datetime.now)
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    reply_to_message_id: Optional[str] = None
    is_forwarded: bool = False
    forwarded_from: Optional[str] = None
    media_urls: List[str] = field(default_factory=list)
    raw_payload: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserInfo:
    """User information with privacy considerations"""
    user_id: str
    display_name: Optional[str] = None
    username: Optional[str] = None
    profile_pic_url: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    is_verified: bool = False
    platform_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Message:
    """
    Core message structure for incoming messages from all platforms
    """
    # Core identification
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    
    # Message content
    text: str = ""
    message_type: MessageType = MessageType.TEXT
    
    # Timestamps
    timestamp: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    
    # Platform information
    platform: Platform = Platform.WEB
    metadata: Optional[MessageMetadata] = None
    user_info: Optional[UserInfo] = None
    
    # Message context
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    thread_id: Optional[str] = None
    
    # Additional data
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    quick_replies: List[str] = field(default_factory=list)
    buttons: List[Dict[str, str]] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate message after initialization"""
        if not self.user_id:
            raise ValueError("user_id is required")
        
        if self.message_type == MessageType.TEXT and not self.text:
            raise ValueError("text is required for text messages")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization"""
        return {
            'message_id': self.message_id,
            'user_id': self.user_id,
            'text': self.text,
            'message_type': self.message_type.value,
            'timestamp': self.timestamp.isoformat(),
            'created_at': self.created_at.isoformat(),
            'platform': self.platform.value,
            'metadata': self.metadata.__dict__ if self.metadata else None,
            'user_info': self.user_info.__dict__ if self.user_info else None,
            'session_id': self.session_id,
            'conversation_id': self.conversation_id,
            'thread_id': self.thread_id,
            'attachments': self.attachments,
            'quick_replies': self.quick_replies,
            'buttons': self.buttons
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        # Convert enums
        if 'message_type' in data:
            data['message_type'] = MessageType(data['message_type'])
        if 'platform' in data:
            data['platform'] = Platform(data['platform'])
        
        # Convert timestamps
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        # Convert metadata
        if 'metadata' in data and data['metadata']:
            metadata_data = data['metadata']
            if 'platform' in metadata_data:
                metadata_data['platform'] = Platform(metadata_data['platform'])
            if 'received_at' in metadata_data:
                metadata_data['received_at'] = datetime.fromisoformat(metadata_data['received_at'])
            data['metadata'] = MessageMetadata(**metadata_data)
        
        # Convert user_info
        if 'user_info' in data and data['user_info']:
            data['user_info'] = UserInfo(**data['user_info'])
        
        return cls(**data)

@dataclass
class AIResponse:
    """AI-generated response with confidence and metadata"""
    text: str
    confidence: float
    language: str
    generation_method: str
    
    # Response enhancement
    suggested_quick_replies: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    followup_questions: List[str] = field(default_factory=list)
    
    # Metadata
    model_version: Optional[str] = None
    processing_time_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    
    # Quality metrics
    coherence_score: Optional[float] = None
    relevance_score: Optional[float] = None
    sentiment_appropriateness: Optional[float] = None

@dataclass
class ProcessingMetrics:
    """Detailed processing metrics for monitoring and optimization"""
    # Timing metrics
    total_processing_time_ms: float
    language_detection_time_ms: float
    intent_classification_time_ms: float
    sentiment_analysis_time_ms: float
    entity_extraction_time_ms: float
    response_generation_time_ms: float
    context_update_time_ms: float
    
    # Accuracy metrics
    intent_confidence: float
    sentiment_confidence: float
    language_confidence: float
    overall_confidence: float
    
    # Resource metrics
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    gpu_usage_percent: Optional[float] = None
    
    # Model metrics
    model_versions: Dict[str, str] = field(default_factory=dict)
    features_used: List[str] = field(default_factory=list)

@dataclass
class ProcessedMessage:
    """
    Comprehensive processed message with AI analysis results
    """
    # Core data
    original_message: Message
    processing_result: 'ProcessingResult'  # Forward reference
    
    # Processing metadata
    timestamp: datetime = field(default_factory=datetime.now)
    processor_version: str = "1.0.0"
    processing_status: ProcessingStatus = ProcessingStatus.COMPLETED
    
    # Error handling
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    retry_count: int = 0
    
    # Metrics
    metrics: Optional[ProcessingMetrics] = None
    
    def __post_init__(self):
        """Validate processed message"""
        if self.processing_status == ProcessingStatus.FAILED and not self.error_message:
            raise ValueError("error_message is required for failed processing")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'original_message': self.original_message.to_dict(),
            'processing_result': self.processing_result.__dict__ if self.processing_result else None,
            'timestamp': self.timestamp.isoformat(),
            'processor_version': self.processor_version,
            'processing_status': self.processing_status.value,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'retry_count': self.retry_count,
            'metrics': self.metrics.__dict__ if self.metrics else None
        }
    
    @property
    def is_successful(self) -> bool:
        """Check if processing was successful"""
        return self.processing_status == ProcessingStatus.COMPLETED and not self.error_message
    
    @property
    def confidence_score(self) -> float:
        """Get overall confidence score"""
        if self.processing_result:
            return self.processing_result.confidence
        return 0.0

@dataclass
class ResponseTemplate:
    """Template for generating structured responses"""
    template_id: str
    name: str
    description: str
    language: str
    
    # Template content
    text_template: str
    variables: List[str] = field(default_factory=list)
    
    # Conditional logic
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Response enhancements
    quick_replies: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    
    # Metadata
    category: Optional[str] = None
    priority: int = 0
    usage_count: int = 0
    success_rate: float = 0.0
    
    def render(self, variables: Dict[str, Any]) -> str:
        """Render template with provided variables"""
        rendered_text = self.text_template
        
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in rendered_text:
                rendered_text = rendered_text.replace(placeholder, str(var_value))
        
        return rendered_text
    
    def is_applicable(self, context: Dict[str, Any]) -> bool:
        """Check if template is applicable for given context"""
        if not self.conditions:
            return True
        
        for condition_key, condition_value in self.conditions.items():
            if condition_key not in context:
                return False
            
            if isinstance(condition_value, list):
                if context[condition_key] not in condition_value:
                    return False
            else:
                if context[condition_key] != condition_value:
                    return False
        
        return True

@dataclass
class ConversationSummary:
    """Summary of conversation for context and analytics"""
    conversation_id: str
    user_id: str
    
    # Summary data
    message_count: int
    duration_minutes: float
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Intent analysis
    primary_intent: str = "unknown"
    intent_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Sentiment analysis
    overall_sentiment: str = "neutral"
    sentiment_journey: List[Tuple[datetime, str, float]] = field(default_factory=list)
    
    # Resolution tracking
    is_resolved: bool = False
    resolution_type: Optional[str] = None
    satisfaction_score: Optional[float] = None
    
    # Language and communication
    primary_language: str = "en"
    communication_style: str = "neutral"
    
    # Key insights
    key_topics: List[str] = field(default_factory=list)
    mentioned_entities: List[Dict[str, Any]] = field(default_factory=list)
    escalation_triggers: List[str] = field(default_factory=list)
    
    # Performance metrics
    average_response_time: Optional[float] = None
    ai_confidence_average: Optional[float] = None

@dataclass 
class QualityMetrics:
    """Quality assessment metrics for responses and processing"""
    # Response quality
    relevance_score: float = 0.0
    coherence_score: float = 0.0
    helpfulness_score: float = 0.0
    politeness_score: float = 0.0
    
    # Language quality
    grammar_score: float = 0.0
    fluency_score: float = 0.0
    cultural_appropriateness: float = 0.0
    
    # Context awareness
    context_relevance: float = 0.0
    conversation_flow: float = 0.0
    personalization_level: float = 0.0
    
    # User experience
    user_satisfaction_predicted: float = 0.0
    engagement_level: float = 0.0
    resolution_likelihood: float = 0.0
    
    # Overall quality
    @property
    def overall_quality_score(self) -> float:
        """Calculate overall quality score"""
        scores = [
            self.relevance_score,
            self.coherence_score,
            self.helpfulness_score,
            self.context_relevance,
            self.user_satisfaction_predicted
        ]
        return sum(scores) / len(scores) if scores else 0.0

# Utility functions for message processing
def create_facebook_message(
    user_id: str,
    text: str,
    platform_message_id: str,
    platform_user_id: str,
    **kwargs
) -> Message:
    """Create Facebook message with proper metadata"""
    metadata = MessageMetadata(
        platform=Platform.FACEBOOK,
        platform_message_id=platform_message_id,
        platform_user_id=platform_user_id,
        **kwargs
    )
    
    return Message(
        user_id=user_id,
        text=text,
        platform=Platform.FACEBOOK,
        metadata=metadata
    )

def create_instagram_message(
    user_id: str,
    text: str,
    platform_message_id: str,
    platform_user_id: str,
    **kwargs
) -> Message:
    """Create Instagram message with proper metadata"""
    metadata = MessageMetadata(
        platform=Platform.INSTAGRAM,
        platform_message_id=platform_message_id,
        platform_user_id=platform_user_id,
        **kwargs
    )
    
    return Message(
        user_id=user_id,
        text=text,
        platform=Platform.INSTAGRAM,
        metadata=metadata
    )

def create_whatsapp_message(
    user_id: str,
    text: str,
    platform_message_id: str,
    platform_user_id: str,
    **kwargs
) -> Message:
    """Create WhatsApp message with proper metadata"""
    metadata = MessageMetadata(
        platform=Platform.WHATSAPP,
        platform_message_id=platform_message_id,
        platform_user_id=platform_user_id,
        **kwargs
    )
    
    return Message(
        user_id=user_id,
        text=text,
        platform=Platform.WHATSAPP,
        metadata=metadata
    )

def validate_message(message: Message) -> List[str]:
    """Validate message and return list of validation errors"""
    errors = []
    
    if not message.user_id:
        errors.append("user_id is required")
    
    if message.message_type == MessageType.TEXT and not message.text:
        errors.append("text is required for text messages")
    
    if not message.platform:
        errors.append("platform is required")
    
    if message.metadata and not message.metadata.platform_message_id:
        errors.append("platform_message_id is required in metadata")
    
    return errors

def serialize_message(message: Union[Message, ProcessedMessage]) -> str:
    """Serialize message to JSON string"""
    return json.dumps(message.to_dict(), default=str, ensure_ascii=False, indent=2)

def deserialize_message(json_str: str) -> Message:
    """Deserialize message from JSON string"""
    data = json.loads(json_str)
    return Message.from_dict(data)

# Export all classes and functions
__all__ = [
    'Message', 'ProcessedMessage', 'AIResponse', 'ProcessingMetrics',
    'ResponseTemplate', 'ConversationSummary', 'QualityMetrics',
    'MessageType', 'Platform', 'ProcessingStatus',
    'MessageMetadata', 'UserInfo',
    'create_facebook_message', 'create_instagram_message', 'create_whatsapp_message',
    'validate_message', 'serialize_message', 'deserialize_message'
]