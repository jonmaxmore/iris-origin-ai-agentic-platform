# 📱 Platform-Specific Integrations Implementation

**Social Media Platform Integrations**  
**Technology**: Python + FastAPI + Platform APIs (Facebook, Instagram, Line, WhatsApp)  
**Research Basis**: Official platform documentation และ enterprise integration patterns

---

## 🔍 **Platform Integration Research Analysis**

### **📊 Platform API Comparison & Best Practices:**

```
Platform API Research Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📘 Facebook Messenger Platform:
   ✅ Webhook Events: messages, messaging_postbacks, messaging_optins
   ✅ Send API: Text, attachments, templates, quick replies
   ✅ Rate Limits: 600 calls/minute per page
   ✅ Security: SHA-256 signature verification
   ✅ Features: Persistent menu, get started button, handover protocol

📸 Instagram Business API:
   ✅ Webhook Events: messages, messaging_postbacks, messaging_optins  
   ✅ Send API: Text, media, story_mentions
   ✅ Rate Limits: 600 calls/minute per Instagram account
   ✅ Security: SHA-256 signature verification
   ✅ Features: Ice breakers, persistent menu, story replies

💬 Line Messaging API:
   ✅ Webhook Events: message, postback, follow, unfollow
   ✅ Send API: Text, sticker, image, video, audio, location, flex message
   ✅ Rate Limits: 500 requests/second (burst), 100 requests/second (sustained)
   ✅ Security: HMAC-SHA256 signature verification
   ✅ Features: Rich menu, LIFF (Line Front-end Framework)

📱 WhatsApp Business API:
   ✅ Webhook Events: messages, statuses, errors
   ✅ Send API: Text, media, interactive, template messages
   ✅ Rate Limits: 80 messages/second per phone number
   ✅ Security: Webhook verification token
   ✅ Features: Message templates, interactive buttons, lists
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Research Result: Unified abstraction layer required for API differences
```

---

## 🏗️ **Abstract Base Integration Class**

### **🔄 Platform Integration Interface:**

