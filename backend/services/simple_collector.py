from typing import Dict, Any, List
import logging
from datetime import datetime
from services.tavily_service import tavily_search_service

logger = logging.getLogger(__name__)

class SimpleSourceCollector:
    """جامع مصادر بسيط وعملي للأدب العُماني"""
    
    def __init__(self):
        # قائمة الكتاب والشعراء العُمانيين المعروفين
        self.known_authors = [
            'سيف الرحبي', 'جوخة الحارثي', 'هدى حمد', 'عبدالله الريامي',
            'سعيد الصقلاوي', 'محمد الحارثي', 'بدرية الشحي', 'عبدالله الطائي',
            'زاهر الغافري', 'سالم الراشدي', 'أحمد بلال', 'فاطمة الشيدي'
        ]
    
    async def collect_sources_for_author(self, author_name: str) -> Dict[str, Any]:
        """جمع مصادر لمؤلف واحد"""
        
        try:
            # البحث عن مقابلات
            interviews = await self._find_interviews(author_name)
            
            # البحث عن مقالات أكاديمية
            articles = await self._find_articles(author_name)
            
            # البحث عن معلومات الكتب
            books_info = await self._find_books_info(author_name)
            
            return {
                'author': author_name,
                'interviews': interviews,
                'articles': articles,
                'books_info': books_info,
                'total_sources': len(interviews) + len(articles) + len(books_info),
                'collection_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في جمع مصادر {author_name}: {e}")
            return {
                'author': author_name,
                'interviews': [],
                'articles': [],
                'books_info': [],
                'total_sources': 0,
                'error': str(e)
            }
    
    async def _find_interviews(self, author_name: str) -> List[Dict[str, Any]]:
        """البحث عن مقابلات"""
        try:
            query = f'مقابلة مع "{author_name}" OR حوار مع "{author_name}" الأدب العُماني'
            results = await tavily_search_service.search_omani_literature_advanced(query, max_results=3)
            
            interviews = []
            for result in results.get('results', []):
                if any(keyword in result.get('content', '').lower() 
                       for keyword in ['مقابلة', 'حوار', 'لقاء', 'interview']):
                    interviews.append({
                        'title': result.get('title', ''),
                        'content': result.get('content', '')[:600],
                        'url': result.get('url', ''),
                        'source_type': 'interview',
                        'reliability': result.get('reliability_rating', 0.7)
                    })
            
            return interviews
            
        except Exception as e:
            logger.error(f"خطأ في البحث عن مقابلات {author_name}: {e}")
            return []
    
    async def _find_articles(self, author_name: str) -> List[Dict[str, Any]]:
        """البحث عن مقالات أكاديمية"""
        try:
            query = f'"{author_name}" الأدب العُماني مقال أكاديمي OR academic article'
            results = await tavily_search_service.search_omani_literature_advanced(query, max_results=3)
            
            articles = []
            for result in results.get('results', []):
                if any(keyword in result.get('content', '').lower() 
                       for keyword in ['مقال', 'دراسة', 'article', 'academic', 'journal']):
                    articles.append({
                        'title': result.get('title', ''),
                        'content': result.get('content', '')[:600],
                        'url': result.get('url', ''),
                        'source_type': 'academic_article',
                        'reliability': result.get('reliability_rating', 0.8)
                    })
            
            return articles
            
        except Exception as e:
            logger.error(f"خطأ في البحث عن مقالات {author_name}: {e}")
            return []
    
    async def _find_books_info(self, author_name: str) -> List[Dict[str, Any]]:
        """البحث عن معلومات الكتب والدواوين"""
        try:
            query = f'كتب "{author_name}" OR مؤلفات "{author_name}" OR دواوين "{author_name}" الأدب العُماني'
            results = await tavily_search_service.search_omani_literature_advanced(query, max_results=3)
            
            books = []
            for result in results.get('results', []):
                if any(keyword in result.get('content', '').lower() 
                       for keyword in ['كتاب', 'ديوان', 'رواية', 'مؤلف', 'book', 'published']):
                    books.append({
                        'title': result.get('title', ''),
                        'content': result.get('content', '')[:600],
                        'url': result.get('url', ''),
                        'source_type': 'book_info',
                        'reliability': result.get('reliability_rating', 0.6)
                    })
            
            return books
            
        except Exception as e:
            logger.error(f"خطأ في البحث عن كتب {author_name}: {e}")
            return []
    
    async def bulk_collect_all_authors(self) -> Dict[str, Any]:
        """جمع شامل لجميع المؤلفين المعروفين"""
        
        collection_summary = {
            'authors_processed': 0,
            'total_sources_found': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'detailed_results': [],
            'start_time': datetime.utcnow().isoformat()
        }
        
        try:
            for author in self.known_authors[:6]:  # أول 6 للاختبار
                logger.info(f"جمع مصادر للمؤلف: {author}")
                
                author_results = await self.collect_sources_for_author(author)
                collection_summary['detailed_results'].append(author_results)
                collection_summary['authors_processed'] += 1
                
                if author_results.get('total_sources', 0) > 0:
                    collection_summary['successful_collections'] += 1
                    collection_summary['total_sources_found'] += author_results['total_sources']
                else:
                    collection_summary['failed_collections'] += 1
                
                # تأخير بين الطلبات
                await __import__('asyncio').sleep(3)
            
            collection_summary['completion_time'] = datetime.utcnow().isoformat()
            collection_summary['collection_completed'] = True
            
            logger.info(f"اكتمل الجمع: {collection_summary['total_sources_found']} مصدر من {collection_summary['authors_processed']} مؤلف")
            
        except Exception as e:
            logger.error(f"خطأ في الجمع الشامل: {e}")
            collection_summary['collection_completed'] = False
            collection_summary['error'] = str(e)
        
        return collection_summary

# إنشاء مثيل واحد
simple_collector = SimpleSourceCollector()