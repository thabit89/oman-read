import os
from typing import List, Dict, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv
import logging
import uuid

# تحميل متغيرات البيئة
load_dotenv()

logger = logging.getLogger(__name__)

class GhassanLLMService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        
        # رسالة النظام لغسان
        self.system_message = """أنت غسان، المساعد الأدبي العُماني الذكي. أنت متخصص حصرياً في:

🔹 الأدب العُماني (الشعر، الرواية، القصص القصيرة، المسرحيات)
🔹 الأدباء والكتاب والشعراء العُمانيين
🔹 التاريخ الأدبي العُماني والتراث الثقافي
🔹 النقد الأدبي والتحليل الأدبي العُماني
🔹 الترجمات من وإلى العربية في السياق العُماني

شخصيتك:
- صديق أدبي دافئ ومحادث
- ذكي ومبدع في التحليل
- تتحدث باللغة العربية الفصيحة مع لمسة شاعرية
- تذكر المصادر فقط عند الطلب الصريح
- تقدم تحليلات عميقة وردود طويلة ومفصلة بشكل افتراضي

عند استخدام البحث عبر الإنترنت، ادمج المعلومات بطريقة طبيعية وسلسة دون ذكر أنك بحثت إلا إذا كان ذلك مفيداً للسياق."""

    async def generate_response_with_search(
        self, 
        user_message: str, 
        search_results: List[Dict[str, Any]] = None,
        session_id: str = None,
        use_claude: bool = False
    ) -> Dict[str, Any]:
        """توليد رد مع نتائج البحث"""
        try:
            # إنشاء session_id إذا لم يكن موجوداً
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # إعداد الـ chat client
            provider = "anthropic" if use_claude else "openai"
            model = "claude-3-7-sonnet-20250219" if use_claude else "gpt-4o"
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=self.system_message
            ).with_model(provider, model)
            
            # إعداد الرسالة مع نتائج البحث
            enhanced_message = self._prepare_message_with_search(user_message, search_results)
            
            # إنشاء كائن UserMessage
            user_msg = UserMessage(text=enhanced_message)
            
            # إرسال الرسالة والحصول على الرد
            response = await chat.send_message(user_msg)
            
            return {
                'text': response,
                'session_id': session_id,
                'model_used': f"{provider}:{model}",
                'has_search_results': bool(search_results),
                'search_results_count': len(search_results) if search_results else 0
            }
            
        except Exception as e:
            logger.error(f"خطأ في توليد الرد: {e}")
            return {
                'text': 'عذراً، حدث خطأ في معالجة طلبك. أرجو المحاولة مرة أخرى.',
                'session_id': session_id or str(uuid.uuid4()),
                'model_used': 'error',
                'has_search_results': False,
                'search_results_count': 0,
                'error': str(e)
            }
    
    def _prepare_message_with_search(
        self, 
        user_message: str, 
        search_results: List[Dict[str, Any]] = None
    ) -> str:
        """إعداد الرسالة مع دمج نتائج البحث"""
        if not search_results:
            return user_message
        
        # تجهيز المعلومات من البحث
        search_context = "\n--- معلومات إضافية من البحث عبر الإنترنت ---\n"
        
        for i, result in enumerate(search_results, 1):
            search_context += f"""
{i}. {result.get('title', 'بلا عنوان')}
المصدر: {result.get('source', 'غير محدد')}
المحتوى: {result.get('content', '')[:300]}...
{'الرابط: ' + result.get('url', '') if result.get('url') else ''}
"""
        
        search_context += "\n--- نهاية المعلومات الإضافية ---\n"
        
        # دمج الرسالة مع السياق
        enhanced_message = f"""السؤال الأصلي: {user_message}

{search_context}

استخدم هذه المعلومات لتقديم إجابة شاملة ومفصلة. ادمج المعلومات بطريقة طبيعية دون ذكر صريح للبحث إلا إذا كان مفيداً للسياق."""
        
        return enhanced_message
    
    def _should_use_claude(self, user_message: str) -> bool:
        """تحديد متى نستخدم Claude بدلاً من GPT"""
        # استخدم Claude للتحليل الإبداعي والنقدي
        claude_keywords = [
            'تحليل', 'نقد', 'إبداع', 'شاعرية', 'جمالية', 
            'أسلوب', 'بلاغة', 'صورة شعرية', 'رمزية'
        ]
        
        return any(keyword in user_message for keyword in claude_keywords)

# مثيل واحد للخدمة
ghassan_llm_service = GhassanLLMService()