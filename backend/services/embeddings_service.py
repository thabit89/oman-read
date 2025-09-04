import os
from typing import List, Dict, Any, Optional, Tuple
import openai
import numpy as np
from motor.motor_asyncio import AsyncIOMotorCollection
import logging
from datetime import datetime
import json
from sklearn.metrics.pairwise import cosine_similarity

from models.literature_models import EmbeddingRecord, Author, LiteraryWork, AcademicSource

logger = logging.getLogger(__name__)

class EmbeddingsService:
    """خدمة التضمين المتجه للأدب العُماني باستخدام OpenAI"""
    
    def __init__(self, db):
        self.db = db
        self.embeddings_collection: AsyncIOMotorCollection = db.embeddings
        self.authors_collection: AsyncIOMotorCollection = db.authors
        self.works_collection: AsyncIOMotorCollection = db.literary_works
        self.sources_collection: AsyncIOMotorCollection = db.academic_sources
        
        # إعداد OpenAI
        self.openai_api_key = os.environ.get('EMERGENT_LLM_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # نموذج التضمين المتقدم
        self.embedding_model = "text-embedding-3-large"
        self.embedding_dimensions = 3072  # أبعاد النموذج الكبير
    
    async def create_author_embedding(self, author: Author) -> Optional[str]:
        """إنشاء تضمين متجه لمؤلف"""
        try:
            # تجميع النص الخاص بالمؤلف
            author_text = f"""
            الاسم: {author.full_name}
            السيرة: {author.biography}
            الأنواع الأدبية: {', '.join([genre.value for genre in author.main_genres])}
            التأثيرات: {', '.join(author.influences)}
            الفترات الأدبية: {', '.join(author.literary_periods)}
            """
            
            # إنشاء التضمين
            embedding_vector = await self._generate_embedding(author_text)
            
            if embedding_vector:
                # حفظ في قاعدة البيانات
                embedding_record = EmbeddingRecord(
                    content_id=author.id,
                    content_type="author",
                    text_content=author_text.strip(),
                    embedding_vector=embedding_vector,
                    metadata={
                        'author_name': author.full_name,
                        'main_genres': [genre.value for genre in author.main_genres]
                    }
                )
                
                await self.embeddings_collection.insert_one(embedding_record.dict())
                
                # تحديث معرف التضمين في سجل المؤلف
                await self.authors_collection.update_one(
                    {'id': author.id},
                    {'$set': {'embedding_id': embedding_record.id}}
                )
                
                logger.info(f"تم إنشاء تضمين للمؤلف: {author.full_name}")
                return embedding_record.id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء تضمين المؤلف: {e}")
        
        return None
    
    async def create_work_embedding(self, work: LiteraryWork) -> Optional[str]:
        """إنشاء تضمين متجه لعمل أدبي"""
        try:
            # تجميع النص الخاص بالعمل
            work_text = f"""
            العنوان: {work.title}
            الفئة: {work.category.value}
            الأسلوب: {work.style.value}
            الموضوع الرئيسي: {work.main_theme}
            الملخص: {work.summary}
            المواضيع: {', '.join(work.themes)}
            النص الكامل: {work.text_content[:2000] if work.text_content else 'غير متوفر'}
            """
            
            embedding_vector = await self._generate_embedding(work_text)
            
            if embedding_vector:
                embedding_record = EmbeddingRecord(
                    content_id=work.id,
                    content_type="literary_work",
                    text_content=work_text.strip(),
                    embedding_vector=embedding_vector,
                    metadata={
                        'work_title': work.title,
                        'category': work.category.value,
                        'style': work.style.value,
                        'themes': work.themes
                    }
                )
                
                await self.embeddings_collection.insert_one(embedding_record.dict())
                
                await self.works_collection.update_one(
                    {'id': work.id},
                    {'$set': {'embedding_id': embedding_record.id}}
                )
                
                logger.info(f"تم إنشاء تضمين للعمل: {work.title}")
                return embedding_record.id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء تضمين العمل: {e}")
        
        return None
    
    async def semantic_search(
        self, 
        query: str, 
        content_types: List[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """البحث الدلالي في المحتوى باستخدام التضمين المتجه"""
        
        try:
            # إنشاء تضمين لاستعلام البحث
            query_embedding = await self._generate_embedding(query)
            if not query_embedding:
                return []
            
            # جلب جميع التضمينات
            filter_criteria = {}
            if content_types:
                filter_criteria['content_type'] = {'$in': content_types}
            
            embeddings_cursor = self.embeddings_collection.find(filter_criteria)
            embeddings_list = await embeddings_cursor.to_list(length=None)
            
            # حساب التشابه
            similarities = []
            for embedding_record in embeddings_list:
                similarity = self._calculate_similarity(
                    query_embedding,
                    embedding_record['embedding_vector']
                )
                
                similarities.append({
                    'content_id': embedding_record['content_id'],
                    'content_type': embedding_record['content_type'],
                    'text_content': embedding_record['text_content'],
                    'similarity_score': similarity,
                    'metadata': embedding_record.get('metadata', {})
                })
            
            # ترتيب حسب التشابه
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # إرجاع أفضل النتائج
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"خطأ في البحث الدلالي: {e}")
            return []
    
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """إنشاء تضمين متجه للنص باستخدام OpenAI"""
        try:
            if not self.openai_api_key:
                logger.warning("OpenAI API key not available for embeddings")
                return None
            
            # تنظيف النص
            cleaned_text = text.strip().replace('\n', ' ')[:8000]  # حد أقصى
            
            # إنشاء التضمين
            response = await openai.Embedding.acreate(
                input=cleaned_text,
                model=self.embedding_model
            )
            
            embedding_vector = response['data'][0]['embedding']
            return embedding_vector
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء التضمين: {e}")
            return None
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """حساب التشابه الكوسيني بين متجهين"""
        try:
            # تحويل إلى numpy arrays
            arr1 = np.array(vec1).reshape(1, -1)
            arr2 = np.array(vec2).reshape(1, -1)
            
            # حساب التشابه الكوسيني
            similarity = cosine_similarity(arr1, arr2)[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"خطأ في حساب التشابه: {e}")
            return 0.0
    
    async def get_embeddings_stats(self) -> Dict[str, Any]:
        """إحصائيات التضمينات المتجهة"""
        try:
            total_embeddings = await self.embeddings_collection.count_documents({})
            
            # إحصائيات حسب النوع
            pipeline = [
                {'$group': {'_id': '$content_type', 'count': {'$sum': 1}}}
            ]
            
            type_stats = {}
            async for stat in self.embeddings_collection.aggregate(pipeline):
                type_stats[stat['_id']] = stat['count']
            
            return {
                'total_embeddings': total_embeddings,
                'by_content_type': type_stats,
                'embedding_model': self.embedding_model,
                'embedding_dimensions': self.embedding_dimensions,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في إحصائيات التضمينات: {e}")
            return {'error': str(e)}

# إنشاء مثيل خدمة التضمينات
embeddings_service = None  # سيتم تهيئته في الخادم الرئيسي