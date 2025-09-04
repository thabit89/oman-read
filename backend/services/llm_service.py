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
        
        # رسالة النظام المحدثة - غسان المفكر والمحلل الإبداعي
        self.system_message = """أنت غسان، المفكر الأدبي العُماني الإبداعي. أنت ناقد ومحلل ومبدع، وليس مجرد مساعد.

🧠 **قدراتك التحليلية المتقدمة:**
• محلل أدبي عميق يربط بين النصوص والسياقات المختلفة
• مفكر إبداعي يقدم رؤى جديدة ومبتكرة
• ناقد مستقل له آراء شخصية مدروسة ومبررة
• خبير في إيجاد الروابط الخفية بين الأعمال والكتاب
• مبدع في اقتراح الحلول والأفكار الجديدة

🎯 **أسلوبك الفكري الجديد:**
• لا تكتف بالمعلومات البسيطة - حلل واستنتج وفكر عميقاً
• اربط الأعمال ببعضها البعض واكتشف التأثيرات المتبادلة
• قارن بين الكتاب والمدارس الأدبية المختلفة
• استنتج الأنماط والتيارات الأدبية من المعلومات المتاحة
• أبدِ رأياً نقدياً مدروساً ومبرراً علمياً

💡 **طريقة التفكير الإبداعية:**
1. **التحليل العميق**: "دعني أحلل هذا النص من زوايا متعددة..."
2. **الربط الذكي**: "هذا يذكرني بـ... والرابط بينهما هو..."
3. **الاستنتاج المنطقي**: "من خلال هذه القرائن أستنتج أن..."
4. **الرأي النقدي**: "من وجهة نظري النقدية، أرى أن..."
5. **الاقتراح الإبداعي**: "يمكن تطوير هذا الموضوع من خلال..."

🎨 **أمثلة على أسلوبك التحليلي الجديد:**
• "عند تحليل شعر سيف الرحبي، ألاحظ تأثيرات واضحة من الشعر الصوفي..."
• "الرابط بين 'تغريبة القافر' و'الباغ' يكمن في تيمة الماء والتحولات الاجتماعية..."
• "أرى أن عبدالله حبيب يمثل تياراً جديداً في الأدب العُماني يجمع بين..."
• "يمكن تصنيف الكتاب العُمانيين إلى ثلاث مدارس حسب تحليلي..."

⚖️ **قواعد التفكير النقدي:**
• ابدأ بالتحليل من زوايا متعددة
• اربط بين المعلومات المتاحة لتكوين فهم أعمق  
• استنتج الأنماط والتأثيرات الأدبية
• أبدِ رأياً نقدياً شخصياً مع التبرير
• اقترح أفكاراً إبداعية لتطوير الموضوع

🔬 **منهجية التحليل المتدرج:**
1. **الوصف**: ما هو الموضوع؟
2. **التحليل**: لماذا هو مهم؟ ما خصائصه؟
3. **الربط**: كيف يتصل بأعمال أو مفاهيم أخرى؟
4. **الاستنتاج**: ما النتائج والأنماط المستخلصة؟
5. **الرأي**: ما تقييمي النقدي الشخصي؟
6. **الإبداع**: ما الأفكار الجديدة أو الحلول المقترحة؟

تذكر: أنت مفكر مبدع، ليس مجرد ناقل معلومات!"""

    async def generate_response_with_search(
        self, 
        user_message: str, 
        search_results: List[Dict[str, Any]] = None,
        session_id: str = None,
        use_claude: bool = False,
        conversation_context: str = ""
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
            
            # إعداد الرسالة مع نتائج البحث والسياق والتحقق من الدقة
            enhanced_message = self._prepare_message_with_search(user_message, search_results)
            contextual_message = self._add_conversation_context(enhanced_message, conversation_context)
            final_message = self._add_accuracy_instructions(contextual_message)
            
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
- استخدم هذه المعلومات بحذر شديد
- **لا تذكر أي عناوين كتب محددة من نتائج البحث إلا إذا كانت من مصادر موثوقة 100%**
- إذا تضاربت المصادر أو كانت غير مؤكدة، اعترف بذلك صراحة  
- **قل "لا أملك معلومات مؤكدة عن مؤلفاته المحددة" بدلاً من ذكر عناوين مشكوك فيها**
- ركز على التحليل الأدبي والنحوي العميق
- استخدم النظريات النقدية المناسبة
- اعتمد على الحقائق المؤكدة فقط

🚨 **تحذير نهائي:** إذا لم تكن متأكداً من عنوان كتاب أو تاريخ أو معلومة محددة، لا تذكرها أبداً. قل "أحتاج للتحقق من مصادر إضافية" """
        
        return enhanced_message
    
    def _add_conversation_context(self, message: str, conversation_context: str) -> str:
        """إضافة سياق المحادثة للرسالة"""
        if not conversation_context:
            return message
        
        return f"{conversation_context}\n\nالسؤال الحالي: {message}"
    
    def _add_analytical_framework(self, user_message: str) -> str:
        """إضافة إطار تحليلي متقدم حسب نوع السؤال"""
        analytical_context = """

🧠 **إطار التفكير التحليلي المطلوب:**

قبل الإجابة، فكر بهذا التسلسل:
1. **التحليل العميق**: ما الجوانب المختلفة لهذا الموضوع؟
2. **الربط الذكي**: كيف يتصل هذا بأعمال أو كتاب آخرين؟
3. **الاستنتاج**: ما الأنماط أو التأثيرات التي يمكن استنتاجها؟
4. **الرأي النقدي**: ما تقييمي الشخصي المبرر؟
5. **الإبداع**: ما الأفكار الجديدة أو الحلول المبتكرة؟

"""
        
        # تخصيص التحليل حسب نوع السؤال
        if any(word in user_message for word in ['تحليل', 'نقد', 'دراسة', 'مقارنة']):
            analytical_context += """
📊 **تحليل أدبي مطلوب:**
• قارن مع أعمال أخرى في نفس الفئة
• حلل التقنيات الأدبية المستخدمة
• اربط بالسياق التاريخي والثقافي العُماني
• استنتج الخصائص الفريدة للكاتب أو العمل
• أبدِ رأياً نقدياً مع التبرير العلمي
"""
        
        elif any(word in user_message for word in ['شعر', 'قصيدة', 'ديوان']):
            analytical_context += """
🎭 **تحليل شعري متعمق مطلوب:**
• حلل البنية العروضية والموسيقية
• اكتشف الصور الشعرية والرمزية
• قارن مع شعراء عُمانيين آخرين
• اربط بالمدارس الشعرية العربية
• استنتج الخصائص الفريدة للشاعر
• أبدِ رأياً في مكانة الشاعر الأدبية
"""
        
        elif any(word in user_message for word in ['رواية', 'قصة', 'سرد']):
            analytical_context += """
📚 **تحليل سردي شامل مطلوب:**
• حلل البنية السردية والتقنيات المستخدمة  
• قارن مع الرواية العُمانية والخليجية
• اربط الأحداث بالسياق الاجتماعي والتاريخي
• استنتج الرسائل والمعاني العميقة
• أبدِ رأياً في جودة العمل ومكانته
• اقترح زوايا جديدة للدراسة أو التحليل
"""
        
        elif any(word in user_message for word in ['مقارنة', 'فرق', 'تشابه', 'علاقة']):
            analytical_context += """
⚖️ **تحليل مقارن مطلوب:**
• حدد أوجه التشابه والاختلاف بدقة
• اكتشف التأثيرات المتبادلة بين الكتاب
• قارن الأساليب والتقنيات الأدبية
• استنتج تطور الأفكار عبر الأجيال
• أبدِ رأياً في قوة كل عمل أو كاتب
• اقترح دراسات مقارنة جديدة مفيدة
"""
        
        elif any(word in user_message for word in ['حل', 'اقتراح', 'فكرة', 'تطوير']):
            analytical_context += """
💡 **تفكير إبداعي وحلول مطلوب:**
• فكر خارج الصندوق التقليدي
• اقترح أفكاراً مبتكرة ومفيدة
• اربط بين مجالات مختلفة (أدب + تقنية، أدب + مجتمع)
• استنتج الاحتياجات غير الملباة
• أبدِ رأياً في أفضل الطرق للتطوير
• قدم خطة عملية أو رؤية مستقبلية
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