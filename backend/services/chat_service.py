from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime
import uuid
import logging

from .search_service import web_search_service
from .llm_service import ghassan_llm_service
from .claude_service import claude_direct_service
from .tavily_service import tavily_search_service
from data.omani_knowledge_base import OMANI_LITERATURE_KNOWLEDGE_BASE, EXTRACTED_KNOWLEDGE
from data.omani_curriculum import OMANI_ARABIC_CURRICULUM

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, db):
        self.db = db
        self.messages_collection: AsyncIOMotorCollection = db.messages
        self.sessions_collection: AsyncIOMotorCollection = db.sessions
    
    async def process_user_message(
        self,
        message_text: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """معالجة رسالة المستخدم مع تذكر السياق"""
        
        try:
            # إنشاء session_id جديد إذا لم يكن موجوداً
            if not session_id:
                session_id = await self._create_new_session()
            
            # **جلب المحادثة السابقة للسياق**
            recent_messages = await self.get_chat_history(session_id, limit=5)
            conversation_context = self._build_conversation_context(recent_messages)
            
            # حفظ رسالة المستخدم
            user_message = await self._save_message(
                text=message_text,
                sender='user',
                session_id=session_id
            )
            
            # تحديد إذا كان يحتاج بحث
            needs_search = self._message_needs_search(message_text)
            search_results = []
            
            # **تحديد المرحلة التعليمية للطالب**
            student_level = self._detect_student_level(message_text, conversation_context)
            curriculum_context = self._get_curriculum_context(message_text, student_level)
            
            # البحث في قاعدة المعرفة المحلية أولاً
            local_knowledge = self._search_local_knowledge_base(message_text)
            
            # تحديد إذا كان يحتاج بحث خارجي
            if needs_search and not local_knowledge:
                logger.info(f"رسالة تحتاج بحث متقدم بـ Tavily: {message_text}")
                
                # استخدام Tavily للبحث المتقدم
                tavily_results = await tavily_search_service.search_omani_literature_advanced(message_text)
                
                # تحويل نتائج Tavily لصيغة موحدة
                search_results = self._convert_tavily_to_standard_format(tavily_results)
            else:
                search_results = []
                if local_knowledge:
                    # تحويل المعرفة المحلية لصيغة search_results
                    search_results = [{
                        'title': f"معلومات من قاعدة المعرفة: {local_knowledge['source']}",
                        'content': local_knowledge['content'],
                        'source': 'قاعدة المعرفة المحلية',
                        'reliability_score': local_knowledge.get('reliability', 0.95)
                    }]
            
            # تحديد إذا كان يحتاج تحليل أدبي متقدم
            needs_advanced_analysis = self._needs_advanced_literary_analysis(message_text)
            use_claude = self._should_use_claude_analysis(message_text)
            
            # توليد رد غسان - معالجة سريعة ومبسطة
            logger.info(f"معالجة سريعة للرسالة: {message_text[:50]}...")
            llm_response = await ghassan_llm_service.generate_response_with_search(
                message_text, 
                search_results=search_results,
                session_id=session_id,
                use_claude=use_claude,
                conversation_context=conversation_context
            )
            
            # التحقق إذا كان الرد يحتاج روابط خارجية بديلة
            needs_external_links = self._needs_external_links_fallback(llm_response['text'], message_text)
            
            if needs_external_links:
                logger.info(f"البحث عن روابط خارجية بديلة: {message_text}")
                external_links = await self._generate_external_links(message_text)
                if external_links:
                    llm_response['text'] += "\n\n" + external_links
                    llm_response['has_external_links'] = True
            
            # حفظ رد غسان
            ghassan_message = await self._save_message(
                text=llm_response['text'],
                sender='ghassan',
                session_id=session_id,
                metadata={
                    'model_used': llm_response.get('model_used'),
                    'has_web_search': needs_search,
                    'search_results_count': len(search_results),
                    'has_external_links': llm_response.get('has_external_links', False)
                }
            )
            
            # تحديث معلومات الجلسة
            await self._update_session(session_id, llm_response['text'])
            
            return {
                'message_id': str(ghassan_message['_id']),
                'text': llm_response['text'],
                'session_id': session_id,
                'timestamp': ghassan_message['timestamp'],
                'has_web_search': needs_search,
                'model_used': llm_response.get('model_used', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الرسالة: {e}")
            # رد تلقائي في حالة الخطأ
            return {
                'message_id': str(uuid.uuid4()),
                'text': 'عذراً، واجهت مشكلة تقنية. أرجو المحاولة مرة أخرى.',
                'session_id': session_id or str(uuid.uuid4()),
                'timestamp': datetime.utcnow(),
                'has_web_search': False,
                'model_used': 'error',
                'error': str(e)
            }
    
    async def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """جلب تاريخ المحادثات لجلسة معينة"""
        try:
            messages = await self.messages_collection.find(
                {'session_id': session_id}
            ).sort('timestamp', 1).limit(limit).to_list(limit)
            
            return [self._format_message(msg) for msg in messages]
            
        except Exception as e:
            logger.error(f"خطأ في جلب تاريخ المحادثات: {e}")
            return []
    
    async def _create_new_session(self) -> str:
        """إنشاء جلسة جديدة"""
        session_id = str(uuid.uuid4())
        session_data = {
            '_id': session_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'message_count': 0,
            'title': 'محادثة جديدة مع غسان'
        }
        
        await self.sessions_collection.insert_one(session_data)
        return session_id
    
    async def _save_message(
        self,
        text: str,
        sender: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """حفظ رسالة في قاعدة البيانات"""
        message_data = {
            '_id': str(uuid.uuid4()),
            'text': text,
            'sender': sender,
            'session_id': session_id,
            'timestamp': datetime.utcnow(),
            'metadata': metadata or {}
        }
        
        await self.messages_collection.insert_one(message_data)
        return message_data
    
    async def _update_session(self, session_id: str, last_message: str):
        """تحديث معلومات الجلسة"""
        await self.sessions_collection.update_one(
            {'_id': session_id},
            {
                '$set': {
                    'updated_at': datetime.utcnow(),
                    'last_message': last_message[:100] + '...' if len(last_message) > 100 else last_message
                },
                '$inc': {'message_count': 1}
            }
        )
    
    def _message_needs_search(self, message: str) -> bool:
        """تحديد إذا كانت الرسالة تحتاج بحث خارجي - مع تقليل البحث للسرعة"""
        
        # قائمة أضيق للبحث - فقط الحالات التي تحتاج بحث فعلي
        critical_search_indicators = [
            'أخبرني عن', 'معلومات عن', 'من هو', 'من هي',
            'أعمال', 'مؤلفات', 'كتب', 'دواوين'
        ]
        
        message_lower = message.lower()
        
        # تحقق أولاً إذا كانت المعلومات متوفرة محلياً
        has_local_info = any(name.lower() in message_lower 
                           for name in EXTRACTED_KNOWLEDGE['omani_literary_figures'])
        
        # إذا كانت المعلومات متوفرة محلياً، لا تبحث خارجياً (توفير الوقت)
        if has_local_info:
            return False
            
        # ابحث خارجياً فقط للحالات الحرجة
        return any(indicator in message_lower for indicator in critical_search_indicators)
    
    def _needs_advanced_literary_analysis(self, message: str) -> bool:
        """تحديد إذا كانت الرسالة تحتاج تحليل أدبي متقدم"""
        advanced_keywords = [
            'تحليل', 'نقد', 'إعراب', 'بلاغة', 'عروض', 'بحر شعري', 
            'قافية', 'استعارة', 'كناية', 'مجاز', 'تشبيه',
            'بنية', 'أسلوب', 'نظرية', 'منهج', 'مدرسة أدبية',
            'نحو', 'صرف', 'بديع', 'بيان', 'معاني'
        ]
        
        return any(keyword in message.lower() for keyword in advanced_keywords)
    
    def _should_use_claude_analysis(self, message: str) -> bool:
        """تحديد متى نستخدم Claude - مع تقليل الاستخدام للسرعة"""
        # استخدم Claude فقط للتحليل المعقد حقاً
        complex_analysis_keywords = [
            'إعراب', 'تحليل نحوي', 'بلاغة', 'عروض', 
            'تحليل أدبي متقدم', 'نقد متخصص'
        ]
        
        return any(keyword in message.lower() for keyword in complex_analysis_keywords)
    
    def _format_search_context(self, search_results: List[Dict[str, Any]]) -> str:
        """تنسيق نتائج البحث لـ Claude"""
        if not search_results:
            return ""
        
        context = "--- معلومات من المصادر الموثوقة ---\n"
        for result in search_results:
            context += f"• {result.get('title', 'N/A')}\n"
            context += f"المصدر: {result.get('source', 'N/A')}\n"
            context += f"المحتوى: {result.get('content', '')[:200]}...\n\n"
        
        return context
    
    def _convert_tavily_to_standard_format(self, tavily_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """تحويل نتائج Tavily إلى الصيغة الموحدة"""
        if not tavily_results.get('results'):
            return []
        
        standard_results = []
        for result in tavily_results['results']:
            standard_result = {
                'title': result.get('title', ''),
                'content': result.get('content', ''),
                'url': result.get('url', ''),
                'source': f"Tavily - {result.get('source_type', 'مصدر موثوق')}",
                'reliability_score': result.get('reliability_rating', 0.8),
                'search_engine': 'tavily_advanced',
                'omani_keywords': result.get('omani_keywords', [])
            }
            standard_results.append(standard_result)
        
        return standard_results
    
    def _build_conversation_context(self, recent_messages: List[Dict[str, Any]]) -> str:
        """بناء سياق المحادثة من الرسائل السابقة"""
        if not recent_messages:
            return ""
        
        context = "--- سياق المحادثة السابقة ---\n"
        
        for msg in recent_messages[-4:]:  # آخر 4 رسائل فقط
            sender = "المستخدم" if msg['sender'] == 'user' else "غسان"
            context += f"{sender}: {msg['text'][:100]}...\n"
        
        context += "--- نهاية السياق ---\n"
        context += "**تذكر:** استخدم هذا السياق لتجنب تكرار المعلومات وربط الأسئلة الجديدة بما سبق.\n"
        
        return context
    
    def _search_local_knowledge_base(self, query: str) -> Optional[Dict[str, Any]]:
        """البحث في قاعدة المعرفة المحلية"""
        query_lower = query.lower()
        
        # البحث في الشخصيات الأدبية
        for figure in EXTRACTED_KNOWLEDGE['omani_literary_figures']:
            if figure.lower() in query_lower:
                # البحث عن التفاصيل في قاعدة البيانات
                for category in OMANI_LITERATURE_KNOWLEDGE_BASE.values():
                    if isinstance(category, dict):
                        # البحث في الشعراء
                        if 'poets' in category:
                            for poet in category['poets']:
                                if poet['name'] == figure:
                                    return {
                                        'content': f"الشاعر {poet['name']} من {poet.get('period', 'العصر القديم')}، {poet.get('significance', '')}. {poet.get('notes', '')}",
                                        'source': 'الحياة الأدبية في عُمان - الجهضمي',
                                        'reliability': 0.95,
                                        'type': 'poet'
                                    }
                        
                        # البحث في كتاب النثر
                        if 'writers' in category:
                            for writer in category['writers']:
                                if writer['name'] == figure:
                                    return {
                                        'content': f"{writer['name']} {writer.get('type', '')} من {writer.get('family', '')}. {writer.get('significance', '')}. من أعماله: {writer.get('famous_work', '')}.",
                                        'source': 'الحياة الأدبية في عُمان - الجهضمي',
                                        'reliability': 0.95,
                                        'type': 'prose_writer'
                                    }
                        
                        # البحث في العلماء
                        if 'scholars' in category:
                            for scholar in category['scholars']:
                                if scholar['name'] == figure:
                                    return {
                                        'content': f"{scholar['name']} {scholar.get('title', '')}. من أعماله: {scholar.get('works', '')}. {scholar.get('significance', '')}.",
                                        'source': 'الحياة الأدبية في عُمان - الجهضمي',
                                        'reliability': 0.95,
                                        'type': 'scholar'
                                    }
        
        # البحث في المفاهيم الأساسية
        for concept in EXTRACTED_KNOWLEDGE['key_concepts']:
            if any(word in query_lower for word in concept.lower().split()):
                return {
                    'content': f"من المفاهيم المهمة في الأدب العُماني القديم: {concept}. وفقاً لدراسة الجهضمي الأكاديمية حول الحياة الأدبية في عُمان حتى 134هـ.",
                    'source': 'قاعدة المعرفة الأكاديمية',
                    'reliability': 0.9,
                    'type': 'concept'
                }
        
        # البحث في الأعمال الأدبية
        for work in EXTRACTED_KNOWLEDGE['literary_works']:
            if any(word in work.lower() for word in query_lower.split() if len(word) > 3):
                return {
                    'content': f"من الأعمال الأدبية العُمانية القديمة: {work}. مذكور في الدراسات الأكاديمية حول تاريخ الأدب العُماني.",
                    'source': 'الأعمال الأدبية العُمانية القديمة',
                    'reliability': 0.9,
                    'type': 'literary_work'
                }
        
        return None
    
    def _needs_external_links_fallback(self, response: str, query: str) -> bool:
        """تحديد إذا كان الرد يحتاج روابط خارجية بديلة"""
        
        # عبارات تدل على عدم توفر معلومات كافية
        fallback_indicators = [
            "لا أملك معلومات",
            "لا أعرف",
            "غير متوفرة",
            "أحتاج للتحقق",
            "من المفيد البحث",
            "مصادر إضافية",
            "معلومات محدودة"
        ]
        
        response_lower = response.lower()
        has_insufficient_info = any(indicator in response_lower for indicator in fallback_indicators)
        
        # أيضاً إذا كان الرد قصير جداً (أقل من 100 حرف)
        is_too_short = len(response.strip()) < 100
        
        return has_insufficient_info or is_too_short
    
    async def _generate_external_links(self, query: str) -> str:
        """توليد روابط خارجية مفيدة عند عدم توفر إجابة مباشرة"""
        
        try:
            # تحسين استعلام البحث للحصول على مصادر موثوقة
            enhanced_query = f"{query} site:nizwa.om OR site:omandaily.om OR site:moe.gov.om OR site:heritage.gov.om OR site:squ.edu.om"
            
            # البحث باستخدام Tavily
            search_results = await tavily_search_service.search_omani_literature_advanced(
                enhanced_query, 
                max_results=6
            )
            
            if not search_results.get('results'):
                return ""
            
            # تنسيق الروابط
            links_text = "\n\n📚 **لم تتوفر إجابة مباشرة، لكن إليك مصادر موثوقة ذات صلة:**\n\n"
            
            for i, result in enumerate(search_results['results'][:5], 1):
                title = result.get('title', 'مصدر مفيد')
                url = result.get('url', '')
                source_type = result.get('source_type', 'مصدر')
                
                # تنظيف العنوان وتقصيره إذا كان طويلاً
                if len(title) > 60:
                    title = title[:57] + "..."
                
                # إضافة رمز حسب نوع المصدر
                icon = "📖" if "academic" in source_type else "📰" if "news" in source_type else "🔗"
                
                links_text += f"• {icon} **{title}**\n"
                links_text += f"  {url}\n\n"
            
            links_text += "💡 **نصيحة**: اضغط على الروابط للحصول على معلومات مفصلة من مصادر موثوقة."
            
            return links_text
            
        except Exception as e:
            logger.error(f"خطأ في توليد الروابط الخارجية: {e}")
            return ""
    
    def _detect_student_level(self, message: str, context: str) -> str:
        """كشف المرحلة التعليمية للطالب من الرسالة والسياق"""
        
        message_lower = message.lower()
        context_lower = context.lower() if context else ""
        combined = message_lower + " " + context_lower
        
        # كشف المرحلة من العبارات المباشرة
        if any(phrase in combined for phrase in ['صف أول', 'صف ثاني', 'صف ثالث', 'صف رابع']):
            return "primary"
        elif any(phrase in combined for phrase in ['صف خامس', 'صف سادس', 'صف سابع', 'صف ثامن', 'صف تاسع']):
            return "middle"
        elif any(phrase in combined for phrase in ['صف عاشر', 'صف حادي', 'صف ثاني عشر', 'ثانوية']):
            return "secondary"
        
        # كشف المرحلة من مستوى السؤال
        # أسئلة بسيطة تشير للمرحلة الابتدائية
        if any(phrase in combined for phrase in ['ما هو', 'اشرح لي', 'بسيط', 'سهل', 'أريد أن أفهم']):
            return "primary"
        
        # أسئلة متوسطة تشير للمرحلة الإعدادية
        elif any(phrase in combined for phrase in ['حلل', 'قارن', 'ما الفرق', 'أسلوب', 'بحر شعري']):
            return "middle"
        
        # أسئلة متقدمة تشير للمرحلة الثانوية
        elif any(phrase in combined for phrase in ['نقد', 'نظرية', 'منهج', 'دراسة مقارنة', 'أطروحة']):
            return "secondary"
        
        return "general"  # مستوى عام إذا لم يتم تحديد المرحلة
    
    def _get_curriculum_context(self, message: str, student_level: str) -> str:
        """الحصول على السياق التعليمي المناسب للمرحلة"""
        
        if student_level == "primary":
            return self._get_primary_context(message)
        elif student_level == "middle":
            return self._get_middle_context(message) 
        elif student_level == "secondary":
            return self._get_secondary_context(message)
        else:
            return ""
    
    def _get_primary_context(self, message: str) -> str:
        """سياق للمرحلة الابتدائية (1-4)"""
        context = """

📚 **السياق التعليمي - المرحلة الابتدائية:**

أهداف التعلم:
• شرح بلغة بسيطة ومفهومة للأطفال
• استخدام أمثلة من البيئة العُمانية المألوفة
• ربط الأدب بالحياة اليومية للطفل العُماني
• التشجيع على الحفظ والإلقاء
• إثارة الحب للغة العربية والأدب

المحتوى المناسب:
• الحكايات العُمانية البسيطة
• الأناشيد الوطنية للأطفال  
• أسماء الأماكن والحيوانات العُمانية
• القيم الأخلاقية من خلال القصص

أسلوب الشرح:
• جمل قصيرة وواضحة
• أمثلة حية من البيئة المحلية
• تشجيع وتحفيز مستمر
• لغة ودودة ومرحة مناسبة للأطفال

"""
        return context
    
    def _get_middle_context(self, message: str) -> str:
        """سياق للمرحلة الإعدادية (5-9)"""
        context = """

🎓 **السياق التعليمي - المرحلة الإعدادية:**

أهداف التعلم:
• تطوير مهارات التحليل الأدبي الأساسي
• فهم تاريخ الأدب العُماني وتطوره
• ربط النصوص بالسياق التاريخي والثقافي
• تنمية الذوق الأدبي والجمالي
• مقارنة الأساليب الأدبية المختلفة

المحتوى المناسب:
• نصوص من الشعراء العُمانيين المعروفين
• قصص من التراث العُماني المكتوب
• أعمال الأدباء العُمانيين المعاصرين
• الحركات الأدبية في عُمان

أسلوب الشرح:
• تحليل متدرج ومنطقي
• أمثلة من المنهج الدراسي
• ربط بالثقافة العُمانية
• تحفيز التفكير النقدي البناء

"""
        return context
    
    def _get_secondary_context(self, message: str) -> str:
        """سياق للمرحلة الثانوية (10-12)"""
        context = """

🎯 **السياق التعليمي - المرحلة الثانوية:**

أهداف التعلم:
• إتقان النقد الأدبي المتخصص والمنهجي
• فهم النظريات الأدبية وتطبيقها
• البحث الأدبي المستقل والأكاديمي
• تحليل الأدب العُماني في السياق العربي والعالمي
• الإعداد للدراسات الجامعية المتخصصة

المحتوى المناسب:
• دراسة أعمال كاملة للأدباء العُمانيين
• تحليل معمق للنصوص الأدبية المعقدة
• مناهج النقد الأدبي الحديث
• الأدب المقارن والدراسات المتقدمة

أسلوب الشرح:
• تحليل أكاديمي متخصص
• استخدام المصطلحات النقدية الدقيقة
• منهجية علمية واضحة
• تحفيز البحث والاستكشاف المستقل
• إعداد للمرحلة الجامعية

"""
        return context
    
    def _format_message(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """تنسيق الرسالة للإرسال للعميل"""
        return {
            'id': msg['_id'],
            'text': msg['text'],
            'sender': msg['sender'],
            'timestamp': msg['timestamp'].isoformat(),
            'hasWebSearch': msg.get('metadata', {}).get('has_web_search', False),
            'modelUsed': msg.get('metadata', {}).get('model_used')
        }