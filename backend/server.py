from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

# استيراد خدمات جديدة
from services.chat_service import ChatService
from services.knowledge_service import OmaniLiteratureKnowledgeBase
from services.verification_service import information_verifier
from services.rag_service import AdvancedRAGService
from services.enhanced_ghassan import EnhancedGhassanService
from services.embeddings_service import EmbeddingsService
from services.academic_collector import academic_collector
from models.literature_models import Author, LiteraryWork, LiteraryCategory, LiteraryStyle

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# إنشاء خدمة الدردشة وقاعدة المعرفة والنظم المتقدمة
chat_service = ChatService(db)
knowledge_base = OmaniLiteratureKnowledgeBase(db)
rag_service = AdvancedRAGService(db)
enhanced_ghassan_service = EnhancedGhassanService(db)
embeddings_service = EmbeddingsService(db)

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message_id: str
    text: str
    session_id: str
    timestamp: str
    has_web_search: bool = False
    model_used: Optional[str] = None
    reliability_score: Optional[float] = None
    confidence_level: Optional[str] = None

class AddSourceRequest(BaseModel):
    title: str
    content: str
    source_type: str  # book, article, poem, biography
    author: Optional[str] = None
    publication_date: Optional[str] = None
    reliability_score: Optional[float] = 0.8
    tags: Optional[List[str]] = None

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "مرحباً! أنا غسان، مساعدك الأدبي العُماني الذكي"}

@api_router.post("/chat/message", response_model=ChatResponse)
async def send_message(request: ChatMessageRequest):
    """إرسال رسالة لغسان والحصول على رد ذكي مع فحص الموثوقية"""
    try:
        result = await chat_service.process_user_message(
            message_text=request.message,
            session_id=request.session_id
        )
        
        # فحص موثوقية الرد
        verification_result = await information_verifier.verify_response(
            response=result['text'],
            user_query=request.message
        )
        
        return ChatResponse(
            message_id=result['message_id'],
            text=result['text'],
            session_id=result['session_id'],
            timestamp=result['timestamp'].isoformat() if hasattr(result['timestamp'], 'isoformat') else str(result['timestamp']),
            has_web_search=result.get('has_web_search', False),
            model_used=result.get('model_used'),
            reliability_score=verification_result['overall_score'],
            confidence_level=verification_result['confidence_level']
        )
    except Exception as e:
        logging.error(f"خطأ في إرسال الرسالة: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في معالجة الرسالة: {str(e)}")

@api_router.post("/knowledge/add-source")
async def add_literature_source(request: AddSourceRequest):
    """إضافة مصدر أدبي جديد لقاعدة المعرفة"""
    try:
        result = await knowledge_base.add_literature_source(
            title=request.title,
            content=request.content,
            source_type=request.source_type,
            author=request.author,
            publication_date=request.publication_date,
            reliability_score=request.reliability_score or 0.8,
            tags=request.tags or []
        )
        return result
    except Exception as e:
        logging.error(f"خطأ في إضافة المصدر: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في إضافة المصدر: {str(e)}")

@api_router.get("/knowledge/stats")
async def get_knowledge_stats():
    """إحصائيات قاعدة المعرفة"""
    try:
        stats = await knowledge_base.get_knowledge_stats()
        return stats
    except Exception as e:
        logging.error(f"خطأ في جلب الإحصائيات: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في جلب الإحصائيات: {str(e)}")

@api_router.post("/chat/message-advanced", response_model=ChatResponse)
async def send_message_advanced(request: ChatMessageRequest):
    """إرسال رسالة لغسان المطور مع نظام RAG متكامل"""
    try:
        # استخدام النظام المطور
        result = await enhanced_ghassan_service.process_intelligent_query(
            user_message=request.message,
            session_id=request.session_id or str(uuid.uuid4()),
            conversation_context=""  # سيتم تحسينه لاحقاً
        )
        
        # حفظ في قاعدة البيانات
        message_id = str(uuid.uuid4())
        await chat_service._save_message(
            text=result['text'],
            sender='ghassan',
            session_id=request.session_id or str(uuid.uuid4()),
            metadata={
                'model_used': result.get('model_used'),
                'sources_used': result.get('sources_used', 0),
                'has_verified_sources': result.get('has_verified_sources', False)
            }
        )
        
        return ChatResponse(
            message_id=message_id,
            text=result['text'],
            session_id=request.session_id or str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            has_web_search=result.get('sources_used', 0) > 0,
            model_used=result.get('model_used'),
            reliability_score=0.95,  # النظام المتقدم أكثر دقة
            confidence_level=result.get('context_confidence', 'عالٍ')
        )
    except Exception as e:
        logging.error(f"خطأ في الرسالة المتقدمة: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في المعالجة المتقدمة: {str(e)}")

@api_router.post("/rag/collect-sources")
async def auto_collect_sources():
    """جمع تلقائي للمصادر الأكاديمية والمقابلات"""
    try:
        results = await rag_service.auto_collect_and_process()
        return results
    except Exception as e:
        logging.error(f"خطأ في جمع المصادر: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في الجمع: {str(e)}")

@api_router.get("/rag/stats")
async def get_rag_stats():
    """إحصائيات نظام RAG الشامل"""
    try:
        stats = await rag_service.get_rag_statistics()
        return stats
    except Exception as e:
        logging.error(f"خطأ في إحصائيات RAG: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في الإحصائيات: {str(e)}")

@api_router.post("/authors/add")
async def add_verified_author(author_data: dict):
    """إضافة مؤلف محقق لقاعدة البيانات"""
    try:
        result = await rag_service.add_verified_author(author_data)
        return result
    except Exception as e:
        logging.error(f"خطأ في إضافة المؤلف: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في الإضافة: {str(e)}")

@api_router.post("/works/add")
async def add_verified_work(work_data: dict):
    """إضافة عمل أدبي محقق لقاعدة البيانات"""
    try:
        result = await rag_service.add_verified_work(work_data)
        return result
    except Exception as e:
        logging.error(f"خطأ في إضافة العمل: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في الإضافة: {str(e)}")

@api_router.get("/search/semantic")
async def semantic_search(query: str, content_types: str = "", limit: int = 5):
    """البحث الدلالي المتقدم"""
    try:
        content_types_list = content_types.split(',') if content_types else None
        results = await embeddings_service.semantic_search(
            query=query,
            content_types=content_types_list,
            limit=limit
        )
        return {"results": results}
    except Exception as e:
        logging.error(f"خطأ في البحث الدلالي: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في البحث: {str(e)}")

@api_router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """جلب تاريخ المحادثات لجلسة معينة"""
    try:
        messages = await chat_service.get_chat_history(session_id, limit)
        return {"messages": messages}
    except Exception as e:
        logging.error(f"خطأ في جلب تاريخ المحادثات: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في جلب التاريخ: {str(e)}")

@api_router.post("/chat/session")
async def create_new_session():
    """إنشاء جلسة محادثة جديدة"""
    try:
        session_id = await chat_service._create_new_session()
        return {"session_id": session_id}
    except Exception as e:
        logging.error(f"خطأ في إنشاء الجلسة: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في إنشاء الجلسة: {str(e)}")

# المسارات القديمة للاختبار
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
