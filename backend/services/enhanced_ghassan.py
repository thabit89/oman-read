from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from services.rag_service import AdvancedRAGService
from services.claude_service import claude_direct_service
from services.llm_service import ghassan_llm_service

logger = logging.getLogger(__name__)

class EnhancedGhassanService:
    """غسان المطور - نظام متكامل مع RAG وقاعدة معرفة شاملة"""
    
    def __init__(self, db):
        self.db = db
        self.rag_service = AdvancedRAGService(db)
    
    async def process_intelligent_query(
        self, 
        user_message: str, 
        session_id: str,
        conversation_context: str = ""
    ) -> Dict[str, Any]:
        """معالجة ذكية ومتقدمة لاستعلامات المستخدم"""
        
        try:
            # البحث الشامل وتجميع السياق
            rag_results = await self.rag_service.comprehensive_search_and_answer(
                user_message, 
                session_id
            )
            
            # تحديد نوع الاستجابة المطلوبة
            response_strategy = self._determine_response_strategy(
                user_message, 
                rag_results,
                conversation_context
            )
            
            # توليد الرد المناسب
            if response_strategy['use_claude'] and response_strategy['needs_deep_analysis']:
                # تحليل أدبي متقدم مع Claude
                response = await self._generate_claude_analysis(
                    user_message,
                    rag_results['context'],
                    conversation_context,
                    session_id
                )
            else:
                # رد عام محسن مع GPT
                response = await self._generate_enhanced_response(
                    user_message,
                    rag_results['context'], 
                    conversation_context,
                    session_id,
                    response_strategy
                )
            
            # تحسين الرد بناءً على جودة السياق
            final_response = self._enhance_response_based_on_context(
                response,
                rag_results,
                response_strategy
            )
            
            return {
                'text': final_response,
                'model_used': response.get('model_used', 'enhanced_ghassan'),
                'sources_used': rag_results['sources_found'],
                'context_confidence': rag_results.get('confidence_level', 'متوسط'),
                'response_strategy': response_strategy['strategy_type'],
                'has_verified_sources': rag_results['sources_found'] > 0
            }
            
        except Exception as e:
            logger.error(f"خطأ في المعالجة الذكية: {e}")
            return {
                'text': 'عذراً، حدث خطأ في المعالجة المتقدمة للاستعلام.',
                'model_used': 'error',
                'sources_used': 0,
                'error': str(e)
            }
    
    def _determine_response_strategy(
        self, 
        query: str, 
        rag_results: Dict[str, Any],
        context: str
    ) -> Dict[str, Any]:
        """تحديد استراتيجية الرد المثلى"""
        
        strategy = {
            'strategy_type': 'general_informative',
            'use_claude': False,
            'needs_deep_analysis': False,
            'priority_sources': 'mixed',
            'response_length': 'medium'
        }
        
        query_lower = query.lower()
        
        # تحليل أدبي متقدم
        if any(word in query_lower for word in ['تحليل', 'نقد', 'إعراب', 'بلاغة']):
            strategy.update({
                'strategy_type': 'deep_literary_analysis',
                'use_claude': True,
                'needs_deep_analysis': True,
                'response_length': 'detailed'
            })
        
        # استفسار عن مؤلف محدد
        elif any(word in query_lower for word in ['من هو', 'أخبرني عن']):
            if rag_results['sources_found'] > 2:
                strategy.update({
                    'strategy_type': 'comprehensive_biography',
                    'priority_sources': 'biographical',
                    'response_length': 'detailed'
                })
            else:
                strategy.update({
                    'strategy_type': 'careful_limited_info',
                    'response_length': 'cautious'
                })
        
        # استفسار عن أعمال
        elif any(word in query_lower for word in ['مؤلفات', 'أعمال', 'كتب']):
            if rag_results.get('confidence_level') == 'عالٍ':
                strategy.update({
                    'strategy_type': 'verified_works_list',
                    'priority_sources': 'bibliographic'
                })
            else:
                strategy.update({
                    'strategy_type': 'cautious_works_inquiry',
                    'response_length': 'cautious'
                })
        
        return strategy
    
    async def _generate_claude_analysis(
        self, 
        query: str,
        context: str, 
        conversation_context: str,
        session_id: str
    ) -> Dict[str, Any]:
        """توليد تحليل أدبي متقدم مع Claude"""
        
        enhanced_context = f"""
        {conversation_context}
        
        السياق من قاعدة المعرفة:
        {context}
        
        المطلوب: {query}
        
        قدم تحليلاً أدبياً أو نحوياً متخصصاً وعميقاً.
        """
        
        return await claude_direct_service.analyze_literary_text(
            user_message=query,
            search_context=enhanced_context,
            session_id=session_id
        )
    
    async def _generate_enhanced_response(
        self,
        query: str,
        context: str,
        conversation_context: str, 
        session_id: str,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """توليد رد محسن مع GPT"""
        
        # تخصيص التعليمات حسب الاستراتيجية
        strategy_instructions = self._get_strategy_instructions(strategy)
        
        enhanced_context = f"""
        {conversation_context}
        
        السياق من قاعدة المعرفة:
        {context}
        
        المطلوب: {query}
        
        استراتيجية الرد: {strategy['strategy_type']}
        {strategy_instructions}
        """
        
        return await ghassan_llm_service.generate_response_with_search(
            user_message=query,
            search_results=[],  # السياق مُجمع مسبقاً
            session_id=session_id,
            use_claude=False,
            conversation_context=enhanced_context
        )
    
    def _get_strategy_instructions(self, strategy: Dict[str, Any]) -> str:
        """الحصول على تعليمات مخصصة لكل استراتيجية"""
        
        instructions = {
            'comprehensive_biography': """
            - قدم معلومات شاملة من المصادر الموثوقة
            - اذكر المصادر عالية الثقة إذا كانت متوفرة
            - كن مفيداً ومعلوماتياً
            """,
            
            'careful_limited_info': """
            - اعترف بمحدودية المصادر المتاحة
            - قدم ما هو مؤكد فقط
            - اقترح البحث في مصادر إضافية
            """,
            
            'verified_works_list': """
            - اذكر الأعمال الموثقة من المصادر عالية الثقة
            - ميز بين المؤكد وغير المؤكد
            - رتب المعلومات بوضوح
            """,
            
            'cautious_works_inquiry': """
            - كن حذراً جداً من ذكر عناوين محددة
            - اعتمد فقط على المصادر الموثوقة جداً
            - إذا لم تجد مصادر كافية، قل ذلك صراحة
            """
        }
        
        return instructions.get(strategy['strategy_type'], "قدم رداً مفيداً ودقيقاً.")
    
    def _enhance_response_based_on_context(
        self,
        response: Dict[str, Any], 
        rag_results: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> str:
        """تحسين الرد بناءً على جودة السياق"""
        
        base_response = response.get('text', '')
        
        # إضافة ملاحظات حسب مستوى الثقة
        if rag_results.get('confidence_level') == 'منخفض' and strategy['strategy_type'] != 'cautious_works_inquiry':
            base_response += "\n\nملاحظة: المعلومات المتاحة محدودة، قد تحتاج للتحقق من مصادر إضافية."
        
        elif rag_results['sources_found'] > 5:
            base_response += f"\n\nاستندت هذه المعلومات إلى {rag_results['sources_found']} مصدر موثوق."
        
        return base_response

# سيتم تهيئته في الخادم الرئيسي
enhanced_ghassan_service = None