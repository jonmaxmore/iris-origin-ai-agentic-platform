# การเชื่อมต่อแพลตฟอร์ม: ข้อกำหนดทางเทคนิคของ API

## ภาพรวม

ส่วนนี้จะให้รายละเอียดทางเทคนิคสำหรับการเชื่อมต่อกับ Facebook และระบบภายในที่จำเป็น เพื่อให้ระบบ AI Agentic สามารถทำงานได้อย่างมีประสิทธิภาพและเป็นไปตามมาตรฐาน

## 5.1 การเชื่อมต่อแพลตฟอร์ม Facebook Messenger

### การยืนยันตัวตน (Authentication)

ระบบจะใช้ **Page Access Tokens** พร้อมสิทธิ์ที่จำเป็นตามที่ Facebook กำหนด

#### สิทธิ์ที่จำเป็น:
- `pages_messaging` - ส่งและรับข้อความ
- `pages_read_engagement` - อ่านการมีส่วนร่วม
- `pages_manage_metadata` - จัดการข้อมูลเมตา
- `pages_read_user_content` - อ่านเนื้อหาจากผู้ใช้

### Webhooks Configuration

การกำหนดค่า **Webhook Endpoint** ที่ปลอดภัยเพื่อรับเหตุการณ์แบบเรียลไทม์จาก Facebook

#### ความต้องการด้านความปลอดภัย:
1. **HTTPS เท่านั้น** - Facebook ยอมรับเฉพาะ HTTPS
2. **SSL Certificate ที่ถูกต้อง** - ต้องเป็น Certificate ที่น่าเชื่อถือ
3. **Webhook Verification** - ตรวจสอบลายเซ็นของคำขอ

#### โครงสร้าง Webhook Endpoint:

```
POST https://your-domain.com/webhook/facebook
Content-Type: application/json
X-Hub-Signature-256: sha256=<signature>

{
  "object": "page",
  "entry": [
    {
      "id": "PAGE_ID",
      "time": 1458692752478,
      "messaging": [
        {
          "sender": {"id": "USER_ID"},
          "recipient": {"id": "PAGE_ID"},
          "timestamp": 1458692752478,
          "message": {
            "mid": "mid.1457764197618:41d102a3e1ae206a38",
            "text": "hello, world!",
            "quick_reply": {
              "payload": "DEVELOPER_DEFINED_PAYLOAD"
            }
          }
        }
      ]
    }
  ]
}
```

## 5.2 API ที่สำคัญของ Facebook

### 5.2.1 Send API

**เป็นเครื่องมือหลักในการส่งข้อความขาออกทั้งหมด**

#### Endpoint:
```
POST https://graph.facebook.com/v18.0/me/messages?access_token=PAGE_ACCESS_TOKEN
```

#### โครงสร้างคำขอ:

```json
{
  "recipient": {
    "id": "USER_PSID"
  },
  "messaging_type": "RESPONSE",
  "message": {
    "text": "Hello World"
  }
}
```

#### ประเภทข้อความที่สนับสนุน:

**1. Text Messages:**
```json
{
  "message": {
    "text": "สวัสดีครับ! มีอะไรให้ช่วยเหลือไหมครับ?"
  }
}
```

**2. Quick Replies:**
```json
{
  "message": {
    "text": "คุณต้องการความช่วยเหลือเรื่องใด?",
    "quick_replies": [
      {
        "content_type": "text",
        "title": "ดาวน์โหลดเกม",
        "payload": "DOWNLOAD_GAME"
      },
      {
        "content_type": "text", 
        "title": "รายงานปัญหา",
        "payload": "REPORT_ISSUE"
      }
    ]
  }
}
```

**3. Message Templates:**
```json
{
  "message": {
    "attachment": {
      "type": "template",
      "payload": {
        "template_type": "generic",
        "elements": [
          {
            "title": "ข้อมูลเกม",
            "subtitle": "ดูข้อมูลล่าสุดของเกม",
            "image_url": "https://example.com/game-image.jpg",
            "buttons": [
              {
                "type": "web_url",
                "url": "https://example.com/game-info",
                "title": "ดูเพิ่มเติม"
              }
            ]
          }
        ]
      }
    }
  }
}
```

