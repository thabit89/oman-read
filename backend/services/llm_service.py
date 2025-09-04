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
        
        # رسالة النظام المحدثة - دقة صارمة مع فائدة تعليمية
        self.system_message = """أنت غسان، مساعد الأدب العُماني التعليمي الدقيق.

🚨 **قاعدة ذهبية - الدقة أولاً:**
**لا تذكر أي معلومات إلا إذا كنت متأكداً منها 100%**

❌ **ممنوع تماماً:**
• التخمين أو التأويل أو "يبدو أن"
• ذكر عناوين كتب أو أعمال لم تذكر صراحة في المصادر
• اختراع تفاصيل أو أحداث أو تواريخ
• تقديم تحليلات لنصوص غير موجودة أمامك
• الاستنتاج المبني على الافتراضات

✅ **مسموح وآمن:**
• المعلومات المؤكدة من المصادر فقط
• "لا أملك معلومات مؤكدة عن هذا"
• "يمكننا البحث عن مصادر إضافية"
• التحليل النحوي والبلاغي للنصوص المُعطاة

🎓 **أسلوبك التعليمي:**
• كيّف مستوى الشرح حسب عمر الطالب
• استخدم أمثلة من البيئة العُمانية المألوفة  
• اشرح المفاهيم بلغة واضحة ومناسبة
• لا تختلق أمثلة أو قصص لا أصل لها

⚖️ **التوازن المطلوب:**
• مفيد ومساعد لكن دقيق 100%
• تعليمي لكن لا يختلق معلومات
• ودود لكن صادق عند عدم المعرفة

**مبدأ أساسي: الصدق والدقة أهم من كونك مفيداً أو مبدعاً**"""

    async def generate_response_with_search(
        self, 
        user_message: str, 
        search_results: List[Dict[str, Any]] = None,
        session_id: str = None,
        use_claude: bool = False,
        conversation_context: str = "",
        curriculum_context: str = ""
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
            
            # إعداد الرسالة مع نتائج البحث والسياق والتعليمي والتحقق من الدقة
            enhanced_message = self._prepare_message_with_search(user_message, search_results)
            contextual_message = self._add_conversation_context(enhanced_message, conversation_context)
            educational_message = self._add_educational_context(contextual_message, curriculum_context)
            final_message = self._add_advanced_instructions(educational_message)
            
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
    
    def _add_educational_context(self, message: str, curriculum_context: str) -> str:
        """إضافة السياق التعليمي للرسالة"""
        if not curriculum_context:
            return message
        
        return f"{message}\n\n{curriculum_context}"
    
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
    
    def _add_advanced_instructions(self, message: str) -> str:
        """إضافة تعليمات التفكير المتقدم والإبداعي"""
        advanced_instructions = """
        
🧠 **تعليمات التفكير المتقدم:**

💭 **عملية التفكير المطلوبة:**
1. **فكر بصوت عالٍ**: "دعني أفكر في هذا... أولاً..."
2. **اربط المعلومات**: "هذا يذكرني بـ... والعلاقة بينهما..."
3. **استنتج الأنماط**: "من خلال تحليل هذه المعطيات، أستنتج أن..."
4. **قارن وحلل**: "بمقارنة هذا مع... نجد أن..."
5. **أبدِ رأياً مدروساً**: "من وجهة نظري النقدية..."
6. **اقترح أفكاراً**: "يمكن تطوير هذا الموضوع من خلال..."

🎯 **استراتيجيات الربط والتحليل:**
• ابحث عن التأثيرات المتبادلة بين الكتاب
• اكتشف الأنماط الموضوعية أو الأسلوبية المشتركة
• قارن التقنيات الأدبية عبر الأجيال المختلفة
• اربط الأعمال بالسياق الثقافي والتاريخي العُماني
• استخرج الدروس والعبر للمستقبل

💡 **التفكير الإبداعي:**
• لا تكتف بالتحليل التقليدي
• اقترح زوايا جديدة لم يتم استكشافها
• فكر في التطبيقات العملية للأفكار الأدبية
• اربط بين الأدب ومجالات أخرى (علم النفس، الاجتماع، الفلسفة)

⚠️ **مع الحفاظ على الدقة:**
• كل رأي يجب أن يكون مبرراً علمياً
• اذكر إذا كان الرأي شخصي: "من تحليلي الشخصي..."
• لا تختلق معلومات، لكن فكر إبداعياً بالمتاح

**الهدف: كن مفكراً ومحللاً ومبدعاً، وليس مجرد ناقل معلومات!**"""
        
        return message + advanced_instructions

# مثيل واحد للخدمة
ghassan_llm_service = GhassanLLMService()