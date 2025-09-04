from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class LiteraryCategory(str, Enum):
    """تصنيفات الأدب العُماني"""
    POETRY = "شعر"
    NOVEL = "رواية"
    SHORT_STORY = "قصة قصيرة"
    PLAY = "مسرحية"
    CRITICISM = "نقد أدبي"
    FOLKLORE = "أدب شعبي"
    CONTEMPORARY = "أدب معاصر"
    CLASSICAL = "أدب كلاسيكي"
    TRANSLATION = "ترجمة"

class LiteraryStyle(str, Enum):
    """الأساليب الأدبية"""
    TRADITIONAL = "تقليدي"
    MODERNIST = "حداثي"
    CONTEMPORARY = "معاصر"
    EXPERIMENTAL = "تجريبي"
    SYMBOLIC = "رمزي"
    REALISTIC = "واقعي"
    ROMANTIC = "رومانسي"

class ReferenceSource(BaseModel):
    """مصدر مرجعي"""
    title: str
    author: Optional[str] = None
    publication_year: Optional[str] = None
    publisher: Optional[str] = None
    url: Optional[str] = None
    source_type: str  # academic, journal, interview, article, book
    reliability_score: float = Field(ge=0.0, le=1.0, default=0.8)
    access_date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class LiteraryWork(BaseModel):
    """عمل أدبي"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    title: str
    author_id: str
    publication_year: Optional[str] = None
    category: LiteraryCategory
    style: LiteraryStyle
    main_theme: str
    summary: str
    critical_notes: List[str] = Field(default_factory=list)
    references: List[ReferenceSource] = Field(default_factory=list)
    
    # للبحث والتحليل
    text_content: Optional[str] = None  # النص الكامل إذا متوفر
    keywords: List[str] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    
    # معلومات تقنية
    embedding_id: Optional[str] = None
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class Author(BaseModel):
    """مؤلف عُماني"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    full_name: str
    birth_date: Optional[str] = None  # نص مفتوح للمرونة
    death_date: Optional[str] = None
    birth_place: Optional[str] = None
    
    # السيرة والمعلومات
    biography: str = ""
    literary_periods: List[str] = Field(default_factory=list)  # كلاسيكي، معاصر، إلخ
    main_genres: List[LiteraryCategory] = Field(default_factory=list)
    influences: List[str] = Field(default_factory=list)  # تأثيرات أدبية
    
    # الأعمال والمراجع
    works: List[str] = Field(default_factory=list)  # قائمة معرفات الأعمال
    references: List[ReferenceSource] = Field(default_factory=list)
    interviews: List[str] = Field(default_factory=list)  # روابط مقابلات
    
    # للبحث
    aliases: List[str] = Field(default_factory=list)  # أسماء بديلة أو مستعارة
    tags: List[str] = Field(default_factory=list)
    
    # معلومات تقنية
    embedding_id: Optional[str] = None
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False  # هل المعلومات محققة

class AcademicSource(BaseModel):
    """مصدر أكاديمي متخصص"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    title: str
    authors: List[str]
    abstract: str
    full_text: Optional[str] = None
    
    # معلومات النشر
    journal_name: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publication_date: Optional[str] = None
    doi: Optional[str] = None
    isbn: Optional[str] = None
    
    # التصنيف
    topic: str
    keywords: List[str] = Field(default_factory=list)
    covered_authors: List[str] = Field(default_factory=list)
    covered_works: List[str] = Field(default_factory=list)
    
    # للبحث المتقدم
    embedding_id: Optional[str] = None
    citations_count: int = 0
    relevance_score: float = 0.0
    
    # الوصول والمراجع
    url: Optional[str] = None
    access_restrictions: Optional[str] = None
    downloaded_date: datetime = Field(default_factory=datetime.utcnow)

class SearchQuery(BaseModel):
    """استعلام البحث مع التتبع"""
    query_text: str
    user_session: str
    search_type: str  # author, work, topic, general
    results_count: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    response_quality: Optional[float] = None

class EmbeddingRecord(BaseModel):
    """سجل التضمين المتجه"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    content_id: str  # معرف المحتوى الأصلي
    content_type: str  # author, work, academic_source, reference
    text_content: str
    embedding_vector: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_date: datetime = Field(default_factory=datetime.utcnow)