from typing import Dict, Any, List, Optional
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class InformationVerificationService:
    """خدمة التحقق من صحة المعلومات ومنع الأخطاء"""
    
    def __init__(self):
        # قوائم الأسماء والمصطلحات المعروفة في الأدب العُماني
        self.known_authors = [
            'سيف الرحبي', 'هدى حمد', 'عبدالله الريامي', 'سعيد الصقلاوي',
            'محمد الحارثي', 'جوخة الحارثي', 'بدرية الشحي', 'سالم الراشدي',
            'أحمد بلال', 'يحيى منصور', 'حسين العبري', 'فاطمة الشيدي'
        ]
        
        self.suspicious_patterns = [
            # أنماط مشبوهة تدل على معلومات مختلقة
            r'وُلد في عام \d{4} تحديداً',  # تواريخ محددة جداً
            r'يبلغ عدد أعماله \d+ عملاً بالضبط',  # أرقام دقيقة مشبوهة
            r'حاز على جائزة .+ في عام \d{4}',  # جوائز محددة
            r'درس في جامعة .+ وتخرج عام \d{4}',  # تفاصيل دراسية دقيقة
        ]
        
        # كلمات تدل على عدم اليقين (إيجابية)
        self.uncertainty_words = [
            'يُذكر أن', 'من المحتمل', 'يبدو أن', 'وفقاً للمصادر',
            'حسب علمي', 'في ضوء المتاح', 'لا أملك معلومات دقيقة'
        ]
        
    async def verify_response(self, response: str, user_query: str) -> Dict[str, Any]:
        """فحص شامل لرد غسان للتأكد من دقته"""
        
        verification_result = {
            'overall_score': 0.0,
            'warnings': [],
            'suggestions': [],
            'is_reliable': True,
            'confidence_level': 'متوسط'
        }
        
        # فحص الأنماط المشبوهة
        suspicious_score = self._check_suspicious_patterns(response)
        
        # فحص استخدام كلمات عدم اليقين
        uncertainty_score = self._check_uncertainty_usage(response)
        
        # فحص المعلومات المحددة
        specific_info_score = self._check_specific_information(response)
        
        # فحص الأسماء والكيانات
        names_score = await self._check_names_and_entities(response)
        
        # فحص السياق والتماسك
        context_score = self._check_context_consistency(response, user_query)
        
        # حساب النتيجة الإجمالية
        total_score = (
            suspicious_score * 0.3 +
            uncertainty_score * 0.2 +
            specific_info_score * 0.2 +
            names_score * 0.2 +
            context_score * 0.1
        )
        
        verification_result['overall_score'] = total_score
        
        # تحديد مستوى الثقة
        if total_score >= 0.8:
            verification_result['confidence_level'] = 'عالٍ'
            verification_result['is_reliable'] = True
        elif total_score >= 0.6:
            verification_result['confidence_level'] = 'متوسط'
            verification_result['is_reliable'] = True
        else:
            verification_result['confidence_level'] = 'منخفض'
            verification_result['is_reliable'] = False
            verification_result['warnings'].append('يحتاج مراجعة إضافية')
        
        return verification_result
    
    def _check_suspicious_patterns(self, text: str) -> float:
        """فحص الأنماط المشبوهة في النص"""
        warnings = []
        suspicious_count = 0
        
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, text)
            if matches:
                suspicious_count += len(matches)
                warnings.append(f'تم العثور على نمط مشبوه: {matches[0]}')
        
        # كلما قل عدد الأنماط المشبوهة، كلما ارتفعت النتيجة
        score = max(0.0, 1.0 - (suspicious_count * 0.3))
        return score
    
    def _check_uncertainty_usage(self, text: str) -> float:
        """فحص استخدام عبارات عدم اليقين (شيء إيجابي)"""
        uncertainty_count = 0
        
        for word in self.uncertainty_words:
            if word in text:
                uncertainty_count += 1
        
        # استخدام عبارات عدم اليقين شيء إيجابي
        score = min(1.0, uncertainty_count * 0.2 + 0.5)
        return score
    
    def _check_specific_information(self, text: str) -> float:
        """فحص المعلومات المحددة جداً"""
        # البحث عن معلومات محددة جداً قد تكون مختلقة
        specific_patterns = [
            r'\d{4}م',  # تواريخ محددة
            r'\d{4}هـ',
            r'\d+ عاماً',  # أعمار محددة
            r'\d+ كتاباً',  # أرقام كتب محددة
            r'في يوم \d+',  # تواريخ يومية محددة
        ]
        
        specific_count = 0
        for pattern in specific_patterns:
            matches = re.findall(pattern, text)
            specific_count += len(matches)
        
        # توازن: بعض التحديد طبيعي، لكن الكثير منه مشبوه
        if specific_count == 0:
            return 0.7  # لا توجد تفاصيل محددة
        elif specific_count <= 3:
            return 0.9  # تفاصيل معقولة
        else:
            return 0.3  # تفاصيل كثيرة مشبوهة
    
    async def _check_names_and_entities(self, text: str) -> float:
        """فحص الأسماء والكيانات المذكورة"""
        score = 1.0
        warnings = []
        
        # استخراج الأسماء المحتملة
        potential_names = re.findall(r'[أ-ي]+\s+[أ-ي]+', text)
        
        for name in potential_names:
            if len(name) > 20:  # أسماء طويلة جداً مشبوهة
                score -= 0.1
                warnings.append(f'اسم مشبوه: {name}')
        
        return max(0.0, score)
    
    def _check_context_consistency(self, response: str, user_query: str) -> float:
        """فحص تماسك السياق والاستجابة للسؤال"""
        # فحص بسيط: هل الرد يحتوي على كلمات من السؤال؟
        query_words = set(user_query.lower().split())
        response_words = set(response.lower().split())
        
        # نسبة الكلمات المشتركة
        common_words = query_words.intersection(response_words)
        if len(query_words) == 0:
            return 0.5
        
        relevance_score = len(common_words) / len(query_words)
        return min(1.0, relevance_score + 0.3)  # حد أدنى 0.3
    
    def generate_reliability_report(self, verification_result: Dict[str, Any]) -> str:
        """إنشاء تقرير موثوقية للرد"""
        score = verification_result['overall_score']
        level = verification_result['confidence_level']
        
        if score >= 0.8:
            return f"✅ هذا الرد موثوق بدرجة {level} ({score:.1%})"
        elif score >= 0.6:
            return f"⚠️ هذا الرد مقبول بدرجة ثقة {level} ({score:.1%}) - يُفضل مراجعة إضافية"
        else:
            return f"❌ هذا الرد يحتاج مراجعة دقيقة - موثوقية {level} ({score:.1%})"
    
    async def suggest_improvements(self, response: str, verification_result: Dict[str, Any]) -> List[str]:
        """اقتراح تحسينات للرد"""
        suggestions = []
        
        if verification_result['overall_score'] < 0.6:
            suggestions.append("أضف عبارات مثل 'وفقاً للمصادر المتاحة' أو 'حسب علمي'")
        
        if len(verification_result['warnings']) > 0:
            suggestions.append("راجع المعلومات المحددة والتواريخ الدقيقة")
        
        # فحص عدم وجود عبارات عدم اليقين
        has_uncertainty = any(word in response for word in self.uncertainty_words)
        if not has_uncertainty and len(response) > 100:
            suggestions.append("أضف عبارات تدل على حدود المعرفة عند الضرورة")
        
        return suggestions

# إنشاء مثيل خدمة التحقق
information_verifier = InformationVerificationService()