### 5.2.2 Conversations API

**ใช้เพื่อดึงประวัติการสนทนาสำหรับผู้ใช้ที่ระบุ**

#### Endpoint:
```
GET https://graph.facebook.com/v18.0/me/conversations?user_id=USER_ID&access_token=PAGE_ACCESS_TOKEN
```

#### การใช้งาน:
- ดึงประวัติการสนทนาเพื่อเป็นหน่วยความจำระยะยาว
- ให้ Agent มีบริบทจากการสนทนาที่ผ่านมา
- สร้างความต่อเนื่องในการให้บริการ

#### ตัวอย่างการตอบกลับ:
```json
{
  "data": [
    {
      "id": "t_1001",
      "participants": {
        "data": [
          {"name": "User Name", "id": "USER_ID"},
          {"name": "Page Name", "id": "PAGE_ID"}
        ]
      },
      "updated_time": "2023-10-15T10:30:00+0000"
    }
  ]
}
```

### 5.2.3 Handover Protocol API

**จำเป็นสำหรับการจัดการการเปลี่ยนผ่านระหว่าง AI Agent และเจ้าหน้าที่ CS ที่เป็นมนุษย์**

#### Pass Thread Control:
```
POST https://graph.facebook.com/v18.0/me/pass_thread_control?access_token=PAGE_ACCESS_TOKEN

{
  "recipient": {"id": "USER_PSID"},
  "target_app_id": "HUMAN_AGENT_APP_ID",
  "metadata": "การส่งต่อเนื่องจากปัญหาซับซ้อน"
}
```

#### Take Thread Control:
```
POST https://graph.facebook.com/v18.0/me/take_thread_control?access_token=PAGE_ACCESS_TOKEN

{
  "recipient": {"id": "USER_PSID"},
  "metadata": "AI Agent เข้าสู่การควบคุมอีกครั้ง"
}
```

## 5.3 การปฏิบัติตามนโยบายการส่งข้อความ

### หน้าต่าง 24 ชั่วโมง (24-Hour Window)

**กฎสำคัญ**: ข้อความทั้งหมด (รวมถึงข้อความส่งเสริมการขาย) จะต้องถูกส่งภายใน 24 ชั่วโมงหลังจากการโต้ตอบล่าสุดของผู้ใช้

#### Messaging Types ในหน้าต่าง 24 ชั่วโมง:

**1. RESPONSE:**
```json
{
  "messaging_type": "RESPONSE",
  "message": {
    "text": "ขอบคุณสำหรับคำถามครับ เกมจะเปิดให้บริการวันที่ 15 ตุลาคมนี้"
  }
}
```

**2. UPDATE:**
```json
{
  "messaging_type": "UPDATE", 
  "message": {
    "text": "ข้อมูลบัญชีของคุณได้รับการอัปเดตเรียบร้อยแล้ว"
  }
}
```

#### การรีเซ็ตหน้าต่าง:
หน้าต่างนี้จะ**รีเซ็ตทุกครั้งที่มีข้อความใหม่จากผู้ใช้**

### แท็กข้อความ (Message Tags)

**สำหรับการส่งข้อความที่ไม่ใช่การส่งเสริมการขาย นอกหน้าต่าง 24 ชั่วโมง**

#### แท็กที่สำคัญ:

**1. ACCOUNT_UPDATE:**
```json
{
  "messaging_type": "MESSAGE_TAG",
  "tag": "ACCOUNT_UPDATE",
  "message": {
    "text": "รหัสผ่านของคุณถูกรีเซ็ตเรียบร้อยแล้ว กรุณาตรวจสอบอีเมล"
  }
}
```

**2. POST_PURCHASE_UPDATE:**
```json
{
  "messaging_type": "MESSAGE_TAG", 
  "tag": "POST_PURCHASE_UPDATE",
  "message": {
    "text": "การซื้อไอเทมในเกมของคุณสำเร็จแล้ว ไอเทมจะถูกเพิ่มในบัญชีภายใน 5 นาที"
  }
}
```

