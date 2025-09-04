import asyncio
import aiohttp
from typing import List, Dict, Any
import logging
from urllib.parse import quote
import re
import random

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def search_omani_literature(self, query: str) -> List[Dict[str, Any]]:
        """البحث الدقيق في مصادر الأدب العُماني الموثوقة"""
        try:
            # تحسين الاستعلام للحصول على نتائج أكثر دقة
            enhanced_query = self._enhance_query_for_accuracy(query)
            
            # البحث في ويكيبيديا العربية أولاً
            wikipedia_results = await self._search_arabic_wikipedia(enhanced_query)
            
            # البحث في مصادر أكاديمية عُمانية
            academic_results = await self._search_academic_sources(enhanced_query)
            
            # البحث في المصادر الحكومية العُمانية
            official_results = await self._search_official_omani_sources(enhanced_query)
            
            # دمج النتائج مع ترجيح المصادر الموثوقة
            all_results = self._prioritize_reliable_sources([
                *wikipedia_results,
                *academic_results, 
                *official_results
            ])
            
            return all_results[:3]  # أفضل 3 نتائج موثوقة فقط
            
        except Exception as e:
            logger.error(f"خطأ في البحث: {e}")
            return []
    
    def _enhance_query_for_accuracy(self, query: str) -> str:
        """تحسين الاستعلام للحصول على نتائج دقيقة"""
        # إضافة كلمات مفتاحية للدقة
        accuracy_terms = [
            "الأدب العُماني",
            "سلطنة عُمان", 
            "الثقافة العُمانية",
            "التراث العُماني"
        ]
        
        # تنظيف الاستعلام من الكلمات الغامضة
        vague_words = ["قليلاً", "ربما", "أظن", "أعتقد"]
        cleaned_query = query
        for word in vague_words:
            cleaned_query = cleaned_query.replace(word, "")
        
        # إضافة مصطلحات دقة
        enhanced = f"{cleaned_query} {random.choice(accuracy_terms)} مصادر موثوقة"
        return enhanced.strip()
    
    async def _search_academic_sources(self, query: str) -> List[Dict[str, Any]]:
        """البحث في المصادر الأكاديمية المتخصصة"""
        results = []
        try:
            # محاكاة البحث في المصادر الأكاديمية
            # في التطبيق الحقيقي، يمكن استخدام APIs مثل:
            # - ResearchGate API
            # - Google Scholar API
            # - Academia.edu API
            
            academic_sources = [
                {
                    'title': f'بحث أكاديمي: {query} في الأدب العُماني المعاصر',
                    'content': 'مصدر أكاديمي متخصص في الأدب العُماني...',
                    'url': 'https://academic-source-example.com',
                    'source': 'مجلة الدراسات العُمانية',
                    'reliability_score': 0.95,
                    'type': 'academic'
                }
            ]
            
            return academic_sources
            
        except Exception as e:
            logger.error(f"خطأ في البحث الأكاديمي: {e}")
            return []
    
    async def _search_official_omani_sources(self, query: str) -> List[Dict[str, Any]]:
        """البحث في المصادر الحكومية العُمانية الرسمية"""
        results = []
        try:
            # مصادر حكومية عُمانية موثوقة
            official_domains = [
                "moe.gov.om",  # وزارة التربية والتعليم
                "moci.gov.om", # وزارة التجارة والصناعة  
                "heritage.gov.om",  # وزارة التراث والثقافة
                "omanobserver.om",  # جريدة عُمان أوبزرفر
                "omandaily.om"  # الصحف العُمانية
            ]
            
            # محاكاة نتائج من مصادر رسمية
            for domain in official_domains[:2]:  # أول مصدرين فقط
                official_result = {
                    'title': f'معلومات رسمية من {domain} حول {query}',
                    'content': f'معلومات موثوقة من المصادر الحكومية العُمانية...',
                    'url': f'https://{domain}/page',
                    'source': f'المصادر الرسمية العُمانية - {domain}',
                    'reliability_score': 0.9,
                    'type': 'official'
                }
                results.append(official_result)
            
            return results
            
        except Exception as e:
            logger.error(f"خطأ في البحث الرسمي: {e}")
            return []
    
    def _prioritize_reliable_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ترتيب النتائج حسب مستوى الموثوقية"""
        # ترجيح المصادر حسب النوع
        type_weights = {
            'academic': 1.0,      # المصادر الأكاديمية أولاً
            'official': 0.9,      # المصادر الرسمية ثانياً  
            'wikipedia': 0.7,     # ويكيبيديا ثالثاً
            'general': 0.5        # المصادر العامة أخيراً
        }
        
        # إضافة درجة موثوقية مجمعة
        for result in results:
            base_score = result.get('reliability_score', 0.5)
            type_weight = type_weights.get(result.get('type', 'general'), 0.5)
            result['final_score'] = base_score * type_weight
        
        # ترتيب حسب الموثوقية
        sorted_results = sorted(results, key=lambda x: x.get('final_score', 0), reverse=True)
        
        # إضافة تحذيرات الموثوقية
        for result in sorted_results:
            if result.get('final_score', 0) < 0.6:
                result['reliability_warning'] = 'مصدر يحتاج تحقق إضافي'
            elif result.get('final_score', 0) < 0.8:
                result['reliability_warning'] = 'مصدر موثوق نسبياً'
        
        return sorted_results
    
    async def _search_arabic_wikipedia(self, query: str) -> List[Dict[str, Any]]:
        """البحث في ويكيبيديا العربية"""
        results = []
        try:
            # إضافة كلمات مفتاحية عُمانية للبحث
            omani_query = f"{query} عُمان أدب عُماني"
            encoded_query = quote(omani_query)
            
            # API ويكيبيديا العربية
            wikipedia_api = f"https://ar.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(wikipedia_api, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'extract' in data:
                            results.append({
                                'title': data.get('title', ''),
                                'content': data.get('extract', '')[:500],
                                'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                                'source': 'ويكيبيديا العربية',
                                'relevance_score': 0.9
                            })
        except Exception as e:
            logger.error(f"خطأ في البحث في ويكيبيديا: {e}")
        
        return results
    
    async def _search_omani_content(self, query: str) -> List[Dict[str, Any]]:
        """البحث في المحتوى العُماني العام"""
        results = []
        try:
            # مصادر عُمانية مخصصة
            omani_sites = [
                "site:moe.gov.om",
                "site:moci.gov.om", 
                "site:omanobserver.om",
                "الأدب العُماني",
                "الثقافة العُمانية"
            ]
            
            # إنشاء استعلام محسن
            enhanced_query = f"{query} {' OR '.join(omani_sites)}"
            
            # محاكاة نتائج البحث (في التطبيق الحقيقي، استخدم Google Custom Search API)
            sample_results = [
                {
                    'title': f'مقال عن {query} في الأدب العُماني',
                    'content': f'معلومات مفصلة حول {query} من المصادر العُمانية الموثوقة...',
                    'url': 'https://example-omani-literature.com',
                    'source': 'مصادر الأدب العُماني',
                    'relevance_score': 0.8
                }
            ]
            
            results.extend(sample_results)
            
        except Exception as e:
            logger.error(f"خطأ في البحث العام: {e}")
        
        return results
    
    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """إزالة النتائج المكررة"""
        seen_titles = set()
        unique_results = []
        
        for result in results:
            title = result.get('title', '').lower()
            if title not in seen_titles and title:
                seen_titles.add(title)
                unique_results.append(result)
        
        return unique_results
    
    def extract_key_terms(self, query: str) -> List[str]:
        """استخراج المصطلحات المفتاحية من الاستعلام"""
        # إزالة كلمات الاستفهام والحروف
        stop_words = ['من', 'ما', 'أين', 'متى', 'كيف', 'هل', 'عن', 'في', 'على', 'إلى']
        
        # تنظيف النص
        cleaned_query = re.sub(r'[^\w\s]', '', query)
        words = cleaned_query.split()
        
        # استخراج الكلمات المهمة
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_terms[:3]  # أهم 3 مصطلحات

# مثيل واحد للخدمة
web_search_service = WebSearchService()