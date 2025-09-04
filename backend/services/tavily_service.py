import os
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
import logging
from dotenv import load_dotenv
import asyncio

load_dotenv()

logger = logging.getLogger(__name__)

class TavilyAdvancedSearchService:
    """خدمة البحث المتقدمة باستخدام Tavily للأدب العُماني"""
    
    def __init__(self):
        self.api_key = os.environ.get('TAVILY_API_KEY')
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        self.client = TavilyClient(api_key=self.api_key)
        
        # مجالات البحث المتخصصة للأدب العُماني
        self.search_domains = {
            'academic': [
                'jstor.org', 'academia.edu', 'researchgate.net',
                'journals.omanstudies.om', 'omanliterature.org'
            ],
            'official': [
                'moe.gov.om', 'heritage.gov.om', 'oman.om', 
                'omanobserver.om', 'omandaily.om', 'shabiba.com'
            ],
            'cultural': [
                'culturaloman.org', 'omanculture.net', 
                'omanpoetry.org', 'omaniheritage.com'
            ]
        }
    
    async def search_omani_literature_advanced(
        self, 
        query: str, 
        max_results: int = 5,
        include_domains: List[str] = None
    ) -> Dict[str, Any]:
        """البحث المتقدم في المقابلات والمقالات الأدبية العُمانية المنشورة"""
        
        try:
            # تحسين استعلام البحث للمقابلات والمقالات
            enhanced_query = self._enhance_query_for_omani_literature(query)
            
            # بحث مخصص للمحتوى الصحفي والأكاديمي المنشور
            search_response = self.client.search(
                query=enhanced_query,
                search_depth="advanced",  # بحث عميق
                max_results=max_results * 2,  # ضاعف النتائج للتصفية
                include_answer=True,
                include_domains=include_domains or self._get_journalism_domains(),
                exclude_domains=["facebook.com", "twitter.com", "instagram.com"],  # تجنب وسائل التواصل
                include_raw_content=True,
                max_tokens=8000  # محتوى أطول للمقالات
            )
            
            # تصفية وترتيب النتائج للتركيز على المحتوى الصحفي
            filtered_results = self._filter_for_journalism_content(search_response, query)
            
            return {
                'query': query,
                'enhanced_query': enhanced_query,
                'results': filtered_results,
                'total_found': len(filtered_results),
                'search_engine': 'tavily_journalism_focused',
                'answer_summary': search_response.get('answer', ''),
                'search_type': 'articles_and_interviews'
            }
            
        except Exception as e:
            logger.error(f"خطأ في بحث Tavily المحسن: {e}")
            return {
                'query': query,
                'results': [],
                'total_found': 0,
                'error': str(e),
                'search_engine': 'tavily_journalism_error'
            }
    
    def _enhance_query_for_omani_literature(self, query: str) -> str:
        """تحسين استعلام البحث للتركيز على المقابلات والمقالات المنشورة"""
        
        # إضافة كلمات مفتاحية لإيجاد المقابلات والمقالات
        interview_terms = [
            "مقابلة مع", "حوار مع", "لقاء مع", "interview with",
            "مقال عن", "تقرير عن", "دراسة عن", "article about",
            "صحيفة", "مجلة", "موقع أدبي", "منشور"
        ]
        
        # مواقع موثوقة تنشر مقابلات ومقالات أدبية
        reliable_sources = [
            "site:omanobserver.om", "site:omandaily.om", "site:shabiba.com",
            "site:alwatan.com", "site:omanalaan.com", "site:omansultanate.com",
            "site:moe.gov.om", "site:heritage.gov.om",
            "interview OR مقابلة OR حوار OR لقاء",
            "article OR مقال OR تقرير OR دراسة"
        ]
        
        # تنظيف الاستعلام من الكلمات غير المفيدة
        stop_words = ['أريد', 'أعطني', 'قل لي', 'أخبرني عن']
        cleaned_query = query
        for word in stop_words:
            cleaned_query = cleaned_query.replace(word, '')
        
        # بناء استعلام محسن يركز على المحتوى المنشور
        enhanced = f'{cleaned_query} الأدب العُماني ("مقابلة" OR "حوار" OR "مقال" OR "interview" OR "article")'
        
        # إضافة مصطلحات للحصول على مصادر صحفية وأكاديمية موثوقة
        enhanced += f' ({" OR ".join(reliable_sources[:5])})'
        
        logger.info(f"استعلام Tavily محسن: {enhanced}")
        
        return enhanced.strip()
    
    def _get_priority_domains(self) -> List[str]:
        """الحصول على النطاقات ذات الأولوية للبحث"""
        priority_domains = []
        
        # جمع أهم النطاقات من جميع الفئات
        for category, domains in self.search_domains.items():
            priority_domains.extend(domains[:2])  # أول نطاقين من كل فئة
        
        # إضافة نطاقات أكاديمية عامة
        priority_domains.extend([
            'wikipedia.org', 'britannica.com', 'scholar.google.com'
        ])
        
        return priority_domains
    
    def _get_journalism_domains(self) -> List[str]:
        """الحصول على النطاقات المتخصصة في الصحافة والمقالات الأدبية"""
        journalism_domains = []
        
        # مواقع صحفية عُمانية موثوقة
        journalism_domains.extend([
            'omanobserver.om', 'omandaily.om', 'shabiba.com',
            'alwatan.com', 'omanalaan.com', 'omansultanate.com',
            'timesofoman.com', 'muscatdaily.com'
        ])
        
        # مواقع حكومية ثقافية
        journalism_domains.extend([
            'moe.gov.om', 'heritage.gov.om', 'oman.om'
        ])
        
        # مواقع أكاديمية ومجلات أدبية
        journalism_domains.extend([
            'jstor.org', 'academia.edu', 'researchgate.net',
            'journals.omanstudies.om', 'omanliterature.org'
        ])
        
        return journalism_domains
    
    def _process_tavily_results(
        self, 
        search_response: Dict[str, Any], 
        original_query: str
    ) -> List[Dict[str, Any]]:
        """معالجة وتصفية نتائج Tavily"""
        
        raw_results = search_response.get('results', [])
        processed_results = []
        
        for result in raw_results:
            # تقييم صلة النتيجة بالأدب العُماني
            relevance_score = self._calculate_relevance_score(result, original_query)
            
            if relevance_score > 0.3:  # عتبة الصلة
                processed_result = {
                    'title': result.get('title', ''),
                    'content': result.get('content', '')[:600],  # أول 600 حرف
                    'url': result.get('url', ''),
                    'score': result.get('score', 0),
                    'relevance_score': relevance_score,
                    'source_type': self._identify_source_type(result.get('url', '')),
                    'reliability_rating': self._rate_source_reliability(result.get('url', '')),
                    'published_date': result.get('published_date'),
                    'raw_content': result.get('raw_content', '')[:200]  # محتوى خام قصير
                }
                
                # إضافة تحليل المحتوى للكلمات المفتاحية
                processed_result['omani_keywords'] = self._extract_omani_keywords(
                    processed_result['content']
                )
                
                processed_results.append(processed_result)
        
        # ترتيب النتائج حسب الصلة والموثوقية
        processed_results.sort(
            key=lambda x: (x['relevance_score'], x['reliability_rating']), 
            reverse=True
        )
        
        return processed_results
    
    def _calculate_relevance_score(self, result: Dict[str, Any], query: str) -> float:
        """حساب درجة صلة النتيجة بالاستعلام والأدب العُماني"""
        
        content = (result.get('content', '') + ' ' + result.get('title', '')).lower()
        query_lower = query.lower()
        
        score = 0.0
        
        # نقاط للكلمات المفتاحية العُمانية
        omani_keywords = ['عُمان', 'عُماني', 'oman', 'omani', 'سلطنة']
        for keyword in omani_keywords:
            if keyword.lower() in content:
                score += 0.3
        
        # نقاط للمصطلحات الأدبية
        literary_terms = ['أدب', 'شعر', 'رواية', 'قصة', 'شاعر', 'literature', 'poetry']
        for term in literary_terms:
            if term.lower() in content:
                score += 0.2
        
        # نقاط لتطابق كلمات الاستعلام
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 2 and word in content:
                score += 0.1
        
        return min(1.0, score)  # حد أقصى 1.0
    
    def _identify_source_type(self, url: str) -> str:
        """تحديد نوع المصدر من الرابط"""
        url_lower = url.lower()
        
        if '.edu' in url_lower or 'academic' in url_lower or 'journal' in url_lower:
            return 'أكاديمي'
        elif '.gov.om' in url_lower or 'official' in url_lower:
            return 'حكومي رسمي'
        elif 'wikipedia' in url_lower:
            return 'موسوعي'
        elif 'news' in url_lower or 'observer' in url_lower:
            return 'صحفي'
        else:
            return 'عام'
    
    def _rate_source_reliability(self, url: str) -> float:
        """تقييم موثوقية المصدر"""
        url_lower = url.lower()
        
        # مصادر عالية الموثوقية
        if any(domain in url_lower for domain in ['.edu', '.gov.om', 'jstor', 'academia.edu']):
            return 0.9
        
        # مصادر متوسطة الموثوقية
        elif any(domain in url_lower for domain in ['wikipedia', 'britannica', 'observer']):
            return 0.7
        
        # مصادر منخفضة الموثوقية
        else:
            return 0.5
    
    def _extract_omani_keywords(self, content: str) -> List[str]:
        """استخراج الكلمات المفتاحية العُمانية من المحتوى"""
        
        omani_specific_terms = [
            'عُمان', 'عُماني', 'عُمانية', 'مسقط', 'صلالة', 'نزوى', 'صحار',
            'الباطنة', 'ظفار', 'الداخلية', 'مسندم', 'الوسطى',
            'سلطنة', 'سلطان', 'قابوس', 'هيثم', 'آل سعيد',
            'خنجر', 'عنزة', 'هجن', 'نخيل', 'لبان', 'بخور',
            'فرقة', 'رزحة', 'برعة', 'فن', 'تراث'
        ]
        
        found_keywords = []
        content_lower = content.lower()
        
        for term in omani_specific_terms:
            if term.lower() in content_lower:
                found_keywords.append(term)
        
        return found_keywords
    
    async def search_specific_author(self, author_name: str) -> Dict[str, Any]:
        """بحث متخصص عن مؤلف عُماني معين"""
        
        # استعلام مخصص للمؤلفين
        author_query = f'"{author_name}" شاعر عُماني OR "{author_name}" أديب عُماني OR "{author_name}" Omani poet OR "{author_name}" Omani writer'
        
        return await self.search_omani_literature_advanced(
            query=author_query,
            max_results=7,
            include_domains=self.search_domains['academic'] + self.search_domains['official']
        )
    
    async def search_literary_work(self, work_title: str, author: str = "") -> Dict[str, Any]:
        """بحث متخصص عن عمل أدبي معين"""
        
        work_query = f'"{work_title}" {author} الأدب العُماني'
        if author:
            work_query += f' "{author}"'
        
        work_query += ' رواية OR قصيدة OR ديوان OR مسرحية OR قصة'
        
        return await self.search_omani_literature_advanced(
            query=work_query,
            max_results=5
        )
    
    def format_results_for_llm(self, search_results: Dict[str, Any]) -> str:
        """تنسيق نتائج البحث للذكاء الاصطناعي"""
        
        if not search_results.get('results'):
            return "لم يتم العثور على نتائج موثوقة."
        
        formatted = f"نتائج البحث المتقدم لـ: {search_results['query']}\n\n"
        
        # إضافة الملخص إذا كان متوفراً
        if search_results.get('answer_summary'):
            formatted += f"الملخص: {search_results['answer_summary']}\n\n"
        
        # إضافة النتائج مع تقييم الموثوقية
        for i, result in enumerate(search_results['results'], 1):
            reliability_emoji = "🏆" if result['reliability_rating'] > 0.8 else "✅" if result['reliability_rating'] > 0.6 else "⚠️"
            
            formatted += f"{i}. {result['title']} {reliability_emoji}\n"
            formatted += f"النوع: {result['source_type']} | الموثوقية: {result['reliability_rating']:.1f}/1.0\n"
            formatted += f"المحتوى: {result['content'][:300]}...\n"
            
            if result['omani_keywords']:
                formatted += f"كلمات مفتاحية عُمانية: {', '.join(result['omani_keywords'][:5])}\n"
            
            formatted += f"المصدر: {result['url']}\n\n"
        
        formatted += f"إجمالي النتائج: {search_results['total_found']} | محرك البحث: Tavily Advanced"
        
        return formatted

# إنشاء مثيل خدمة Tavily
tavily_search_service = TavilyAdvancedSearchService()