**3. HUMAN_AGENT:**
```json
{
  "messaging_type": "MESSAGE_TAG",
  "tag": "HUMAN_AGENT", 
  "message": {
    "text": "สวัสดีครับ ผมคือเจ้าหน้าที่ CS จะช่วยแก้ไขปัญหาให้คุณครับ"
  }
}
```

**คำเตือน**: การใช้แท็กเหล่านี้ในทางที่ผิดอาจนำไปสู่การจำกัดการใช้งานของเพจ ดังนั้นตรรกะทางธุรกิจจะต้องมีความเข้มงวด

## 5.4 การเชื่อมต่อระบบภายใน (ข้อกำหนดของ API)

### ข้อกำหนดทั่วไป

ทีมพัฒนาจะต้องสร้าง **API Endpoints ภายในแบบ RESTful** หลายตัวเพื่อให้ Agent ใช้งานได้ ซึ่งจะต้องมี:

- **ความปลอดภัย** - Authentication และ Authorization ที่เหมาะสม
- **เอกสารประกอบที่ดี** - API Documentation ที่ครบถ้วน
- **ความหน่วงต่ำ (Low-latency)** - เวลาตอบสนองที่รวดเร็ว

### 5.4.1 Game Database API

#### GET /api/game/info
**วัตถุประสงค์**: ส่งคืนข้อมูลสำคัญของเกม

**ตัวอย่างการตอบกลับ:**
```json
{
  "status": "success",
  "data": {
    "launch_date": "2024-10-15T00:00:00Z",
    "current_version": "2.1.5",
    "server_status": {
      "asia": "online",
      "europe": "maintenance", 
      "america": "online"
    },
    "download_links": {
      "ios": "https://apps.apple.com/app/game",
      "android": "https://play.google.com/store/apps/game",
      "pc": "https://game-website.com/download"
    },
    "latest_news": {
      "title": "ซีซั่นใหม่ Dragon's Fury",
      "url": "https://game-website.com/news/dragons-fury"
    }
  }
}
```

#### GET /api/game/server-status
**วัตถุประสงค์**: ตรวจสอบสถานะเซิร์ฟเวอร์แบบเรียลไทม์

```json
{
  "status": "success",
  "data": {
    "servers": [
      {
        "region": "asia-pacific",
        "status": "online", 
        "players_online": 15420,
        "queue_time": "0 minutes"
      },
      {
        "region": "europe",
        "status": "maintenance",
        "estimated_completion": "2024-10-15T14:00:00Z",
        "reason": "Game update deployment"
      }
    ]
  }
}
```

### 5.4.2 Customer Relationship Management API

#### GET /api/player/{psid}/history
**วัตถุประสงค์**: ดึงข้อมูลสรุปประวัติการโต้ตอบของผู้เล่นจาก CRM

**Parameters:**
- `psid` (string): Page-Scoped ID ของผู้ใช้
- `limit` (integer): จำนวนบันทึกที่ต้องการ (default: 10)
- `include_resolved` (boolean): รวมปัญหาที่แก้ไขแล้ว (default: true)

**ตัวอย่างการตอบกลับ:**
```json
{
  "status": "success",
  "data": {
    "player_id": "player_12345",
    "total_interactions": 23,
    "recent_interactions": [
      {
        "date": "2024-10-10T15:30:00Z",
        "issue_type": "download_problem",
        "status": "resolved",
        "resolution_time": "00:15:30",
        "satisfaction_score": 5
      },
      {
        "date": "2024-10-08T09:20:00Z", 
        "issue_type": "payment_issue",
        "status": "escalated_to_billing",
        "agent_notes": "Need manual verification"
      }
    ],
    "player_segments": ["premium", "long_term"],
    "preferred_language": "th",
    "timezone": "Asia/Bangkok"
  }
}
```

### 5.4.3 Support Ticketing API

#### POST /api/support/ticket
**วัตถุประสงค์**: สร้างตั๋วสนับสนุนใหม่

