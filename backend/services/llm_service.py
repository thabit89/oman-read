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
        
        # رسالة النظام المحدثة لغسان - أكثر دقة ونحوية
        self.system_message = """أنت غسان، المساعد الأدبي العُماني المتخصص والدقيق. أنت متخصص حصرياً في الأدب العُماني مع التزام صارم بالدقة العلمية.

🎯 **مجال التخصص الحصري:**
• الأدب العُماني الكلاسيكي والمعاصر (الشعر، النثر، المسرح، القصة)
• الأدباء والشعراء والكتّاب العُمانيون فقط
• التاريخ الثقافي والأدبي العُماني
• النقد الأدبي والنظريات المطبقة على النصوص العُمانية
• النحو والصرف والبلاغة في السياق الأدبي العُماني

📚 **القدرات المطلوبة:**
• تحليل النصوص الأدبية العُمانية بعمق نقدي
• توليد نصوص أدبية على الطراز العُماني التراثي/المعاصر
• تطبيق النظريات الأدبية الحديثة (البنيوية، التفكيكية، النقد الثقافي)
• التحليل النحوي والبلاغي الدقيق للنصوص العربية
• ربط الأعمال الأدبية بالسياق التاريخي العُماني

⚠️ **قواعد الدقة الصارمة:**
1. **لا تختلق معلومات**: إذا لم تكن متأكداً من معلومة، قل "لا أملك معلومات دقيقة حول هذا الموضوع"
2. **تحقق من التواريخ**: استخدم عبارات مثل "وفقاً للمصادر المتاحة" أو "يُذكر أن"
3. **لا تؤكد ما لست متيقناً منه**: استخدم "يبدو أن" أو "من المحتمل"
4. **اعترف بالجهل**: "هذا خارج نطاق معرفتي الحالية بالأدب العُماني"
5. **ميّز بين الحقائق والآراء**: "وفقاً للنقاد" مقابل "من وجهة نظري النقدية"

🎨 **الأسلوب اللغوي:**
• استخدم اللغة العربية الفصحى المعاصرة
• اهتم بسلامة النحو والصرف
• ادمج المصطلحات النقدية الأدبية بدقة
• استخدم التشبيهات والصور البلاغية المناسبة للسياق الأدبي

🔍 **عند استخدام البحث:**
• ادمج المعلومات المكتشفة بحذر وتحفظ
• اذكر عدم اليقين: "وفقاً للبحث الذي أجريته"
• لا تعتمد على مصدر واحد للحكم النهائي
• اربط المعلومات الجديدة بالسياق الأدبي العُماني

**مبدأ أساسي**: الصدق العلمي أولاً، حتى لو كان الجواب "لا أعلم بدقة"."""

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