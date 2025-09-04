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
        # استخدام مفتاح Claude الخاص للتحليل الأدبي المتقدم
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        self.emergent_key = os.environ.get('EMERGENT_LLM_KEY')
        
        if not self.anthropic_key:
            logger.warning("ANTHROPIC_API_KEY not found, using EMERGENT_LLM_KEY")
        if not self.emergent_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        
        # رسالة النظام المحدثة - منع الهلوسة بصرامة مطلقة
        self.system_message = """أنت غسان، مساعد الأدب العُماني. أنت صديق أدبي طبيعي ومفيد.

🚨 **قاعدة ذهبية - منع الهلوسة:**
**لا تذكر أبداً أسماء كتب أو مؤلفات أو تواريخ محددة إلا إذا كنت متأكداً 100%**

❌ **ممنوع تماماً:**
• ذكر عناوين كتب أو دواوين محددة دون مصدر مؤكد
• ذكر تواريخ ولادة أو وفاة محددة 
• ذكر أسماء جوائز أو مناصب محددة
• ذكر أي تفاصيل شخصية محددة للأدباء

✅ **مسموح وآمن:**
• "كاتب عُماني معروف"
• "له أعمال في الشعر والنثر"
• "من الأدباء العُمانيين المعاصرين"
• "حسب المصادر المتاحة له مؤلفات متنوعة"

🎯 **أسلوبك:**
• طبيعي ومباشر
• واضح وودود دون مبالغة
• لا رموز تعبيرية
• لغة بسيطة للطلاب العُمانيين

📚 **تخصصك:**
• الأدب العُماني فقط
• النحو والبلاغة في السياق الأدبي
• التحليل النصي

⚖️ **عند السؤال عن أي مؤلف:**
1. ابحث في المعلومات المتوفرة أولاً
2. إذا لم تجد معلومات مؤكدة، قل: "لا أملك معلومات مؤكدة عن مؤلفاته المحددة"
3. اقترح البحث: "يمكننا البحث عن معلومات أكثر"
4. لا تختلق أبداً عناوين كتب

**مبدأ أساسي: الصدق أولاً، حتى لو كان الجواب ناقصاً"""

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
            
            # اختيار المفتاح والنموذج المناسب
            if use_claude and self.anthropic_key:
                # استخدام Claude الخاص للتحليل الأدبي المتقدم
                api_key = self.anthropic_key
                provider = "anthropic"
                model = "claude-3-5-sonnet-20241022"  # أحدث نموذج Claude
                logger.info(f"استخدام Claude الخاص للتحليل الأدبي: {user_message[:50]}...")
            else:
                # استخدام Emergent للاستفسارات العامة
                api_key = self.emergent_key
                provider = "openai"
                model = "gpt-4o"
                logger.info(f"استخدام GPT-4o للاستفسارات العامة: {user_message[:50]}...")
            
            # إعداد الـ chat client
            chat = LlmChat(
                api_key=api_key,
                session_id=session_id,
                system_message=self.system_message
            ).with_model(provider, model)
            
            # إعداد الرسالة مع نتائج البحث والتحقق من الدقة
            enhanced_message = self._prepare_message_with_search(user_message, search_results)
            final_message = self._add_accuracy_instructions(enhanced_message)
            
            # إنشاء كائن UserMessage
            user_msg = UserMessage(text=final_message)
            
            # إرسال الرسالة والحصول على الرد
            response = await chat.send_message(user_msg)
            
            return {
                'text': response,
                'session_id': session_id,
                'model_used': f"{provider}:{model}" + ("(خاص)" if use_claude and self.anthropic_key else ""),
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
        """إضافة تعليمات صارمة جداً لمنع الهلوسات"""
        accuracy_instructions = """
        
🚨 تحذير صارم - منع الهلوسة:

❌ **ممنوع منعاً باتاً:**
- ذكر أي عناوين كتب أو دواوين محددة دون مصدر مؤكد
- ذكر تواريخ ولادة أو وفاة أو نشر محددة
- ذكر أسماء جوائز أو مناصب أو وظائف محددة
- ذكر أرقام محددة (عدد الكتب، الصفحات، السنوات)
- اختلاق أي معلومات شخصية عن الأدباء

✅ **آمن للاستخدام:**
- "كاتب عُماني معروف"
- "له أعمال في الشعر والنثر" 
- "من الأدباء المعاصرين"
- "حسب المصادر المتاحة"
- "يُذكر أنه كاتب مؤثر"

🔍 **قبل ذكر أي معلومة محددة:**
- هل لديك مصدر مؤكد لهذه المعلومة؟
- هل ذكرت هذا في سياق البحث المتوفر؟
- إذا كان هناك شك، قل "لا أملك معلومات مؤكدة"

💡 **عبارات آمنة للاستخدام:**
- "لا أعرف تفاصيل محددة عن مؤلفاته"
- "يمكننا البحث عن معلومات أكثر" 
- "حسب ما هو متاح في المصادر"
- "من المفيد التحقق من مصادر إضافية"

تذكر: الصدق والاعتراف بعدم المعرفة أفضل ألف مرة من اختلاق معلومة واحدة."""
        
        return message + accuracy_instructions

# مثيل واحد للخدمة
ghassan_llm_service = GhassanLLMService()