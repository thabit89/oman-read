# Ghassan - المساعد الأدبي العُماني الذكي
## API Contracts & Integration Plan

### Frontend Mock Data Currently Used
في الـ frontend حالياً نستخدم mock data في `/app/frontend/src/data/mock.js`:

- **messages**: محادثات تجريبية مع غسان
- **userSessions**: جلسات محادثات سابقة (للمستقبل)

### Backend APIs Required

#### 1. Chat Endpoints
```
POST /api/chat/message
- إرسال رسالة جديدة للمساعد غسان
- Input: { message: string, sessionId?: string }
- Response: { response: string, messageId: string, timestamp: string }

GET /api/chat/history/{sessionId}
- جلب تاريخ المحادثات لجلسة معينة
- Response: { messages: Array<Message> }

POST /api/chat/session
- إنشاء جلسة محادثة جديدة
- Response: { sessionId: string }
```

#### 2. LLM Integration
- **OpenAI GPT-4o**: للتحليل الأدبي العميق
- **Claude Sonnet 3.5**: للإبداع والتحليل النقدي
- **Emergent LLM Key**: مفتاح موحد للوصول للخدمتين
- **System Message**: تخصيص غسان كمساعد أدبي عُماني ذكي

#### 3. Database Schema
```javascript
// Message Model
{
  id: string,
  text: string, 
  sender: 'user' | 'ghassan',
  sessionId: string,
  timestamp: Date,
  llmModel?: 'openai-gpt4o' | 'claude-sonnet-3.5'
}

// Session Model  
{
  id: string,
  title: string,
  lastMessage: string,
  messageCount: number,
  createdAt: Date,
  updatedAt: Date
}
```

### Frontend-Backend Integration Plan

#### 1. Remove Mock Data
- حذف استخدام mock data من Chat.jsx
- استبدالها بـ API calls حقيقية

#### 2. API Service
- إنشاء ChatService للتعامل مع البيانات
- إدارة sessions و message history

#### 3. Real-time Features
- تطبيق نظام typing indicator حقيقي
- حفظ المحادثات في قاعدة البيانات

#### 4. Error Handling
- معالجة أخطاء الشبكة وفقدان الاتصال
- رسائل خطأ باللغة العربية

### Technical Implementation
- **Backend**: FastAPI + MongoDB + emergentintegrations library
- **LLM Strategy**: استخدام OpenAI و Claude بالتناوب أو حسب نوع السؤال
- **Arabic Support**: دعم كامل للنصوص العربية
- **Session Management**: إدارة جلسات المحادثة لكل مستخدم