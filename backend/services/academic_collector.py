import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
import logging
from bs4 import BeautifulSoup
from newspaper import Article
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re

from services.tavily_service import tavily_search_service

logger = logging.getLogger(__name__)

class AcademicSourceCollector:
    """جامع المصادر الأكاديمية للأدب العُماني"""
    
    def __init__(self):
        # مصادر أكاديمية موثوقة للأدب العُماني
        self.academic_sites = {
            'universities': [
                'https://www.squ.edu.om',  # جامعة السلطان قابوس
                'https://www.unizwa.edu.om',  # جامعة نزوى
                'https://www.uod.edu.om',  # جامعة ظفار
                'https://www.asu.edu.om',  # الجامعة العربية المفتوحة
            ],
            'cultural_centers': [
                'https://www.moe.gov.om',  # وزارة التربية والتعليم
                'https://heritage.gov.om',  # وزارة التراث والثقافة
                'https://www.oman.om',  # البوابة الرسمية
            ],
            'journals': [
                'jstor.org', 'academia.edu', 'researchgate.net',
                'journals.sagepub.com', 'tandfonline.com'
            ]
        }
        
        # قائمة الكتاب والشعراء العُمانيين المعروفين للبحث عنهم
        self.known_omani_authors = [
            'سيف الرحبي', 'جوخة الحارثي', 'هدى حمد', 'عبدالله الريامي',
            'سعيد الصقلاوي', 'محمد الحارثي', 'بدرية الشحي', 'سالم الراشدي',
            'أحمد بلال', 'يحيى منصور', 'حسين العبري', 'فاطمة الشيدي',
            'عبدالله الطائي', 'زاهر الغافري', 'خالد البلوشي'
        ]
    
    async def collect_comprehensive_sources(self) -> Dict[str, Any]:
        """جمع شامل للمصادر الأكاديمية"""
        
        collection_results = {
            'academic_papers': [],
            'interviews': [],
            'articles': [],
            'books_metadata': [],
            'total_collected': 0,
            'collection_date': datetime.utcnow().isoformat()
        }
        
        try:
            # جمع الأبحاث الأكاديمية
            academic_results = await self._collect_academic_papers()
            collection_results['academic_papers'] = academic_results
            
            # جمع المقابلات والحوارات
            interviews_results = await self._collect_interviews()
            collection_results['interviews'] = interviews_results
            
            # جمع المقالات من المجلات الأدبية
            articles_results = await self._collect_literary_articles()
            collection_results['articles'] = articles_results
            
            # جمع معلومات الكتب والدواوين
            books_results = await self._collect_books_metadata()
            collection_results['books_metadata'] = books_results
            
            collection_results['total_collected'] = (
                len(academic_results) + len(interviews_results) + 
                len(articles_results) + len(books_results)
            )
            
            logger.info(f"تم جمع {collection_results['total_collected']} مصدر أكاديمي")
            
            return collection_results
            
        except Exception as e:
            logger.error(f"خطأ في جمع المصادر: {e}")
            return collection_results
    
    async def _collect_academic_papers(self) -> List[Dict[str, Any]]:
        """جمع الأبحاث الأكاديمية عن الأدب العُماني"""
        academic_papers = []
        
        try:
            # البحث في كل مؤلف معروف
            for author in self.known_omani_authors[:5]:  # أول 5 للاختبار
                search_query = f'"{author}" الأدب العُماني academic research site:edu OR site:jstor.org'
                
                # استخدام Tavily للبحث الأكاديمي
                results = await tavily_search_service.search_omani_literature_advanced(
                    query=search_query,
                    max_results=3,
                    include_domains=self.academic_sites['journals'] + 
                                  [site.replace('https://', '').replace('http://', '') 
                                   for site in self.academic_sites['universities']]
                )
                
                for result in results.get('results', []):
                    if self._is_academic_content(result):
                        academic_paper = {
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'abstract': result.get('content', '')[:500],
                            'covered_author': author,
                            'source_type': 'academic_paper',
                            'reliability_score': result.get('reliability_rating', 0.8),
                            'collection_date': datetime.utcnow().isoformat(),
                            'metadata': {
                                'search_query': search_query,
                                'tavily_score': result.get('score', 0)
                            }
                        }
                        academic_papers.append(academic_paper)
                
                # تأخير للتجنب Rate limiting
                await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"خطأ في جمع الأبحاث الأكاديمية: {e}")
        
        return academic_papers[:20]  # أول 20 بحث
    
    async def _collect_interviews(self) -> List[Dict[str, Any]]:
        """جمع المقابلات والحوارات مع الأدباء العُمانيين"""
        interviews = []
        
        try:
            # البحث عن مقابلات مع كل مؤلف
            for author in self.known_omani_authors[:5]:
                interview_query = f'مقابلة مع "{author}" OR حوار مع "{author}" OR لقاء مع "{author}" site:omanobserver.om OR site:shabiba.com'
                
                results = await tavily_search_service.search_omani_literature_advanced(
                    query=interview_query,
                    max_results=2
                )
                
                for result in results.get('results', []):
                    if self._is_interview_content(result):
                        interview = {
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'content': result.get('content', ''),
                            'interviewee': author,
                            'source_type': 'interview',
                            'publication_date': result.get('published_date'),
                            'reliability_score': result.get('reliability_rating', 0.7),
                            'collection_date': datetime.utcnow().isoformat()
                        }
                        interviews.append(interview)
                
                await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"خطأ في جمع المقابلات: {e}")
        
        return interviews
    
    async def _collect_literary_articles(self) -> List[Dict[str, Any]]:
        """جمع المقالات من المجلات الأدبية العربية"""
        articles = []
        
        try:
            # مواضيع أدبية عُمانية للبحث عنها
            literary_topics = [
                'الشعر العُماني المعاصر',
                'الرواية في الأدب العُماني',
                'النقد الأدبي العُماني',
                'التراث الثقافي العُماني'
            ]
            
            for topic in literary_topics:
                article_query = f'"{topic}" مقال OR article مجلة أدبية OR literary journal'
                
                results = await tavily_search_service.search_omani_literature_advanced(
                    query=article_query,
                    max_results=3
                )
                
                for result in results.get('results', []):
                    if self._is_literary_article(result):
                        article = {
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'content': result.get('content', ''),
                            'topic': topic,
                            'source_type': 'literary_article',
                            'reliability_score': result.get('reliability_rating', 0.6),
                            'collection_date': datetime.utcnow().isoformat()
                        }
                        articles.append(article)
                
                await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"خطأ في جمع المقالات: {e}")
        
        return articles
    
    async def _collect_books_metadata(self) -> List[Dict[str, Any]]:
        """جمع معلومات الكتب والدواوين العُمانية"""
        books = []
        
        try:
            # البحث عن كتب ودواوين محددة
            book_queries = [
                'دواوين شعراء عُمان',
                'روايات عُمانية منشورة', 
                'كتب الأدب العُماني',
                'مؤلفات الكتاب العُمانيين'
            ]
            
            for query in book_queries:
                search_query = f'"{query}" كتاب OR book ديوان OR collection'
                
                results = await tavily_search_service.search_omani_literature_advanced(
                    query=search_query,
                    max_results=4
                )
                
                for result in results.get('results', []):
                    if self._is_book_metadata(result):
                        book = {
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'description': result.get('content', ''),
                            'search_category': query,
                            'source_type': 'book_metadata',
                            'reliability_score': result.get('reliability_rating', 0.5),
                            'collection_date': datetime.utcnow().isoformat()
                        }
                        books.append(book)
                
                await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"خطأ في جمع معلومات الكتب: {e}")
        
        return books
    
    def _is_academic_content(self, result: Dict[str, Any]) -> bool:
        """فحص إذا كان المحتوى أكاديمياً"""
        content = result.get('content', '').lower()
        title = result.get('title', '').lower()
        url = result.get('url', '').lower()
        
        academic_indicators = [
            'abstract', 'university', 'research', 'journal', 'academic',
            'مستخلص', 'جامعة', 'بحث', 'مجلة', 'دراسة', 'أكاديمي'
        ]
        
        return any(indicator in content + title + url for indicator in academic_indicators)
    
    def _is_interview_content(self, result: Dict[str, Any]) -> bool:
        """فحص إذا كان المحتوى مقابلة"""
        content = result.get('content', '').lower()
        title = result.get('title', '').lower()
        
        interview_indicators = [
            'مقابلة', 'حوار', 'لقاء', 'interview', 'حديث مع', 'في حوار',
            'يقول', 'أجاب', 'سأل', 'استضاف'
        ]
        
        return any(indicator in content + title for indicator in interview_indicators)
    
    def _is_literary_article(self, result: Dict[str, Any]) -> bool:
        """فحص إذا كان المحتوى مقالاً أدبياً"""
        content = result.get('content', '').lower()
        title = result.get('title', '').lower()
        
        article_indicators = [
            'مقال', 'article', 'دراسة أدبية', 'تحليل أدبي', 'نقد',
            'criticism', 'literary analysis', 'أدب', 'literature'
        ]
        
        return any(indicator in content + title for indicator in article_indicators)
    
    def _is_book_metadata(self, result: Dict[str, Any]) -> bool:
        """فحص إذا كان المحتوى معلومات كتاب"""
        content = result.get('content', '').lower()
        title = result.get('title', '').lower()
        
        book_indicators = [
            'كتاب', 'ديوان', 'مؤلف', 'رواية', 'مجموعة',
            'book', 'published', 'author', 'novel', 'collection',
            'نشر', 'طبع', 'إصدار', 'publication'
        ]
        
        return any(indicator in content + title for indicator in book_indicators)

# إنشاء مثيل جامع المصادر الأكاديمية
academic_collector = AcademicSourceCollector()