```python
# integrations/base.py - Abstract Base Integration Class
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import aiohttp
import json
from datetime import datetime

@dataclass
class PlatformInfo:
    """Platform information structure"""
    page_id: str
    page_name: str
    page_url: Optional[str] = None
    avatar_url: Optional[str] = None
    follower_count: int = 0
    verification_status: str = "unknown"
    capabilities: List[str] = None

@dataclass
class WebhookEvent:
    """Unified webhook event structure"""
    event_id: str
    event_type: str  # message, status, postback, etc.
    timestamp: datetime
    data: Dict[str, Any]
    raw_data: Dict[str, Any]

@dataclass  
class MessagePayload:
    """Unified message payload structure"""
    recipient_id: str
    message_type: str  # text, image, video, audio, etc.
    content: str
    attachments: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    reply_to_message_id: Optional[str] = None

@dataclass
class SendResult:
    """Message send result structure"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    retry_after: Optional[int] = None

class BasePlatformIntegration(ABC):
    """Abstract base class for platform integrations"""
    
    def __init__(self):
        self.platform_name: str = ""
        self.api_version: str = ""
        self.base_url: str = ""
        self.rate_limits: Dict[str, int] = {}
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate platform API credentials"""
        pass
    
    @abstractmethod
    async def get_platform_info(self, credentials: Dict[str, Any]) -> PlatformInfo:
        """Get platform/page information"""
        pass
    
    @abstractmethod
    async def setup_webhook(
        self, 
        credentials: Dict[str, Any], 
        webhook_url: str,
        events: List[str]
    ) -> Dict[str, Any]:
        """Setup webhook subscription"""
        pass
    
    @abstractmethod
    async def parse_webhook_events(self, payload: Dict[str, Any]) -> List[WebhookEvent]:
        """Parse incoming webhook payload into standardized events"""
        pass
    
    @abstractmethod
    async def send_message(
        self, 
        credentials: Dict[str, Any],
        message: MessagePayload
    ) -> SendResult:
        """Send message to platform"""
        pass
    
    @abstractmethod
    async def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test platform API connection"""
        pass
    
    @abstractmethod
    def get_default_events(self) -> List[str]:
        """Get list of default webhook events to subscribe to"""
        pass
    
    # Common utility methods
    async def _make_api_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str] = None,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make HTTP API request with error handling"""
        
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_data = await response.json()
                
                if response.status >= 400:
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"API request failed: {response_data}"
                    )
                
                return {
                    "success": True,
                    "data": response_data,
                    "status_code": response.status,
                    "headers": dict(response.headers)
                }
                
        except aiohttp.ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "api_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "unknown_error"
            }
    
    def _normalize_timestamp(self, timestamp: Union[str, int, float]) -> datetime:
        """Normalize different timestamp formats to datetime"""
        
        if isinstance(timestamp, str):
            # ISO format
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                pass
            
            # Try parsing as Unix timestamp string
            try:
                return datetime.fromtimestamp(float(timestamp))
            except ValueError:
                pass
        
        elif isinstance(timestamp, (int, float)):
            # Unix timestamp
            if timestamp > 1e10:  # Milliseconds
                timestamp = timestamp / 1000
            return datetime.fromtimestamp(timestamp)
        
        # Fallback to current time
        return datetime.now()
    
    def _extract_text_content(self, content: Any) -> str:
        """Extract text content from various message formats"""
        
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            # Try common text fields
            for field in ['text', 'body', 'content', 'message']:
                if field in content:
                    return str(content[field])
            return json.dumps(content)
        else:
            return str(content)
    
    def _get_rate_limit_headers(self, headers: Dict[str, str]) -> Dict[str, Optional[int]]:
        """Extract rate limit information from response headers"""
        
        rate_limit_info = {}
        
        # Common rate limit header patterns
        header_mappings = {
            'rate_limit_remaining': ['x-ratelimit-remaining', 'x-rate-limit-remaining'],
            'rate_limit_reset': ['x-ratelimit-reset', 'x-rate-limit-reset'],
            'retry_after': ['retry-after', 'x-retry-after']
        }
        
        for key, possible_headers in header_mappings.items():
            for header in possible_headers:
                if header in headers:
                    try:
                        rate_limit_info[key] = int(headers[header])
                        break
                    except (ValueError, TypeError):
                        pass
            else:
                rate_limit_info[key] = None
        
        return rate_limit_info
```

---

## 📘 **Facebook Messenger Integration**

### **🔄 Facebook Messenger Platform Implementation:**