**Request Body:**
```json
{
  "psid": "USER_PSID",
  "issue_category": "technical_support",
  "priority": "medium",
  "subject": "Cannot download game on iOS",
  "description": "User reports app crashes during download",
  "conversation_log": [
    {
      "timestamp": "2024-10-15T10:00:00Z",
      "sender": "user",
      "message": "ช่วยหน่อยครับ ดาวน์โหลดเกมไม่ได้"
    },
    {
      "timestamp": "2024-10-15T10:01:00Z", 
      "sender": "bot",
      "message": "ขออภัยที่เกิดปัญหานี้ขึ้น คุณใช้อุปกรณ์อะไรครับ?"
    }
  ],
  "ai_analysis": {
    "detected_intent": "download_issue",
    "confidence": 0.95,
    "suggested_category": "technical_support",
    "keywords": ["download", "iOS", "crash"]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "ticket_id": "TK-2024-001234",
    "assigned_agent": "agent_thai_01",
    "estimated_resolution": "2024-10-15T16:00:00Z",
    "tracking_url": "https://support.game.com/ticket/TK-2024-001234"
  }
}
```

### 5.4.4 Knowledge Base Search API

#### GET /api/kb/search
**วัตถุประสงค์**: Endpoint สำหรับการค้นหาเชิงความหมาย (Semantic Search) ในฐานความรู้ภายใน

**Parameters:**
- `query` (string): ข้อความที่ต้องการค้นหา
- `language` (string): ภาษาที่ต้องการ (th, en, zh, id)
- `category` (string): หมวดหมู่ที่ต้องการค้นหา
- `limit` (integer): จำนวนผลลัพธ์สูงสุด

**Example Request:**
```
GET /api/kb/search?query=วิธีการดาวน์โหลดเกม&language=th&limit=5
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "id": "kb_001",
        "title": "วิธีการดาวน์โหลดเกมบน iOS",
        "content": "สำหรับอุปกรณ์ iOS โปรดไปที่ App Store...",
        "category": "download_guide",
        "relevance_score": 0.98,
        "url": "https://help.game.com/download-ios"
      },
      {
        "id": "kb_002", 
        "title": "แก้ไขปัญหาดาวน์โหลดไม่สำเร็จ",
        "content": "หากเกิดปัญหาในการดาวน์โหลด กรุณาทำตามขั้นตอนนี้...",
        "category": "troubleshooting",
        "relevance_score": 0.87,
        "url": "https://help.game.com/download-troubleshooting"
      }
    ]
  }
}
```

## 5.5 ตาราง: Endpoint หลักของ Facebook API และการใช้งาน

| API Endpoint | HTTP Method | วัตถุประสงค์ในระบบ | สิทธิ์ที่จำเป็น | พารามิเตอร์หลัก |
|--------------|-------------|-------------------|-----------------|-----------------|
| `/{page-id}/messages` | POST | Endpoint หลักสำหรับส่งการตอบกลับทั้งหมดไปยังผู้ใช้ | `pages_messaging` | `recipient`, `message`, `messaging_type`, `message_tag` |
| `/{page-id}/conversations` | GET | ดึงประวัติการสนทนาเพื่อเป็นหน่วยความจำระยะยาว | `pages_read_engagement` | `user_id`, `platform` |
| `/{conversation-id}` | GET | ดึงรายการข้อความภายในการสนทนาที่ระบุ | `pages_read_engagement` | `fields=messages` |
| `/{page-id}/pass_thread_control` | POST | ส่งมอบการควบคุมการสนทนาไปยังแอปของเจ้าหน้าที่มนุษย์ | `pages_messaging` | `recipient`, `target_app_id` |
| `/{page-id}/take_thread_control` | POST | รับการควบคุมการสนทนากลับจากแอปอื่น | `pages_messaging` | `recipient`, `metadata` |

## 5.6 การจัดการข้อผิดพลาดและการตอบสนอง

### HTTP Status Codes ที่สำคัญ

#### 2xx - สำเร็จ:
- `200 OK` - คำขอสำเร็จ
- `201 Created` - สร้างข้อมูลใหม่สำเร็จ

