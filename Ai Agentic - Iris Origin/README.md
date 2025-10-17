# 🤖 Iris Origin - AI Agentic Platform

## 🚀 ภาพรวมโครงการ

**Iris Origin - AI Agentic Platform** เป็นพิมพ์เขียวที่ครบถ้วนสำหรับการพัฒนาระบบ AI Agentic สำหรับการบริการลูกค้าบน Facebook Fan Pages ซึ่งออกแบบมาเพื่อเปลี่ยนแปลงจากการเป็นแชทบอทธรรมดาไปสู่ระบบ "Agentic" ที่มีความสามารถในการให้เหตุผลและดำเนินการได้ด้วยตนเอง

## โครงสร้างเอกสาร

### 📋 เอกสารหลัก

- **[สถาปัตยกรรมระบบ](docs/architecture/core-architecture.md)** - แกนหลักและองค์ประกอบของระบบ AI Agentic
- **[กลไกการเรียนรู้ RLHF](docs/rlhf/learning-mechanisms.md)** - การปรับปรุงอย่างต่อเนื่องด้วย Reinforcement Learning from Human Feedback
- **[ระบบสนับสนุนหลายภาษา](docs/multilingual/language-capabilities.md)** - การเข้าถึงฐานผู้เล่นทั่วโลก (ไทย, อังกฤษ, จีน, อินโดนีเซีย)
- **[พิมพ์เขียวการติดตั้ง](docs/implementation/system-blueprint.md)** - กระบวนการ, เวิร์กโฟลว์ และตรรกะทางธุรกิจ
- **[ข้อกำหนด API](docs/api/platform-integration.md)** - การเชื่อมต่อ Facebook และระบบภายใน

### 🛠️ ด้านเทคนิค

- **[ชุดเทคโนโลยีที่แนะนำ](docs/implementation/technology-stack.md)** - การเปรียบเทียบและคำแนะนำ Rasa vs Dialogflow vs Bot Framework
- **[การวิเคราะห์การแข่งขัน](docs/competitive-analysis/industry-analysis.md)** - แนวทางของอุตสาหกรรมและแผนการดำเนินงาน
- **[แผนการดำเนินงาน](docs/implementation/roadmap.md)** - การพัฒนาแบบแบ่งระยะ

## คุณสมบัติหลัก

### 🤖 ระบบ AI Agentic

- **การรับรู้** (Perception) - วิเคราะห์ข้อความผ่าน Facebook Webhooks
- **การตัดสินใจ** (Decision-Making) - ใช้ LLM สำหรับ NLU และ Intent Classification
- **การกระทำ** (Action) - เรียกใช้เครื่องมือและ API ต่างๆ
- **หน่วยความจำ** (Memory) - ระบบหน่วยความจำแบบผสมระยะสั้นและระยะยาว
- **การสื่อสาร** (Communication) - โต้ตอบผ่าน Facebook Send API

### 📚 การเรียนรู้ด้วย RLHF

- **Supervised Fine-Tuning (SFT)** - ปรับแต่งแบบจำลองให้เข้ากับโดเมนเกม
- **Reward Model Training** - เรียนรู้จากข้อมูลป้อนกลับของเจ้าหน้าที่
- **Policy Optimization** - ปรับปรุงประสิทธิภาพด้วย Reinforcement Learning
- **Continuous Learning Loop** - การปรับปรุงอย่างต่อเนื่อง

### 🌏 การสนับสนุนหลายภาษา

- ภาษาไทย - การแบ่งคำและบริบททางวัฒนธรรม
- ภาษาอังกฤษ - ภาษาหลักสำหรับการพัฒนา
- ภาษาจีน - อักษรภาพและความหมายตามบริบท
- ภาษาอินโดนีเซีย - โครงสร้างคำที่ซับซ้อน

## การเริ่มต้นใช้งาน

### ข้อกำหนดเบื้องต้น

- Facebook Developer Account
- Page Access Tokens
- ระบบ CRM และ Game Database APIs
- Python/Rasa Development Environment

### ขั้นตอนการติดตั้ง

1. **ระยะที่ 1**: โครงการนำร่อง (สัปดาห์ 0-6)
2. **ระยะที่ 2**: เปิดตัว MVP และวางรากฐาน RLHF (สัปดาห์ 7-12)
3. **ระยะที่ 3**: การขยายขนาดและการปรับปรุงประสิทธิภาพ (สัปดาห์ 13-24)
4. **ระยะที่ 4**: ความสามารถ Agentic เต็มรูปแบบ (ต่อเนื่อง)

## ตัวชี้วัดความสำเร็จ

- **Containment Rate** > 50% (เป้าหมายสุดท้าย)
- **Customer Satisfaction (CSAT)** > 4.0/5
- **Intent Recognition Accuracy** > 85%
- **Human Agent Handover** < 20% ของกรณีทั้งหมด

## การมีส่วนร่วม

เอกสารนี้มีไว้สำหรับ:

- ทีมพัฒนา (Developers)
- ทีมบริการลูกค้า (CS/CRM)
- ผู้บริหารโครงการ (Project Managers)
- สถาปนิกระบบ (System Architects)

## ใบอนุญาต

© 2025 - เอกสารภายในองค์กร สำหรับการใช้งานภายในเท่านั้น

---

*สร้างเมื่อ: ตุลาคม 2025*  
*เวอร์ชันเอกสาร: 1.0*