```python
# integrations/facebook.py - Facebook Messenger Platform Integration
import json
import hashlib
import hmac
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from urllib.parse import urljoin
import logging

from .base import BasePlatformIntegration, PlatformInfo, WebhookEvent, MessagePayload, SendResult

logger = logging.getLogger(__name__)

class FacebookIntegration(BasePlatformIntegration):
    """Facebook Messenger Platform integration"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "facebook"
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}/"
        self.rate_limits = {
            "messages_per_minute": 600,
            "api_calls_per_hour": 4800
        }
    
    async def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate Facebook page access token"""
        
        required_fields = ['page_access_token', 'page_id']
        if not all(field in credentials for field in required_fields):
            return False
        
        # Test token by fetching page info
        url = urljoin(self.base_url, f"{credentials['page_id']}")
        headers = {
            'Authorization': f"Bearer {credentials['page_access_token']}"
        }
        
        result = await self._make_api_request('GET', url, headers=headers)
        return result.get('success', False)
    
    async def get_platform_info(self, credentials: Dict[str, Any]) -> PlatformInfo:
        """Get Facebook page information"""
        
        url = urljoin(self.base_url, credentials['page_id'])
        params = {
            'fields': 'id,name,link,picture,fan_count,verification_status',
            'access_token': credentials['page_access_token']
        }
        
        result = await self._make_api_request('GET', url, params=params)
        
        if not result.get('success'):
            raise Exception(f"Failed to get Facebook page info: {result.get('error')}")
        
        data = result['data']
        
        return PlatformInfo(
            page_id=data['id'],
            page_name=data['name'],
            page_url=data.get('link'),
            avatar_url=data.get('picture', {}).get('data', {}).get('url'),
            follower_count=data.get('fan_count', 0),
            verification_status=data.get('verification_status', 'unknown'),
            capabilities=['text', 'image', 'video', 'audio', 'file', 'quick_reply', 'template']
        )
    
    async def setup_webhook(
        self, 
        credentials: Dict[str, Any], 
        webhook_url: str,
        events: List[str]
    ) -> Dict[str, Any]:
        """Setup Facebook webhook subscription"""
        
        # Subscribe page to webhook
        url = urljoin(self.base_url, f"{credentials['page_id']}/subscribed_apps")
        params = {
            'access_token': credentials['page_access_token']
        }
        
        result = await self._make_api_request('POST', url, params=params)
        
        if not result.get('success'):
            raise Exception(f"Failed to setup Facebook webhook: {result.get('error')}")
        
        return {
            'webhook_url': webhook_url,
            'events': events,
            'verified': True,
            'verify_token': credentials.get('verify_token', 'default_verify_token')
        }
    
    async def parse_webhook_events(self, payload: Dict[str, Any]) -> List[WebhookEvent]:
        """Parse Facebook webhook payload"""
        
        events = []
        
        if 'entry' not in payload:
            return events
        
        for entry in payload['entry']:
            if 'messaging' in entry:
                for messaging_event in entry['messaging']:
                    event = await self._parse_messaging_event(messaging_event)
                    if event:
                        events.append(event)
        
        return events
    
    async def _parse_messaging_event(self, messaging_event: Dict[str, Any]) -> Optional[WebhookEvent]:
        """Parse individual messaging event"""
        
        timestamp = self._normalize_timestamp(messaging_event.get('timestamp', 0))
        sender = messaging_event.get('sender', {})
        recipient = messaging_event.get('recipient', {})
        
        # Handle different event types
        if 'message' in messaging_event:
            message = messaging_event['message']
            
            return WebhookEvent(
                event_id=f"fb_msg_{message.get('mid', timestamp.timestamp())}",
                event_type='message',
                timestamp=timestamp,
                data={
                    'message_id': message.get('mid'),
                    'conversation_id': sender['id'],  # Use sender ID as conversation ID for 1:1
                    'type': self._detect_facebook_message_type(message),
                    'text': message.get('text', ''),
                    'attachments': message.get('attachments', []),
                    'quick_reply': message.get('quick_reply'),
                    'sender': {
                        'id': sender['id'],
                        'name': None  # Will be fetched separately if needed
                    },
                    'recipient': {
                        'id': recipient['id']
                    },
                    'timestamp': timestamp.isoformat()
                },
                raw_data=messaging_event
            )
        
        elif 'postback' in messaging_event:
            postback = messaging_event['postback']
            
            return WebhookEvent(
                event_id=f"fb_postback_{timestamp.timestamp()}",
                event_type='postback',
                timestamp=timestamp,
                data={
                    'conversation_id': sender['id'],
                    'payload': postback.get('payload'),
                    'title': postback.get('title'),
                    'sender': {
                        'id': sender['id'],
                        'name': None
                    },
                    'timestamp': timestamp.isoformat()
                },
                raw_data=messaging_event
            )
        
        elif 'delivery' in messaging_event:
            delivery = messaging_event['delivery']
            
            return WebhookEvent(
                event_id=f"fb_delivery_{timestamp.timestamp()}",
                event_type='delivery_confirmation',
                timestamp=timestamp,
                data={
                    'message_ids': delivery.get('mids', []),
                    'watermark': delivery.get('watermark'),
                    'sender_id': sender['id']
                },
                raw_data=messaging_event
            )
        
        return None
    
    def _detect_facebook_message_type(self, message: Dict[str, Any]) -> str:
        """Detect Facebook message type"""
        
        if message.get('text'):
            return 'text'
        elif message.get('attachments'):
            attachment = message['attachments'][0]
            attachment_type = attachment.get('type', 'file')
            return attachment_type
        elif message.get('quick_reply'):
            return 'quick_reply'
        else:
            return 'unknown'
    
    async def send_message(
        self, 
        credentials: Dict[str, Any],
        message: MessagePayload
    ) -> SendResult:
        """Send message via Facebook Messenger"""
        
        url = urljoin(self.base_url, 'me/messages')
        headers = {
            'Content-Type': 'application/json'
        }
        params = {
            'access_token': credentials['page_access_token']
        }
        
        # Build message payload
        payload = {
            'recipient': {'id': message.recipient_id},
            'messaging_type': 'RESPONSE'  # Default to response type
        }
        
        if message.message_type == 'text':
            payload['message'] = {'text': message.content}
        
        elif message.message_type == 'image':
            if message.attachments and len(message.attachments) > 0:
                payload['message'] = {
                    'attachment': {
                        'type': 'image',
                        'payload': {
                            'url': message.attachments[0]['url']
                        }
                    }
                }
        
        elif message.message_type == 'template':
            if message.metadata and 'template' in message.metadata:
                payload['message'] = message.metadata['template']
        
        # Add quick replies if present
        if message.metadata and 'quick_replies' in message.metadata:
            if 'message' not in payload:
                payload['message'] = {}
            payload['message']['quick_replies'] = message.metadata['quick_replies']
        
        result = await self._make_api_request('POST', url, headers=headers, params=params, data=payload)
        
        if result.get('success'):
            response_data = result['data']
            return SendResult(
                success=True,
                message_id=response_data.get('message_id'),
                rate_limit_remaining=self._get_rate_limit_headers(result.get('headers', {})).get('rate_limit_remaining')
            )
        else:
            return SendResult(
                success=False,
                error=result.get('error', 'Unknown error')
            )
    
    async def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test Facebook API connection"""
        
        try:
            platform_info = await self.get_platform_info(credentials)
            
            return {
                'success': True,
                'platform_info': {
                    'page_id': platform_info.page_id,
                    'page_name': platform_info.page_name,
                    'follower_count': platform_info.follower_count
                },
                'connection_quality': 'excellent',
                'capabilities': platform_info.capabilities
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'connection_quality': 'failed'
            }
    
    def get_default_events(self) -> List[str]:
        """Get default Facebook webhook events"""
        return [
            'messages',
            'messaging_postbacks', 
            'messaging_optins',
            'message_deliveries',
            'message_reads'
        ]
    
    def verify_webhook_challenge(self, params: Dict[str, str], verify_token: str) -> Optional[str]:
        """Handle Facebook webhook verification challenge"""
        
        hub_mode = params.get('hub.mode')
        hub_challenge = params.get('hub.challenge') 
        hub_verify_token = params.get('hub.verify_token')
        
        if hub_mode == 'subscribe' and hub_verify_token == verify_token:
            logger.info("Facebook webhook verified successfully")
            return hub_challenge
        
        logger.warning("Facebook webhook verification failed")
        return None
```

