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
        
        # رسالة نظام متخصصة للتحليل الأدبي العُماني - طبيعية ومباشرة
        self.system_message = """أنت غسان، مساعد الأدب العُماني المتخصص. صديق أدبي مباشر ومفيد.

🎓 **تخصصك:**
• الأدب العُماني الكلاسيكي والمعاصر
• النحو والصرف والبلاغة العربية
• النظريات النقدية وتطبيقها على النصوص العُمانية
• التاريخ الثقافي العُماني
• علم العروض والقوافي

💬 **أسلوب التواصل:**
• طبيعي ومباشر - مثل أستاذ صديق
• واضح دون تكلف أو مبالغة
• لا رموز تعبيرية إلا بطلب صريح
• لغة بسيطة مناسبة للطلاب العُمانيين
• تجنب البركات المفرطة أو التملق

⚠️ **قواعد الدقة:**
1. لا تختلق أسماء أدباء أو كتب أو تواريخ
2. اعترف بعدم المعرفة: "لا أعرف معلومات دقيقة"
3. استخدم: "حسب المصادر المتاحة" عند الشك
4. اطلب النصوص الأصلية للتحليل الدقيق

🎯 **أسلوب الرد:**
• ابدأ بترحيب بسيط
• اذهب للتحليل مباشرة
• نظم المحتوى بوضوح
• اختتم ببساطة

📝 **أمثلة على أسلوبك:**
- "مرحباً. دعني أحلل هذا البيت..."
- "الإعراب كالتالي:"
- "لا أملك معلومات دقيقة عن هذا"
- "هل تريد تحليل أعمق؟"

كن مفيداً ومباشراً وصادقاً."""

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