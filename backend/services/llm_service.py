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
        """إعداد الرسالة مع دمج نتائج البحث والتحقق من الموثوقية"""
        if not search_results:
            return user_message + "\n\n" + self._add_analytical_framework(user_message)
        
        # تجهيز المعلومات من البحث مع تقييم الموثوقية
        search_context = "\n--- معلومات من مصادر موثوقة ---\n"
        
        for i, result in enumerate(search_results, 1):
            reliability_note = ""
            if result.get('reliability_warning'):
                reliability_note = f" (تنبيه: {result['reliability_warning']})"
            
            search_context += f"""
{i}. {result.get('title', 'بلا عنوان')}{reliability_note}
المصدر: {result.get('source', 'غير محدد')} - نوع: {result.get('type', 'عام')}
المحتوى: {result.get('content', '')[:200]}...
درجة الموثوقية: {result.get('final_score', 0.5):.1f}/1.0
"""
        
        search_context += "\n--- نهاية المعلومات ---\n"
        
        # إضافة التوجيهات النقدية والنحوية
        analytical_framework = self._add_analytical_framework(user_message)
        
        # دمج الرسالة مع السياق
        enhanced_message = f"""السؤال: {user_message}

{search_context}

{analytical_framework}

تعليمات مهمة:
- استخدم هذه المعلومات بحذر، خاصة تلك ذات الموثوقية المنخفضة
- إذا تضاربت المصادر، اذكر ذلك صراحة  
- إذا كانت المعلومات غير كافية، اعترف بذلك
- ركز على التحليل الأدبي والنحوي العميق
- استخدم النظريات النقدية المناسبة"""
        
        return enhanced_message
    
    def _add_analytical_framework(self, user_message: str) -> str:
        """إضافة إطار تحليلي حسب نوع السؤال"""
        analytical_context = ""
        
        # تحديد نوع الاستفسار
        if any(word in user_message for word in ['تحليل', 'نقد', 'دراسة']):
            analytical_context += """
إطار التحليل المطلوب:
• استخدم النظريات النقدية المناسبة (البنيوية، التفكيكية، النقد الثقافي)
• حلل البنية اللغوية والنحوية للنص
• اربط العمل بالسياق التاريخي والثقافي العُماني
• اعتمد على منهجية نقدية واضحة
"""
        
        elif any(word in user_message for word in ['شعر', 'قصيدة', 'بيت', 'أبيات']):
            analytical_context += """
تحليل شعري مطلوب:
• حلل البحر الشعري والقافية
• اشرح الصور البلاغية والاستعارات
• حدد التيار الشعري (كلاسيكي، حداثي، معاصر)
• اربط بالمدرسة الشعرية العُمانية
"""
        
        elif any(word in user_message for word in ['نحو', 'إعراب', 'قواعد']):
            analytical_context += """
تحليل نحوي مطلوب:
• اعرب الكلمات والجمل بدقة
• اشرح القواعد النحوية المطبقة
• حدد الوظائف النحوية للعناصر
• اذكر المراجع النحوية المعتمدة
"""
        
        elif any(word in user_message for word in ['تاريخ', 'نشأة', 'تطور']):
            analytical_context += """
سياق تاريخي مطلوب:
• اربط بالأحداث التاريخية العُمانية
• اذكر المراحل الزمنية بدقة
• حدد التأثيرات الثقافية والاجتماعية
• اعتمد على المصادر التاريخية الموثوقة
"""
        
        return analytical_context
    
    def _should_use_claude(self, user_message: str) -> bool:
        """تحديد متى نستخدم Claude بدلاً من GPT للحصول على تحليل أكثر دقة"""
        # استخدم Claude للتحليل الإبداعي والنقدي والنحوي
        claude_keywords = [
            'تحليل', 'نقد', 'إبداع', 'شاعرية', 'جمالية', 
            'أسلوب', 'بلاغة', 'صورة شعرية', 'رمزية',
            'نحو', 'إعراب', 'قواعد', 'بنية', 'تركيب',
            'نظرية', 'منهج', 'مدرسة أدبية', 'تيار'
        ]
        
        return any(keyword in user_message for keyword in claude_keywords)
    
    def _add_accuracy_instructions(self, message: str) -> str:
        """إضافة تعليمات صارمة لتجنب الهلوسات"""
        accuracy_instructions = """
        
🚨 تعليمات الدقة الصارمة:

1. إذا لم تكن متأكداً من معلومة، استخدم عبارات مثل:
   - "وفقاً للمصادر المتاحة"
   - "يُذكر في بعض المراجع"  
   - "لا أملك معلومات دقيقة حول هذا الموضوع"

2. لا تختلق تواريخ أو أسماء أو أحداث

3. ميز بين الحقائق والآراء النقدية بوضوح

4. اعترف بحدود معرفتك بدلاً من التخمين

5. استخدم مصطلحات نقدية دقيقة ومعرّفة

6. عند الشك، اطلب توضيحاً من المستخدم

تذكر: الصدق العلمي أهم من إعطاء إجابة مكتملة."""
        
        return message + accuracy_instructions

# مثيل واحد للخدمة
ghassan_llm_service = GhassanLLMService()