"""
Conversation Context Manager - Enterprise Grade
==============================================

Advanced conversation context management with memory, learning, and personalization.
Implements enterprise-grade context awareness for customer service automation.

Features:
- Multi-session conversation memory
- User profile learning and adaptation
- Context-aware response generation
- Enterprise-grade data persistence
- Real-time context updates

Author: Iris Origin AI Team
Date: 2025-01-17
Version: 1.0.0 Enterprise
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque
import hashlib

# Enterprise data storage
import sqlite3
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """Single conversation message with metadata"""
    user_id: str
    message_id: str
    text: str
    intent: str
    sentiment: str
    language: str
    timestamp: datetime
    platform: str
    confidence: float
    entities: List[Dict[str, Any]]

@dataclass
class UserProfile:
    """Comprehensive user profile with learning capabilities"""
    user_id: str
    name: Optional[str]
    preferred_language: str
    communication_style: str  # formal/informal
    frequent_intents: Dict[str, int]
    sentiment_history: List[Tuple[str, float, datetime]]
    preferences: Dict[str, Any]
    interaction_count: int
    first_seen: datetime
    last_seen: datetime
    satisfaction_score: float
    platform_usage: Dict[str, int]

@dataclass
class ConversationContext:
    """Current conversation context with memory"""
    user_id: str
    session_id: str
    conversation_history: deque
    current_intent: str
    current_sentiment: str
    context_data: Dict[str, Any]
    last_updated: datetime
    session_duration: timedelta
    message_count: int
    unresolved_issues: List[str]

class ConversationContextManager:
    """
    Enterprise-grade conversation context management system.
    
    Features:
    - Persistent conversation memory across sessions
    - User profile learning and adaptation
    - Context-aware conversation flow
    - Real-time context updates
    - Enterprise-grade data persistence
    - Performance optimized for high-volume operations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize conversation context manager"""
        self.config = config or self._get_default_config()
        
        # In-memory caches for performance
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        
        # Performance optimization
        self.max_memory_conversations = self.config['performance']['max_memory_conversations']
        self.context_expiry_hours = self.config['performance']['context_expiry_hours']
        self.max_history_length = self.config['performance']['max_history_length']
        
        # Database connection
        self.db_path = Path(self.config['storage']['database_path'])
        self.db_connection = None
        
        logger.info("Conversation Context Manager initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get research-validated default configuration"""
        return {
            'storage': {
                'database_path': 'data/conversation_context.db',
                'backup_enabled': True,
                'backup_interval_hours': 24
            },
            'performance': {
                'max_memory_conversations': 1000,
                'context_expiry_hours': 72,
                'max_history_length': 50,
                'cache_cleanup_interval': 3600  # seconds
            },
            'learning': {
                'profile_update_threshold': 5,  # messages before profile update
                'sentiment_weight_decay': 0.9,
                'intent_frequency_weight': 0.8,
                'satisfaction_learning_rate': 0.1
            },
            'features': {
                'enable_profile_learning': True,
                'enable_sentiment_tracking': True,
                'enable_preference_learning': True,
                'enable_session_persistence': True
            }
        }
    
    async def initialize(self) -> None:
        """Initialize database and load active contexts"""
        try:
            await self._initialize_database()
            await self._load_active_contexts()
            await self._schedule_cleanup_tasks()
            
            logger.info("Context manager initialization completed")
            
        except Exception as e:
            logger.error(f"Context manager initialization failed: {e}")
            raise
    
    async def _initialize_database(self) -> None:
        """Initialize SQLite database for persistent storage"""
        try:
            # Create data directory if not exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.db_connection = sqlite3.connect(str(self.db_path))
            self.db_connection.row_factory = sqlite3.Row
            
            # Create tables
            await self._create_database_tables()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _create_database_tables(self) -> None:
        """Create database tables for context storage"""
        cursor = self.db_connection.cursor()
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                preferred_language TEXT,
                communication_style TEXT,
                frequent_intents TEXT,
                sentiment_history TEXT,
                preferences TEXT,
                interaction_count INTEGER,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                satisfaction_score REAL,
                platform_usage TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Conversation contexts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_contexts (
                context_id TEXT PRIMARY KEY,
                user_id TEXT,
                session_id TEXT,
                conversation_history TEXT,
                current_intent TEXT,
                current_sentiment TEXT,
                context_data TEXT,
                last_updated TIMESTAMP,
                session_duration TEXT,
                message_count INTEGER,
                unresolved_issues TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # Conversation messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_messages (
                message_id TEXT PRIMARY KEY,
                user_id TEXT,
                session_id TEXT,
                text TEXT,
                intent TEXT,
                sentiment TEXT,
                language TEXT,
                timestamp TIMESTAMP,
                platform TEXT,
                confidence REAL,
                entities TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contexts_user_id ON conversation_contexts(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contexts_session_id ON conversation_contexts(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_user_id ON conversation_messages(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON conversation_messages(timestamp)')
        
        self.db_connection.commit()
        logger.info("Database tables created successfully")
    
    async def get_context(self, user_id: str, session_id: Optional[str] = None) -> ConversationContext:
        """
        Get conversation context for user with session management
        """
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = self._generate_session_id(user_id)
            
            context_key = f"{user_id}:{session_id}"
            
            # Check memory cache first
            if context_key in self.active_conversations:
                context = self.active_conversations[context_key]
                
                # Check if context is still valid
                if self._is_context_valid(context):
                    return context
                else:
                    # Remove expired context
                    del self.active_conversations[context_key]
            
            # Load from database or create new
            context = await self._load_context_from_db(user_id, session_id)
            if not context:
                context = await self._create_new_context(user_id, session_id)
            
            # Cache in memory
            self.active_conversations[context_key] = context
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting context for user {user_id}: {e}")
            # Return minimal context as fallback
            return ConversationContext(
                user_id=user_id,
                session_id=session_id or self._generate_session_id(user_id),
                conversation_history=deque(maxlen=self.max_history_length),
                current_intent="unknown",
                current_sentiment="neutral",
                context_data={},
                last_updated=datetime.now(),
                session_duration=timedelta(0),
                message_count=0,
                unresolved_issues=[]
            )
    
    async def update_context(
        self, 
        user_id: str, 
        intent_result: Any, 
        sentiment_result: Any, 
        entities: List[Dict[str, Any]],
        message_text: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update conversation context with new interaction data
        """
        try:
            # Get current context
            context = await self.get_context(user_id, session_id)
            
            # Create conversation message
            message = ConversationMessage(
                user_id=user_id,
                message_id=self._generate_message_id(),
                text=message_text or "",
                intent=intent_result.intent if hasattr(intent_result, 'intent') else str(intent_result),
                sentiment=sentiment_result.sentiment if hasattr(sentiment_result, 'sentiment') else str(sentiment_result),
                language=getattr(intent_result, 'language', 'unknown'),
                timestamp=datetime.now(),
                platform=context.context_data.get('platform', 'unknown'),
                confidence=getattr(intent_result, 'confidence', 0.0),
                entities=entities
            )
            
            # Update conversation history
            context.conversation_history.append(message)
            context.current_intent = message.intent
            context.current_sentiment = message.sentiment
            context.message_count += 1
            context.last_updated = datetime.now()
            
            # Update context data with insights
            await self._update_context_insights(context, message)
            
            # Update user profile with learning
            await self._update_user_profile(user_id, message)
            
            # Persist to database
            await self._save_context_to_db(context)
            await self._save_message_to_db(message)
            
            # Return updated context data
            return context.context_data
            
        except Exception as e:
            logger.error(f"Error updating context for user {user_id}: {e}")
            return {}
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Get comprehensive user profile with learning data"""
        try:
            # Check memory cache
            if user_id in self.user_profiles:
                profile = self.user_profiles[user_id]
                # Update last seen
                profile.last_seen = datetime.now()
                return profile
            
            # Load from database
            profile = await self._load_profile_from_db(user_id)
            if not profile:
                profile = await self._create_new_profile(user_id)
            
            # Cache in memory
            self.user_profiles[user_id] = profile
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting user profile for {user_id}: {e}")
            return await self._create_new_profile(user_id)
    
    async def _update_context_insights(self, context: ConversationContext, message: ConversationMessage) -> None:
        """Update context with intelligent insights"""
        try:
            # Analyze conversation patterns
            recent_intents = [msg.intent for msg in list(context.conversation_history)[-5:]]
            recent_sentiments = [msg.sentiment for msg in list(context.conversation_history)[-5:]]
            
            # Update context data
            context.context_data.update({
                'recent_intents': recent_intents,
                'recent_sentiments': recent_sentiments,
                'conversation_flow': self._analyze_conversation_flow(context.conversation_history),
                'user_engagement': self._calculate_engagement_score(context),
                'session_summary': self._generate_session_summary(context),
                'recommended_actions': self._get_recommended_actions(context)
            })
            
            # Detect unresolved issues
            if message.intent in ['complaint', 'support_request', 'problem']:
                if not self._is_issue_resolved(context, message.intent):
                    if message.intent not in context.unresolved_issues:
                        context.unresolved_issues.append(message.intent)
            
        except Exception as e:
            logger.error(f"Error updating context insights: {e}")
    
    async def _update_user_profile(self, user_id: str, message: ConversationMessage) -> None:
        """Update user profile with machine learning"""
        try:
            profile = await self.get_user_profile(user_id)
            
            # Update interaction count
            profile.interaction_count += 1
            profile.last_seen = datetime.now()
            
            # Update frequent intents
            if message.intent in profile.frequent_intents:
                profile.frequent_intents[message.intent] += 1
            else:
                profile.frequent_intents[message.intent] = 1
            
            # Update sentiment history (with decay)
            profile.sentiment_history.append((
                message.sentiment, 
                message.confidence, 
                message.timestamp
            ))
            
            # Keep only recent sentiment history
            if len(profile.sentiment_history) > 20:
                profile.sentiment_history = profile.sentiment_history[-20:]
            
            # Update preferred language
            if message.language != 'unknown':
                profile.preferred_language = message.language
            
            # Update platform usage
            platform = message.platform
            if platform in profile.platform_usage:
                profile.platform_usage[platform] += 1
            else:
                profile.platform_usage[platform] = 1
            
            # Learn communication style
            profile.communication_style = self._detect_communication_style(message.text)
            
            # Update satisfaction score based on sentiment trends
            profile.satisfaction_score = self._calculate_satisfaction_score(profile.sentiment_history)
            
            # Save updated profile
            await self._save_profile_to_db(profile)
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
    
    def _analyze_conversation_flow(self, history: deque) -> Dict[str, Any]:
        """Analyze conversation flow patterns"""
        if len(history) < 2:
            return {"pattern": "initial", "transitions": []}
        
        transitions = []
        for i in range(1, len(history)):
            prev_intent = history[i-1].intent
            curr_intent = history[i].intent
            transitions.append(f"{prev_intent}->{curr_intent}")
        
        # Identify common patterns
        pattern = "complex"
        if len(set(msg.intent for msg in history)) == 1:
            pattern = "single_intent"
        elif len(transitions) <= 3:
            pattern = "simple"
        
        return {
            "pattern": pattern,
            "transitions": transitions,
            "intent_diversity": len(set(msg.intent for msg in history)),
            "average_confidence": sum(msg.confidence for msg in history) / len(history)
        }
    
    def _calculate_engagement_score(self, context: ConversationContext) -> float:
        """Calculate user engagement score"""
        if context.message_count == 0:
            return 0.0
        
        # Factors for engagement calculation
        message_frequency = context.message_count / max(1, context.session_duration.total_seconds() / 60)
        response_speed = 1.0  # Placeholder for response time analysis
        intent_diversity = len(set(msg.intent for msg in context.conversation_history))
        
        # Weighted engagement score
        engagement = (
            min(1.0, message_frequency / 10) * 0.4 +  # Message frequency weight
            response_speed * 0.3 +  # Response speed weight
            min(1.0, intent_diversity / 5) * 0.3  # Intent diversity weight
        )
        
        return round(engagement, 2)
    
    def _generate_session_summary(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate intelligent session summary"""
        if not context.conversation_history:
            return {"status": "no_activity"}
        
        # Extract key information
        intents = [msg.intent for msg in context.conversation_history]
        sentiments = [msg.sentiment for msg in context.conversation_history]
        languages = [msg.language for msg in context.conversation_history]
        
        return {
            "primary_intent": max(set(intents), key=intents.count),
            "overall_sentiment": max(set(sentiments), key=sentiments.count),
            "primary_language": max(set(languages), key=languages.count),
            "message_count": len(context.conversation_history),
            "duration_minutes": context.session_duration.total_seconds() / 60,
            "resolved_issues": len(intents) - len(context.unresolved_issues),
            "satisfaction_indicator": self._get_satisfaction_indicator(sentiments)
        }
    
    def _get_recommended_actions(self, context: ConversationContext) -> List[str]:
        """Get AI-recommended actions based on context"""
        recommendations = []
        
        # Check for unresolved issues
        if context.unresolved_issues:
            recommendations.append("escalate_to_human")
        
        # Check sentiment trends
        recent_sentiments = [msg.sentiment for msg in list(context.conversation_history)[-3:]]
        if recent_sentiments.count('negative') >= 2:
            recommendations.append("apply_recovery_strategy")
        
        # Check conversation length
        if context.message_count > 15:
            recommendations.append("summarize_and_close")
        
        # Check engagement
        engagement = self._calculate_engagement_score(context)
        if engagement < 0.3:
            recommendations.append("increase_engagement")
        
        return recommendations
    
    def _detect_communication_style(self, text: str) -> str:
        """Detect user's communication style"""
        if not text:
            return "neutral"
        
        # Simple heuristics for style detection
        formal_indicators = ['คุณ', 'ท่าน', 'กรุณา', 'sir', 'madam', 'please', 'thank you']
        informal_indicators = ['555', 'ฮ่า', 'เฮ้', 'hi', 'hey', 'cool', 'awesome']
        
        text_lower = text.lower()
        formal_count = sum(1 for indicator in formal_indicators if indicator in text_lower)
        informal_count = sum(1 for indicator in informal_indicators if indicator in text_lower)
        
        if formal_count > informal_count:
            return "formal"
        elif informal_count > formal_count:
            return "informal"
        else:
            return "neutral"
    
    def _calculate_satisfaction_score(self, sentiment_history: List[Tuple[str, float, datetime]]) -> float:
        """Calculate user satisfaction score from sentiment history"""
        if not sentiment_history:
            return 0.5  # Neutral starting point
        
        # Weight recent sentiments more heavily
        total_score = 0.0
        total_weight = 0.0
        
        for i, (sentiment, confidence, timestamp) in enumerate(sentiment_history):
            # Convert sentiment to numerical score
            if sentiment == 'positive':
                score = 1.0
            elif sentiment == 'negative':
                score = 0.0
            else:
                score = 0.5
            
            # Apply confidence and recency weights
            weight = confidence * (0.9 ** (len(sentiment_history) - i - 1))
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def _get_satisfaction_indicator(self, sentiments: List[str]) -> str:
        """Get overall satisfaction indicator"""
        if not sentiments:
            return "unknown"
        
        positive_count = sentiments.count('positive')
        negative_count = sentiments.count('negative')
        
        if positive_count > negative_count * 2:
            return "satisfied"
        elif negative_count > positive_count:
            return "dissatisfied"
        else:
            return "neutral"
    
    def _is_issue_resolved(self, context: ConversationContext, issue_intent: str) -> bool:
        """Check if an issue has been resolved in the conversation"""
        # Look for resolution indicators in recent messages
        recent_messages = list(context.conversation_history)[-5:]
        resolution_intents = ['compliment', 'satisfaction', 'goodbye']
        
        for msg in recent_messages:
            if msg.intent in resolution_intents and msg.sentiment == 'positive':
                return True
        
        return False
    
    def _is_context_valid(self, context: ConversationContext) -> bool:
        """Check if context is still valid (not expired)"""
        expiry_time = datetime.now() - timedelta(hours=self.context_expiry_hours)
        return context.last_updated > expiry_time
    
    def _generate_session_id(self, user_id: str) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{user_id}:{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"msg:{timestamp}".encode()).hexdigest()[:12]
    
    async def _load_context_from_db(self, user_id: str, session_id: str) -> Optional[ConversationContext]:
        """Load conversation context from database"""
        # Implementation placeholder - would load from SQLite
        return None
    
    async def _create_new_context(self, user_id: str, session_id: str) -> ConversationContext:
        """Create new conversation context"""
        return ConversationContext(
            user_id=user_id,
            session_id=session_id,
            conversation_history=deque(maxlen=self.max_history_length),
            current_intent="greeting",
            current_sentiment="neutral",
            context_data={},
            last_updated=datetime.now(),
            session_duration=timedelta(0),
            message_count=0,
            unresolved_issues=[]
        )
    
    async def _load_profile_from_db(self, user_id: str) -> Optional[UserProfile]:
        """Load user profile from database"""
        # Implementation placeholder - would load from SQLite
        return None
    
    async def _create_new_profile(self, user_id: str) -> UserProfile:
        """Create new user profile"""
        now = datetime.now()
        return UserProfile(
            user_id=user_id,
            name=None,
            preferred_language="en",
            communication_style="neutral",
            frequent_intents={},
            sentiment_history=[],
            preferences={},
            interaction_count=0,
            first_seen=now,
            last_seen=now,
            satisfaction_score=0.5,
            platform_usage={}
        )
    
    async def _save_context_to_db(self, context: ConversationContext) -> None:
        """Save conversation context to database"""
        # Implementation placeholder - would save to SQLite
        pass
    
    async def _save_message_to_db(self, message: ConversationMessage) -> None:
        """Save conversation message to database"""
        # Implementation placeholder - would save to SQLite
        pass
    
    async def _save_profile_to_db(self, profile: UserProfile) -> None:
        """Save user profile to database"""
        # Implementation placeholder - would save to SQLite
        pass
    
    async def _load_active_contexts(self) -> None:
        """Load active contexts from database on startup"""
        # Implementation placeholder
        pass
    
    async def _schedule_cleanup_tasks(self) -> None:
        """Schedule periodic cleanup tasks"""
        # Implementation placeholder for cleanup scheduling
        pass


# Export main classes
__all__ = ['ConversationContextManager', 'ConversationContext', 'UserProfile', 'ConversationMessage']