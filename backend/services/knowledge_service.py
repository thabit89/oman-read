from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
import logging
from datetime import datetime
import hashlib
import re

logger = logging.getLogger(__name__)

class OmaniLiteratureKnowledgeBase:
    """قاعدة المعرفة للأدب العُماني - للتعلم من المصادر المضافة"""
    
    def __init__(self, db):
        self.db = db
        self.knowledge_collection: AsyncIOMotorCollection = db.omani_literature_knowledge
        self.sources_collection: AsyncIOMotorCollection = db.omani_sources
        
    async def add_literature_source(
        self, 
        title: str,
        content: str,
        source_type: str,  # book, article, poem, biography, etc.
        author: Optional[str] = None,
        publication_date: Optional[str] = None,
        reliability_score: float = 0.8,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """إضافة مصدر أدبي جديد لقاعدة المعرفة"""
        
        try:
            # إنشاء معرف فريد للمحتوى
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # تحليل المحتوى واستخراج الكلمات المفتاحية
            keywords = self._extract_keywords(content)
            entities = self._extract_entities(content)
            
            source_data = {
                '_id': content_hash,
                'title': title,
                'content': content,
                'source_type': source_type,
                'author': author,
                'publication_date': publication_date,
                'reliability_score': reliability_score,
                'tags': tags or [],
                'keywords': keywords,
                'entities': entities,
                'added_date': datetime.utcnow(),
                'processed': False,
                'word_count': len(content.split()),
                'language': 'arabic'
            }
            
            # حفظ في قاعدة البيانات
            await self.sources_collection.update_one(
                {'_id': content_hash},
                {'$set': source_data},
                upsert=True
            )
            
            # معالجة المحتوى وإضافته لقاعدة المعرفة
            knowledge_entries = await self._process_content_to_knowledge(source_data)
            
            for entry in knowledge_entries:
                await self.knowledge_collection.update_one(
                    {'topic': entry['topic'], 'subtopic': entry['subtopic']},
                    {'$set': entry},
                    upsert=True
                )
            
            logger.info(f"تم إضافة مصدر جديد: {title} مع {len(knowledge_entries)} إدخال معرفي")
            
            return {
                'success': True,
                'source_id': content_hash,
                'knowledge_entries': len(knowledge_entries),
                'message': f'تم إضافة "{title}" بنجاح إلى قاعدة المعرفة'
            }
            
        except Exception as e:
            logger.error(f"خطأ في إضافة المصدر: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'فشل في إضافة المصدر'
            }
    
    def _extract_keywords(self, content: str) -> List[str]:
        """استخراج الكلمات المفتاحية من المحتوى"""
        # كلمات مفتاحية متعلقة بالأدب العُماني
        literature_keywords = [
            'شعر', 'شاعر', 'قصيدة', 'ديوان', 'رواية', 'روائي', 'قصة', 'مسرحية',
            'نثر', 'أدب', 'أديب', 'كاتب', 'مؤلف', 'تأليف', 'نشر', 'طباعة',
            'نقد', 'نقدي', 'تحليل', 'دراسة', 'بحث', 'مقال',
            'عُمان', 'عُماني', 'عُمانية', 'سلطنة', 'مسقط', 'صحار', 'نزوى',
            'تراث', 'تراثي', 'شعبي', 'فولكلور', 'حكايات', 'أمثال',
            'بحر', 'عروض', 'قافية', 'وزن', 'إيقاع', 'نبر'
        ]
        
        found_keywords = []
        content_lower = content.lower()
        
        for keyword in literature_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)
        
        # إضافة أسماء الأعلام (تحديد بسيط)
        names = re.findall(r'[أ-ي]+\s+[أ-ي]+', content)
        found_keywords.extend(names[:10])  # أول 10 أسماء
        
        return list(set(found_keywords))
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """استخراج الكيانات المسماة من المحتوى"""
        entities = {
            'authors': [],
            'books': [],
            'places': [],
            'dates': []
        }
        
        # استخراج التواريخ البسيط
        date_patterns = [
            r'\d{4}م',  # سنوات هجرية
            r'\d{4}هـ',  # سنوات ميلادية
            r'عام \d{4}',
            r'سنة \d{4}'
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, content)
            entities['dates'].extend(dates)
        
        # استخراج أسماء الأماكن العُمانية
        omani_places = [
            'مسقط', 'صحار', 'نزوى', 'صلالة', 'مطرح', 'الباطنة', 'ظفار',
            'الداخلية', 'الظاهرة', 'مسندم', 'الوسطى', 'عبري', 'بهلاء',
            'جعلان', 'صور', 'رستاق', 'إبراء', 'بدبد'
        ]
        
        for place in omani_places:
            if place in content:
                entities['places'].append(place)
        
        return entities
    
    async def _process_content_to_knowledge(self, source_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """معالجة المحتوى وتحويله إلى مدخلات معرفية"""
        knowledge_entries = []
        
        # تقسيم المحتوى إلى فقرات
        paragraphs = source_data['content'].split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) < 50:  # تجاهل الفقرات القصيرة
                continue
            
            # تحديد الموضوع الرئيسي من الكلمات المفتاحية
            main_topic = self._identify_main_topic(paragraph, source_data['keywords'])
            
            knowledge_entry = {
                'topic': main_topic,
                'subtopic': f"{source_data['title']}_section_{i}",
                'content': paragraph.strip(),
                'source_title': source_data['title'],
                'source_author': source_data.get('author'),
                'source_type': source_data['source_type'],
                'reliability_score': source_data['reliability_score'],
                'tags': source_data['tags'],
                'last_updated': datetime.utcnow(),
                'usage_count': 0
            }
            
            knowledge_entries.append(knowledge_entry)
        
        return knowledge_entries
    
    def _identify_main_topic(self, text: str, keywords: List[str]) -> str:
        """تحديد الموضوع الرئيسي من النص"""
        
        # خريطة المواضيع
        topic_map = {
            'poetry': ['شعر', 'قصيدة', 'ديوان', 'بيت', 'أبيات', 'قافية', 'بحر'],
            'prose': ['رواية', 'قصة', 'نثر', 'مقال', 'كتاب'],
            'authors': ['شاعر', 'أديب', 'كاتب', 'روائي', 'مؤلف'],
            'criticism': ['نقد', 'تحليل', 'دراسة', 'تفسير', 'شرح'],
            'history': ['تاريخ', 'عصر', 'فترة', 'زمن', 'قديم', 'حديث'],
            'culture': ['تراث', 'ثقافة', 'تقليد', 'شعبي', 'فولكلور']
        }
        
        text_lower = text.lower()
        topic_scores = {}
        
        for topic, topic_keywords in topic_map.items():
            score = sum(1 for keyword in topic_keywords if keyword in text_lower)
            if score > 0:
                topic_scores[topic] = score
        
        # إرجاع الموضوع الأعلى نقاطاً أو "general" إذا لم يوجد
        return max(topic_scores, key=topic_scores.get) if topic_scores else 'general'
    
    async def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """البحث في قاعدة المعرفة"""
        try:
            # بحث نصي بسيط
            search_terms = query.lower().split()
            
            results = []
            async for entry in self.knowledge_collection.find():
                content_lower = entry['content'].lower()
                score = sum(1 for term in search_terms if term in content_lower)
                
                if score > 0:
                    entry['relevance_score'] = score
                    results.append(entry)
            
            # ترتيب حسب الصلة والموثوقية
            results.sort(key=lambda x: (x['relevance_score'], x['reliability_score']), reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"خطأ في البحث في قاعدة المعرفة: {e}")
            return []
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """إحصائيات قاعدة المعرفة"""
        try:
            total_sources = await self.sources_collection.count_documents({})
            total_knowledge = await self.knowledge_collection.count_documents({})
            
            # إحصائيات حسب النوع
            pipeline = [
                {'$group': {'_id': '$source_type', 'count': {'$sum': 1}}}
            ]
            
            type_stats = {}
            async for stat in self.sources_collection.aggregate(pipeline):
                type_stats[stat['_id']] = stat['count']
            
            return {
                'total_sources': total_sources,
                'total_knowledge_entries': total_knowledge,
                'sources_by_type': type_stats,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في جمع الإحصائيات: {e}")
            return {'error': str(e)}

# إنشاء مثيل قاعدة المعرفة - سيتم تهيئته في chat_service
omani_knowledge_base = None