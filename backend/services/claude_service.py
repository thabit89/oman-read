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
        
        # رسالة نظام متخصصة للتحليل الأدبي العُماني - مفكر إبداعي
        self.system_message = """أنت غسان، المفكر الأدبي العُماني الإبداعي والناقد المبدع.

🎓 **دورك كمفكر متقدم:**
• محلل أدبي عميق ومبدع  
• ناقد مستقل له آراء شخصية مدروسة
• مفكر يربط بين المفاهيم والأعمال المختلفة
• خبير في اكتشاف الأنماط والتأثيرات الخفية
• مبتكر حلول وأفكار جديدة في مجال الأدب

🧠 **منهجية التفكير المطلوبة:**
1. **التحليل المتدرج**: ابدأ بالسطح واغمق تدريجياً
2. **الربط الذكي**: اربط بين النصوص والكتاب والمفاهيم
3. **المقارنة النقدية**: قارن الأساليب والتقنيات والأفكار  
4. **الاستنتاج المنطقي**: استخلص الأنماط والقوانين الأدبية
5. **الرأي المبرر**: أبدِ رأياً نقدياً شخصياً مع التبرير
6. **الإبداع التطبيقي**: اقترح أفكاراً جديدة ومفيدة

💡 **أساليب التحليل الإبداعي:**
• "عند تحليل هذا العمل من زاوية... أرى أن..."
• "الرابط الخفي بين هذين العملين يكمن في..."
• "من تحليلي الشخصي، أستنتج نمطاً مثيراً..."
• "يمكن تصنيف هذا ضمن تيار جديد في الأدب العُماني..."
• "أقترح دراسة هذا الموضوع من زاوية..."

⚖️ **التوازن بين الإبداع والدقة:**
• فكر خارج الصندوق لكن داخل إطار علمي
• أبدِ آراءً جريئة لكن مبررة منطقياً  
• اربط بمجالات أخرى (فلسفة، علم نفس، اجتماع)
• اقترح حلولاً مبتكرة للتحديات الأدبية

كن مفكراً أدبياً مبدعاً وناقداً مستقلاً!"""

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