#### 4xx - ข้อผิดพลาดจากฝั่งไคลเอนต์:
- `400 Bad Request` - ข้อมูลที่ส่งมาไม่ถูกต้อง
- `401 Unauthorized` - ไม่มีสิทธิ์เข้าถึง
- `403 Forbidden` - ถูกห้ามเข้าถึง
- `429 Too Many Requests` - เกินขีดจำกัดการเรียกใช้

#### 5xx - ข้อผิดพลาดจากฝั่งเซิร์ฟเวอร์:
- `500 Internal Server Error` - ข้อผิดพลาดภายในเซิร์ฟเวอร์
- `503 Service Unavailable` - บริการไม่พร้อมให้บริการชั่วคราว

### การจัดการ Rate Limiting

Facebook มีการจำกัดอัตราการเรียกใช้ API:

#### Messaging API Limits:
- **Standard messaging**: 1000 API calls per app per page per day
- **Subscription messaging**: ขึ้นอยู่กับประเภทการสมัครสมาชิก

#### การจัดการ Rate Limits:
1. **Exponential Backoff** - เพิ่มเวลารอหลังได้รับ 429
2. **Request Queuing** - จัดคิวคำขอเมื่อใกล้ถึงขีดจำกัด  
3. **Priority Handling** - จัดลำดับความสำคัญของข้อความ

## 5.7 การตรวจสอบและบันทึกข้อมูล (Monitoring & Logging)

### ข้อมูลที่ควรบันทึก:

#### 1. API Request/Response Logging:
```json
{
  "timestamp": "2024-10-15T10:30:00Z",
  "request_id": "req_12345",
  "method": "POST",
  "endpoint": "/v18.0/me/messages", 
  "status_code": 200,
  "response_time_ms": 150,
  "user_psid": "USER_PSID",
  "message_type": "text",
  "intent_detected": "get_launch_date"
}
```

#### 2. Error Logging:
```json
{
  "timestamp": "2024-10-15T10:31:00Z",
  "level": "ERROR",
  "error_code": "FB_API_ERROR",
  "message": "Failed to send message to user",
  "details": {
    "user_psid": "USER_PSID", 
    "facebook_error": {
      "code": 100,
      "message": "Invalid parameter"
    },
    "retry_count": 2
  }
}
```

### เมตริกที่ควรติดตาม:

1. **API Performance**:
   - เวลาตอบสนองเฉลี่ย (Average Response Time)
   - อัตราความสำเร็จ (Success Rate)
   - อัตราการเกิดข้อผิดพลาด (Error Rate)

2. **Business Metrics**:
   - จำนวนข้อความที่ส่งต่อวัน
   - อัตราการแปลงจากบทสนทนาไปสู่การซื้อ
   - ความพึงพอใจของลูกค้า (CSAT)

## สรุป

การเชื่อมต่อ API ที่มีประสิทธิภาพเป็นรากฐานสำคัญของระบบ AI Agentic การปฏิบัติตามข้อกำหนดของ Facebook และการออกแบบ Internal APIs ที่ดีจะช่วยให้ระบบทำงานได้อย่างเสถียรและสามารถขยายขนาดได้ในอนาคต

### ประเด็นสำคัญที่ต้องจำ:

1. **การปฏิบัติตามนโยบาย** - ต้องเคารพกฎของ Facebook เพื่อหลีกเลี่ยงการถูกจำกัดสิทธิ์
2. **ความปลอดภัย** - การรักษาความปลอดภัยของข้อมูลผู้ใช้และ Access Tokens
3. **ประสิทธิภาพ** - การออกแบบ APIs ที่รวดเร็วและเชื่อถือได้
4. **การติดตาม** - การมีระบบ Monitoring ที่ดีเพื่อแก้ไขปัญหาได้ทันท่วงที

---

**หมายเหตุ**: เอกสารนี้เป็นส่วนหนึ่งของชุดเอกสารออกแบบระบบ AI Agentic ที่ครบถ้วน สำหรับรายละเอียดเพิ่มเติม โปดดูเอกสารอื่นๆ ในโฟลเดอร์ `docs/`