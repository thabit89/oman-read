from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from models.literature_models import Author, LiteraryWork, AcademicSource
from services.embeddings_service import EmbeddingsService
from services.academic_collector import academic_collector
from services.tavily_service import tavily_search_service

logger = logging.getLogger(__name__)

class AdvancedRAGService:
    """نظام RAG متقدم للأدب العُماني"""
    
    def __init__(self, db):
        self.db = db
        self.embeddings_service = EmbeddingsService(db)
        
        # مجموعات قاعدة البيانات
        self.authors_collection = db.authors
        self.works_collection = db.literary_works
        self.sources_collection = db.academic_sources
        self.queries_collection = db.search_queries
    
    async def comprehensive_search_and_answer(
        self, 
        user_query: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """البحث الشامل والإجابة المتقدمة"""
        
        try:
            # تسجيل الاستعلام
            await self._log_search_query(user_query, session_id)
            
            # تحليل نوع الاستعلام
            query_analysis = self._analyze_query_type(user_query)
            
            # البحث المتعدد المصادر
            search_results = await self._multi_source_search(user_query, query_analysis)
            
            # البحث الدلالي في قاعدة البيانات المحلية
            semantic_results = await self.embeddings_service.semantic_search(
                user_query, 
                limit=5
            )
            
            # دمج النتائج وترتيبها
            combined_results = self._merge_and_rank_results(
                search_results, 
                semantic_results,
                query_analysis
            )
            
            # تحضير السياق للذكاء الاصطناعي
            context = self._prepare_rag_context(combined_results, query_analysis)
            
            return {
                'query': user_query,
                'query_type': query_analysis['type'],
                'context': context,
                'sources_found': len(combined_results),
                'semantic_matches': len(semantic_results),
                'external_sources': len(search_results.get('results', [])),
                'confidence_level': self._calculate_context_confidence(combined_results)
            }
            
        except Exception as e:
            logger.error(f"خطأ في RAG المتقدم: {e}")
            return {
                'query': user_query,
                'context': "",
                'error': str(e),
                'sources_found': 0
            }
    
    def _analyze_query_type(self, query: str) -> Dict[str, Any]:
        """تحليل نوع الاستعلام لتحسين البحث"""
        
        query_lower = query.lower()
        
        analysis = {
            'type': 'general',
            'target_author': None,
            'target_work': None,
            'analysis_needed': False,
            'search_priority': 'balanced'
        }
        
        # فحص إذا كان السؤال عن مؤلف معين
        for author in academic_collector.known_omani_authors:
            if author.lower() in query_lower:
                analysis['type'] = 'author_specific'
                analysis['target_author'] = author
                analysis['search_priority'] = 'author_focused'
                break
        
        # فحص إذا كان السؤال يحتاج تحليل أدبي
        analytical_keywords = ['تحليل', 'نقد', 'إعراب', 'بلاغة', 'أسلوب']
        if any(keyword in query_lower for keyword in analytical_keywords):
            analysis['analysis_needed'] = True
            analysis['search_priority'] = 'analytical'
        
        # فحص إذا كان السؤال عن مؤلفات محددة
        work_keywords = ['مؤلفات', 'أعمال', 'كتب', 'دواوين', 'روايات']
        if any(keyword in query_lower for keyword in work_keywords):
            analysis['type'] = 'works_inquiry'
            analysis['search_priority'] = 'works_focused'
        
        return analysis
    
    async def _multi_source_search(
        self, 
        query: str, 
        query_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """البحث متعدد المصادر"""
        
        search_results = {'results': [], 'sources': []}
        
        try:
            # البحث الخارجي بـ Tavily
            if query_analysis['target_author']:
                # بحث مخصص للمؤلف
                tavily_results = await tavily_search_service.search_specific_author(
                    query_analysis['target_author']
                )
            else:
                # بحث عام
                tavily_results = await tavily_search_service.search_omani_literature_advanced(query)
            
            search_results['results'] = tavily_results.get('results', [])
            search_results['sources'].append('tavily_advanced')
            
            # البحث في قاعدة المعرفة المحلية إذا كانت متاحة
            local_results = await self._search_local_knowledge(query, query_analysis)
            if local_results:
                search_results['results'].extend(local_results)
                search_results['sources'].append('local_knowledge')
            
        except Exception as e:
            logger.error(f"خطأ في البحث متعدد المصادر: {e}")
        
        return search_results
    
    async def _search_local_knowledge(
        self, 
        query: str, 
        query_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """البحث في قاعدة المعرفة المحلية"""
        
        local_results = []
        
        try:
            # البحث في المؤلفين
            if query_analysis['type'] in ['author_specific', 'general']:
                authors_cursor = self.authors_collection.find({
                    '$text': {'$search': query}
                }).limit(3)
                
                async for author_doc in authors_cursor:
                    local_results.append({
                        'title': f"معلومات عن {author_doc.get('full_name', 'مؤلف')}",
                        'content': author_doc.get('biography', ''),
                        'source_type': 'local_author',
                        'reliability_rating': 0.95,  # عالية للمحتوى المحلي المحقق
                        'metadata': {
                            'author_id': author_doc.get('id'),
                            'genres': author_doc.get('main_genres', [])
                        }
                    })
            
            # البحث في الأعمال الأدبية
            if query_analysis['type'] in ['works_inquiry', 'general']:
                works_cursor = self.works_collection.find({
                    '$text': {'$search': query}
                }).limit(3)
                
                async for work_doc in works_cursor:
                    local_results.append({
                        'title': work_doc.get('title', 'عمل أدبي'),
                        'content': work_doc.get('summary', ''),
                        'source_type': 'local_work',
                        'reliability_rating': 0.95,
                        'metadata': {
                            'work_id': work_doc.get('id'),
                            'category': work_doc.get('category'),
                            'style': work_doc.get('style')
                        }
                    })
            
        except Exception as e:
            logger.error(f"خطأ في البحث المحلي: {e}")
        
        return local_results
    
    def _merge_and_rank_results(
        self, 
        external_results: Dict[str, Any],
        semantic_results: List[Dict[str, Any]],
        query_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """دمج وترتيب النتائج من مصادر متعددة"""
        
        combined = []
        
        # إضافة النتائج الخارجية
        for result in external_results.get('results', []):
            result['result_source'] = 'external'
            result['final_score'] = self._calculate_result_score(result, query_analysis)
            combined.append(result)
        
        # إضافة النتائج الدلالية
        for result in semantic_results:
            result['result_source'] = 'semantic'
            result['final_score'] = result['similarity_score'] * 1.2  # تفضيل المحتوى المحلي
            combined.append(result)
        
        # ترتيب حسب النتيجة النهائية
        combined.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return combined[:8]  # أفضل 8 نتائج
    
    def _calculate_result_score(
        self, 
        result: Dict[str, Any], 
        query_analysis: Dict[str, Any]
    ) -> float:
        """حساب نتيجة شاملة للنتيجة"""
        
        base_score = result.get('reliability_rating', 0.5)
        
        # مكافآت حسب نوع الاستعلام
        if query_analysis['type'] == 'author_specific':
            if result.get('source_type') in ['interview', 'local_author']:
                base_score += 0.3
        
        elif query_analysis['type'] == 'works_inquiry':
            if result.get('source_type') in ['book_metadata', 'local_work']:
                base_score += 0.3
        
        # مكافأة للمحتوى المحلي المحقق
        if result.get('result_source') == 'semantic':
            base_score += 0.2
        
        return min(1.0, base_score)
    
    def _prepare_rag_context(
        self, 
        results: List[Dict[str, Any]], 
        query_analysis: Dict[str, Any]
    ) -> str:
        """تحضير سياق RAG للذكاء الاصطناعي"""
        
        if not results:
            return "لم يتم العثور على مصادر موثوقة في قاعدة البيانات."
        
        context = f"نتائج البحث الشامل (نوع الاستعلام: {query_analysis['type']}):\n\n"
        
        high_confidence_results = [r for r in results if r.get('final_score', 0) > 0.7]
        medium_confidence_results = [r for r in results if 0.4 <= r.get('final_score', 0) <= 0.7]
        
        if high_confidence_results:
            context += "--- مصادر عالية الثقة ---\n"
            for i, result in enumerate(high_confidence_results[:4], 1):
                source_emoji = "📚" if result.get('result_source') == 'semantic' else "🌐"
                context += f"{i}. {source_emoji} {result.get('title', 'بلا عنوان')}\n"
                context += f"النوع: {result.get('source_type', 'غير محدد')}\n"
                context += f"المحتوى: {result.get('content', '')[:300]}...\n"
                context += f"الثقة: {result.get('final_score', 0):.2f}/1.0\n\n"
        
        if medium_confidence_results:
            context += "--- مصادر متوسطة الثقة (للاستئناس) ---\n"
            for i, result in enumerate(medium_confidence_results[:2], 1):
                context += f"{i}. {result.get('title', 'بلا عنوان')}\n"
                context += f"المحتوى: {result.get('content', '')[:150]}...\n\n"
        
        context += f"إجمالي المصادر: {len(results)} | البحث الدلالي: متاح"
        
        return context
    
    def _calculate_context_confidence(self, results: List[Dict[str, Any]]) -> str:
        """حساب مستوى الثقة في السياق المُجمع"""
        
        if not results:
            return "منخفض"
        
        avg_score = sum(r.get('final_score', 0) for r in results) / len(results)
        
        if avg_score >= 0.8:
            return "عالٍ"
        elif avg_score >= 0.6:
            return "متوسط"
        else:
            return "منخفض"
    
    async def _log_search_query(self, query: str, session_id: str):
        """تسجيل استعلامات البحث للتحليل"""
        try:
            query_record = {
                'query_text': query,
                'user_session': session_id,
                'timestamp': datetime.utcnow(),
                'search_type': self._analyze_query_type(query)['type']
            }
            
            await self.queries_collection.insert_one(query_record)
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل الاستعلام: {e}")
    
    async def add_verified_author(self, author_data: Dict[str, Any]) -> Dict[str, Any]:
        """إضافة مؤلف محقق لقاعدة البيانات"""
        try:
            # إنشاء سجل مؤلف
            author = Author(**author_data)
            
            # حفظ في قاعدة البيانات
            await self.authors_collection.insert_one(author.dict())
            
            # إنشاء التضمين المتجه
            embedding_id = await self.embeddings_service.create_author_embedding(author)
            
            logger.info(f"تم إضافة مؤلف محقق: {author.full_name}")
            
            return {
                'success': True,
                'author_id': author.id,
                'embedding_id': embedding_id,
                'message': f'تم إضافة {author.full_name} بنجاح'
            }
            
        except Exception as e:
            logger.error(f"خطأ في إضافة المؤلف: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def add_verified_work(self, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """إضافة عمل أدبي محقق لقاعدة البيانات"""
        try:
            # إنشاء سجل العمل الأدبي
            work = LiteraryWork(**work_data)
            
            # حفظ في قاعدة البيانات
            await self.works_collection.insert_one(work.dict())
            
            # إنشاء التضمين المتجه
            embedding_id = await self.embeddings_service.create_work_embedding(work)
            
            logger.info(f"تم إضافة عمل محقق: {work.title}")
            
            return {
                'success': True,
                'work_id': work.id,
                'embedding_id': embedding_id,
                'message': f'تم إضافة {work.title} بنجاح'
            }
            
        except Exception as e:
            logger.error(f"خطأ في إضافة العمل: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def auto_collect_and_process(self) -> Dict[str, Any]:
        """جمع ومعالجة تلقائية للمصادر"""
        try:
            logger.info("بدء الجمع التلقائي للمصادر الأكاديمية...")
            
            # جمع المصادر الشاملة
            collection_results = await academic_collector.collect_comprehensive_sources()
            
            # معالجة ومعداتة النتائج
            processing_stats = await self._process_collected_sources(collection_results)
            
            return {
                'collection_completed': True,
                'sources_collected': collection_results['total_collected'],
                'sources_processed': processing_stats['processed_count'],
                'embeddings_created': processing_stats['embeddings_count'],
                'completion_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في الجمع التلقائي: {e}")
            return {
                'collection_completed': False,
                'error': str(e)
            }
    
    async def _process_collected_sources(self, collection_results: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة المصادر المجمعة وتحويلها لسجلات منظمة"""
        
        processing_stats = {
            'processed_count': 0,
            'embeddings_count': 0,
            'errors': []
        }
        
        try:
            # معالجة الأبحاث الأكاديمية
            for paper in collection_results.get('academic_papers', []):
                try:
                    academic_source = AcademicSource(
                        title=paper['title'],
                        authors=[paper.get('covered_author', 'غير محدد')],
                        abstract=paper['abstract'],
                        url=paper.get('url'),
                        topic="الأدب العُماني",
                        covered_authors=[paper.get('covered_author', '')],
                        relevance_score=paper.get('reliability_score', 0.8)
                    )
                    
                    await self.sources_collection.insert_one(academic_source.dict())
                    processing_stats['processed_count'] += 1
                    
                except Exception as e:
                    processing_stats['errors'].append(f"خطأ في معالجة البحث: {e}")
            
            # معالجة المقابلات
            for interview in collection_results.get('interviews', []):
                try:
                    # إضافة كمصدر أكاديمي
                    interview_source = AcademicSource(
                        title=interview['title'],
                        authors=[interview.get('interviewee', 'غير محدد')],
                        abstract=interview['content'][:500],
                        full_text=interview.get('content'),
                        url=interview.get('url'),
                        topic=f"مقابلة مع {interview.get('interviewee', 'أديب عُماني')}",
                        covered_authors=[interview.get('interviewee', '')],
                        relevance_score=interview.get('reliability_score', 0.7)
                    )
                    
                    await self.sources_collection.insert_one(interview_source.dict())
                    processing_stats['processed_count'] += 1
                    
                except Exception as e:
                    processing_stats['errors'].append(f"خطأ في معالجة المقابلة: {e}")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة المصادر: {e}")
            processing_stats['errors'].append(str(e))
        
        return processing_stats
    
    async def get_rag_statistics(self) -> Dict[str, Any]:
        """إحصائيات نظام RAG"""
        try:
            stats = {
                'authors_count': await self.authors_collection.count_documents({}),
                'works_count': await self.works_collection.count_documents({}),
                'sources_count': await self.sources_collection.count_documents({}),
                'queries_count': await self.queries_collection.count_documents({}),
            }
            
            # إضافة إحصائيات التضمينات
            embeddings_stats = await self.embeddings_service.get_embeddings_stats()
            stats['embeddings'] = embeddings_stats
            
            # آخر الاستعلامات
            recent_queries_cursor = self.queries_collection.find().sort('timestamp', -1).limit(5)
            recent_queries = await recent_queries_cursor.to_list(5)
            stats['recent_queries'] = [q.get('query_text', '') for q in recent_queries]
            
            return stats
            
        except Exception as e:
            logger.error(f"خطأ في إحصائيات RAG: {e}")
            return {'error': str(e)}

# سيتم تهيئته في الخادم الرئيسي
rag_service = None