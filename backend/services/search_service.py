import asyncio
import aiohttp
from typing import List, Dict, Any
import logging
from urllib.parse import quote
import re

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def search_omani_literature(self, query: str) -> List[Dict[str, Any]]:
        """البحث في مصادر الأدب العُماني"""
        try:
            # البحث في ويكيبيديا العربية أولاً
            wikipedia_results = await self._search_arabic_wikipedia(query)
            
            # البحث العام عن الأدب العُماني
            general_results = await self._search_omani_content(query)
            
            # دمج النتائج وإزالة التكرار
            all_results = wikipedia_results + general_results
            unique_results = self._remove_duplicates(all_results)
            
            return unique_results[:5]  # أفضل 5 نتائج
            
        except Exception as e:
            logger.error(f"خطأ في البحث: {e}")
            return []
    
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