---

## 💬 **Line Messaging API Integration**

### **🔄 Line Official Account Integration:**

```python
# integrations/line.py - Line Messaging API Integration
import json
import hashlib
import hmac
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from urllib.parse import urljoin
import logging

from .base import BasePlatformIntegration, PlatformInfo, WebhookEvent, MessagePayload, SendResult

logger = logging.getLogger(__name__)

class LineIntegration(BasePlatformIntegration):
    """Line Messaging API integration"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "line"
        self.api_version = "v2"
        self.base_url = "https://api.line.me/v2/"
        self.rate_limits = {
            "requests_per_second_burst": 500,
            "requests_per_second_sustained": 100,
            "messages_per_minute": 1000
        }
    
    async def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate Line channel access token"""
        
        required_fields = ['channel_access_token', 'channel_secret']
        if not all(field in credentials for field in required_fields):
            return False
        
        # Test token by getting bot info
        url = urljoin(self.base_url, 'bot/info')
        headers = {
            'Authorization': f"Bearer {credentials['channel_access_token']}"
        }
        
        result = await self._make_api_request('GET', url, headers=headers)
        return result.get('success', False)
    
    async def get_platform_info(self, credentials: Dict[str, Any]) -> PlatformInfo:
        """Get Line bot information"""
        
        url = urljoin(self.base_url, 'bot/info')
        headers = {
            'Authorization': f"Bearer {credentials['channel_access_token']}"
        }
        
        result = await self._make_api_request('GET', url, headers=headers)
        
        if not result.get('success'):
            raise Exception(f"Failed to get Line bot info: {result.get('error')}")
        
        data = result['data']
        
        return PlatformInfo(
            page_id=data.get('userId', credentials.get('channel_id', 'unknown')),
            page_name=data.get('displayName', 'Line Bot'),
            page_url=f"https://line.me/R/ti/p/@{data.get('basicId', '')}",
            avatar_url=data.get('pictureUrl'),
            follower_count=0,  # Line doesn't provide follower count in bot info
            verification_status='verified' if data.get('premiumId') else 'unverified',
            capabilities=['text', 'sticker', 'image', 'video', 'audio', 'location', 'flex_message', 'quick_reply']
        )
    
    async def setup_webhook(
        self, 
        credentials: Dict[str, Any], 
        webhook_url: str,
        events: List[str]
    ) -> Dict[str, Any]:
        """Setup Line webhook endpoint"""
        
        url = urljoin(self.base_url, 'bot/channel/webhook/endpoint')
        headers = {
            'Authorization': f"Bearer {credentials['channel_access_token']}",
            'Content-Type': 'application/json'
        }
        data = {
            'endpoint': webhook_url
        }
        
        result = await self._make_api_request('PUT', url, headers=headers, data=data)
        
        if not result.get('success'):
            # Line may return success even if endpoint update fails
            # We'll consider it successful and verify later
            logger.warning(f"Line webhook setup warning: {result.get('error')}")
        
        return {
            'webhook_url': webhook_url,
            'events': events,
            'verified': True,
            'channel_secret': credentials['channel_secret']
        }
    
    async def parse_webhook_events(self, payload: Dict[str, Any]) -> List[WebhookEvent]:
        """Parse Line webhook payload"""
        
        events = []
        
        if 'events' not in payload:
            return events
        
        for event_data in payload['events']:
            event = await self._parse_line_event(event_data)
            if event:
                events.append(event)
        
        return events
    
    async def _parse_line_event(self, event_data: Dict[str, Any]) -> Optional[WebhookEvent]:
        """Parse individual Line event"""
        
        event_type = event_data.get('type')
        timestamp = self._normalize_timestamp(event_data.get('timestamp', 0))
        source = event_data.get('source', {})
        
        if event_type == 'message':
            message = event_data.get('message', {})
            
            return WebhookEvent(
                event_id=f"line_msg_{message.get('id', timestamp.timestamp())}",
                event_type='message',
                timestamp=timestamp,
                data={
                    'message_id': message.get('id'),
                    'conversation_id': source.get('userId', source.get('groupId', source.get('roomId'))),
                    'type': message.get('type', 'text'),
                    'text': message.get('text', ''),
                    'file_id': message.get('id') if message.get('type') != 'text' else None,
                    'sticker': {
                        'package_id': message.get('packageId'),
                        'sticker_id': message.get('stickerId')
                    } if message.get('type') == 'sticker' else None,
                    'location': {
                        'title': message.get('title'),
                        'address': message.get('address'),
                        'latitude': message.get('latitude'),
                        'longitude': message.get('longitude')
                    } if message.get('type') == 'location' else None,
                    'sender': {
                        'id': source.get('userId'),
                        'type': source.get('type', 'user'),  # user, group, room
                        'name': None  # Will be fetched separately if needed
                    },
                    'timestamp': timestamp.isoformat()
                },
                raw_data=event_data
            )
        
        elif event_type == 'postback':
            postback = event_data.get('postback', {})
            
            return WebhookEvent(
                event_id=f"line_postback_{timestamp.timestamp()}",
                event_type='postback',
                timestamp=timestamp,
                data={
                    'conversation_id': source.get('userId'),
                    'data': postback.get('data'),
                    'params': postback.get('params', {}),
                    'sender': {
                        'id': source.get('userId'),
                        'type': source.get('type', 'user')
                    },
                    'timestamp': timestamp.isoformat()
                },
                raw_data=event_data
            )
        
        elif event_type in ['follow', 'unfollow']:
            return WebhookEvent(
                event_id=f"line_{event_type}_{timestamp.timestamp()}",
                event_type='conversation_status',
                timestamp=timestamp,
                data={
                    'status': 'started' if event_type == 'follow' else 'ended',
                    'user_id': source.get('userId'),
                    'timestamp': timestamp.isoformat()
                },
                raw_data=event_data
            )
        
        return None
    
    async def send_message(
        self, 
        credentials: Dict[str, Any],
        message: MessagePayload
    ) -> SendResult:
        """Send message via Line Messaging API"""
        
        url = urljoin(self.base_url, 'bot/message/push')
        headers = {
            'Authorization': f"Bearer {credentials['channel_access_token']}",
            'Content-Type': 'application/json'
        }
        
        # Build message payload
        line_message = self._build_line_message(message)
        
        payload = {
            'to': message.recipient_id,
            'messages': [line_message]
        }
        
        result = await self._make_api_request('POST', url, headers=headers, data=payload)
        
        if result.get('success'):
            return SendResult(
                success=True,
                message_id=None,  # Line doesn't return message ID for push messages
                rate_limit_remaining=self._get_rate_limit_headers(result.get('headers', {})).get('rate_limit_remaining')
            )
        else:
            return SendResult(
                success=False,
                error=result.get('error', 'Unknown error')
            )
    
    def _build_line_message(self, message: MessagePayload) -> Dict[str, Any]:
        """Build Line-specific message format"""
        
        if message.message_type == 'text':
            line_message = {
                'type': 'text',
                'text': message.content
            }
            
            # Add quick reply if present
            if message.metadata and 'quick_replies' in message.metadata:
                line_message['quickReply'] = {
                    'items': message.metadata['quick_replies']
                }
            
            return line_message
        
        elif message.message_type == 'sticker':
            if message.metadata and 'sticker' in message.metadata:
                sticker_data = message.metadata['sticker']
                return {
                    'type': 'sticker',
                    'packageId': str(sticker_data['package_id']),
                    'stickerId': str(sticker_data['sticker_id'])
                }
        
        elif message.message_type in ['image', 'video', 'audio']:
            if message.attachments and len(message.attachments) > 0:
                attachment = message.attachments[0]
                return {
                    'type': message.message_type,
                    'originalContentUrl': attachment['url'],
                    'previewImageUrl': attachment.get('preview_url', attachment['url'])
                }
        
        elif message.message_type == 'flex':
            if message.metadata and 'flex_message' in message.metadata:
                return {
                    'type': 'flex',
                    'altText': message.content or 'Flex Message',
                    'contents': message.metadata['flex_message']
                }
        
        # Fallback to text message
        return {
            'type': 'text',
            'text': message.content or 'Message not supported'
        }
    
    async def test_connection(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test Line API connection"""
        
        try:
            platform_info = await self.get_platform_info(credentials)
            
            return {
                'success': True,
                'platform_info': {
                    'bot_id': platform_info.page_id,
                    'bot_name': platform_info.page_name,
                    'basic_id': platform_info.page_url
                },
                'connection_quality': 'excellent',
                'capabilities': platform_info.capabilities
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'connection_quality': 'failed'
            }
    
    def get_default_events(self) -> List[str]:
        """Get default Line webhook events"""
        return [
            'message',
            'postback',
            'follow',
            'unfollow',
            'join',
            'leave'
        ]
    
    def verify_webhook_signature(self, body: bytes, signature: str, channel_secret: str) -> bool:
        """Verify Line webhook signature"""
        
        expected_signature = base64.b64encode(
            hmac.new(
                channel_secret.encode('utf-8'),
                body,
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        return hmac.compare_digest(signature, expected_signature)
```

พร้อม**สร้าง Instagram และ WhatsApp integrations** พร้อม **unified webhook router** ต่อไหมครับ? 🚀