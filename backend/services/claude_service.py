import os
from typing import Dict, Any, List
import anthropic
from dotenv import load_dotenv
import logging
import uuid

load_dotenv()

logger = logging.getLogger(__name__)

class ClaudeDirectService:
    """خدمة Claude المباشرة للتحليل الأدبي المتقدم"""
    
    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # رسالة نظام متخصصة للتحليل الأدبي العُماني
        self.system_message = """أنت غسان، أستاذ الأدب العُماني والناقد الأدبي المتخصص. أنت خبير في:

🎓 **التخصص الأكاديمي:**
• الأدب العُماني الكلاسيكي والمعاصر
• النحو والصرف والبلاغة العربية بدقة عالية
• النظريات النقدية (البنيوية، التفكيكية، النقد الثقافي، التحليل الأسلوبي)
• التاريخ الثقافي والأدبي العُماني
• علم العروض والقوافي

🔬 **المنهجية العلمية:**
• التزام صارم بالدقة والصدق العلمي
• الاعتراف بحدود المعرفة بدلاً من التخمين
• التمييز الواضح بين الحقائق والآراء النقدية
• استخدام المصطلحات الأدبية والنحوية بدقة
• التحقق من المصادر والموثوقية

⚠️ **قواعد منع الهلوسة:**
1. لا تختلق أسماء أدباء أو كتب أو تواريخ
2. استخدم عبارات التحقق: "وفقاً للمصادر"، "يُذكر أن"، "من المحتمل"
3. اعترف بعدم المعرفة: "لا أملك معلومات دقيقة"
4. اطلب النصوص الأصلية للتحليل الدقيق
5. تجنب التعميمات غير المدعومة بأدلة

🎯 **التخصصات التفصيلية:**
• **التحليل النحوي**: إعراب دقيق مع شرح القواعد
• **التحليل البلاغي**: الصور البيانية والمحسنات البديعية
• **النقد الأدبي**: تطبيق النظريات الحديثة بدقة
• **العروض**: تحديد البحور والقوافي والزحافات
• **التاريخ الأدبي**: ربط النصوص بالسياق التاريخي العُماني

📝 **أسلوب الإجابة:**
• لغة عربية فصيحة ودقيقة نحوياً
• تنظيم واضح بعناوين وترقيم
• أمثلة محددة وتحليلات معمقة
• اعتماد المنهج العلمي في التحليل"""

    async def analyze_literary_text(
        self, 
        user_message: str, 
        search_context: str = "",
        session_id: str = None
    ) -> Dict[str, Any]:
        """تحليل أدبي متقدم باستخدام Claude"""
        
        try:
            # إعداد الرسالة مع السياق والتعليمات
            full_message = f"""
المطلوب: {user_message}

{search_context if search_context else ""}

تعليمات مهمة:
- قدم تحليلاً أكاديمياً دقيقاً
- استخدم المصطلحات النقدية والنحوية بدقة
- اعترف بأي نقص في المعلومات
- ركز على الأدب العُماني حصرياً
- طبق النظريات النقدية المناسبة
"""

            # إرسال للـ Claude
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.3,  # دقة أعلى، إبداع أقل
                system=self.system_message,
                messages=[
                    {
                        "role": "user", 
                        "content": full_message
                    }
                ]
            )
            
            return {
                'text': response.content[0].text,
                'session_id': session_id or str(uuid.uuid4()),
                'model_used': 'claude-3.5-sonnet(خاص)',
                'analysis_type': 'literary_advanced',
                'accuracy_level': 'high'
            }
            
        except Exception as e:
            logger.error(f"خطأ في Claude المباشر: {e}")
            return {
                'text': 'عذراً، حدث خطأ في التحليل الأدبي المتقدم. أرجو المحاولة مرة أخرى.',
                'session_id': session_id or str(uuid.uuid4()),
                'model_used': 'claude-error',
                'error': str(e)
            }

# مثيل خدمة Claude المباشرة
claude_direct_service = ClaudeDirectService()