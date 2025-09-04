from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
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
import shutil

# استيراد خدمات جديدة
from services.chat_service import ChatService
from services.knowledge_service import OmaniLiteratureKnowledgeBase
from services.verification_service import information_verifier
from services.simple_collector import simple_collector

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# إنشاء خدمة الدردشة وقاعدة المعرفة والنظم المتقدمة
chat_service = ChatService(db)
knowledge_base = OmaniLiteratureKnowledgeBase(db)

# Create the main app without a prefix
app = FastAPI()

# إعداد مجلد الصور الثابتة
UPLOADS_DIR = Path("/app/frontend/public/uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# تقديم الصور الثابتة
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

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

class ContactRequest(BaseModel):
    name: str
    email: str
    subject: str
    message: str

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

@api_router.post("/contact/send")
async def send_contact_message(request: ContactRequest):
    """إرسال رسالة الاتصال"""
    try:
        # حفظ في قاعدة البيانات
        contact_data = {
            'contact_id': str(uuid.uuid4()),
            'name': request.name,
            'email': request.email,
            'subject': request.subject,
            'message': request.message,
            'submitted_at': datetime.utcnow(),
            'status': 'new'
        }
        
        await db.contact_messages.insert_one(contact_data)
        
        return {
            'success': True,
            'message': 'تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.',
            'contact_id': contact_data['contact_id']
        }
    except Exception as e:
        logging.error(f"خطأ في إرسال رسالة الاتصال: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في إرسال الرسالة: {str(e)}")

@api_router.get("/knowledge/stats")
async def get_knowledge_stats():
    """إحصائيات قاعدة المعرفة"""
    try:
        stats = await knowledge_base.get_knowledge_stats()
        return stats
    except Exception as e:
        logging.error(f"خطأ في جلب الإحصائيات: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في جلب الإحصائيات: {str(e)}")

# @api_router.post("/chat/message-advanced", response_model=ChatResponse)
# async def send_message_advanced(request: ChatMessageRequest):
#     """إرسال رسالة لغسان المطور مع نظام RAG متكامل"""
#     try:
#         # استخدام النظام المطور
#         result = await enhanced_ghassan_service.process_intelligent_query(
#             user_message=request.message,
#             session_id=request.session_id or str(uuid.uuid4()),
#             conversation_context=""  # سيتم تحسينه لاحقاً
#         )
#         
#         # حفظ في قاعدة البيانات
#         message_id = str(uuid.uuid4())
#         await chat_service._save_message(
#             text=result['text'],
#             sender='ghassan',
#             session_id=request.session_id or str(uuid.uuid4()),
#             metadata={
#                 'model_used': result.get('model_used'),
#                 'sources_used': result.get('sources_used', 0),
#                 'has_verified_sources': result.get('has_verified_sources', False)
#             }
#         )
#         
#         return ChatResponse(
#             message_id=message_id,
#             text=result['text'],
#             session_id=request.session_id or str(uuid.uuid4()),
#             timestamp=datetime.utcnow().isoformat(),
#             has_web_search=result.get('sources_used', 0) > 0,
#             model_used=result.get('model_used'),
#             reliability_score=0.95,  # النظام المتقدم أكثر دقة
#             confidence_level=result.get('context_confidence', 'عالٍ')
#         )
#     except Exception as e:
#         logging.error(f"خطأ في الرسالة المتقدمة: {e}")
#         raise HTTPException(status_code=500, detail=f"خطأ في المعالجة المتقدمة: {str(e)}")

# @api_router.post("/rag/collect-sources")
# async def auto_collect_sources():
#     """جمع تلقائي للمصادر الأكاديمية والمقابلات"""
#     try:
#         results = await rag_service.auto_collect_and_process()
#         return results
#     except Exception as e:
#         logging.error(f"خطأ في جمع المصادر: {e}")
#         raise HTTPException(status_code=500, detail=f"خطأ في الجمع: {str(e)}")

# @api_router.get("/rag/stats")
# async def get_rag_stats():
#     """إحصائيات نظام RAG الشامل"""
#     try:
#         stats = await rag_service.get_rag_statistics()
#         return stats
#     except Exception as e:
#         logging.error(f"خطأ في إحصائيات RAG: {e}")
#         raise HTTPException(status_code=500, detail=f"خطأ في الإحصائيات: {str(e)}")

# @api_router.post("/authors/add")
# async def add_verified_author(author_data: dict):
#     """إضافة مؤلف محقق لقاعدة البيانات"""
#     try:
#         result = await rag_service.add_verified_author(author_data)
#         return result
#     except Exception as e:
#         logging.error(f"خطأ في إضافة المؤلف: {e}")
#         raise HTTPException(status_code=500, detail=f"خطأ في الإضافة: {str(e)}")

# @api_router.post("/works/add")
# async def add_verified_work(work_data: dict):
#     """إضافة عمل أدبي محقق لقاعدة البيانات"""
#     try:
#         result = await rag_service.add_verified_work(work_data)
#         return result
#     except Exception as e:
#         logging.error(f"خطأ في إضافة العمل: {e}")
#         raise HTTPException(status_code=500, detail=f"خطأ في الإضافة: {str(e)}")

@api_router.post("/upload/avatar")
async def upload_ghassan_avatar(image: UploadFile = File(...), type: str = "avatar", name: str = "ghassan-avatar"):
    """رفع صورة avatar لغسان"""
    try:
        # التحقق من نوع الملف
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="يجب أن يكون الملف صورة")
        
        # التحقق من حجم الملف (5MB)
        content = await image.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="حجم الصورة كبير جداً (أقل من 5MB)")
        
        # إنشاء اسم ملف فريد
        file_extension = image.filename.split(".")[-1].lower()
        filename = f"ghassan-avatar.{file_extension}"
        file_path = UPLOADS_DIR / filename
        
        # حفظ الصورة
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # إنشاء رابط للوصول للصورة
        image_url = f"/uploads/{filename}"
        
        logger.info(f"تم رفع صورة غسان: {filename}")
        
        return {
            "success": True,
            "filename": filename,
            "image_url": image_url,
            "message": "تم رفع صورة غسان بنجاح",
            "file_size": len(content)
        }
        
    except Exception as e:
        logger.error(f"خطأ في رفع الصورة: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في رفع الصورة: {str(e)}")

@api_router.get("/avatar/current")
async def get_current_avatar():
    """الحصول على صورة غسان الحالية"""
    try:
        # البحث عن صور غسان في مجلد uploads
        avatar_files = []
        for ext in ['jpg', 'jpeg', 'png', 'webp']:
            avatar_path = UPLOADS_DIR / f"ghassan-avatar.{ext}"
            if avatar_path.exists():
                avatar_files.append({
                    'filename': f"ghassan-avatar.{ext}",
                    'url': f"/uploads/ghassan-avatar.{ext}",
                    'size': avatar_path.stat().st_size,
                    'modified': datetime.fromtimestamp(avatar_path.stat().st_mtime).isoformat()
                })
        
        if avatar_files:
            # إرجاع أحدث صورة
            latest_avatar = max(avatar_files, key=lambda x: x['modified'])
            return {
                "success": True,
                "current_avatar": latest_avatar,
                "all_avatars": avatar_files
            }
        else:
            return {
                "success": False,
                "message": "لا توجد صورة حالية لغسان"
            }
            
    except Exception as e:
        logger.error(f"خطأ في جلب الصورة الحالية: {e}")
@api_router.post("/collect/simple")
async def simple_collect_sources():
    """جمع بسيط للمصادر من المقابلات والمقالات"""
    try:
        results = await simple_collector.bulk_collect_all_authors()
        
        # حفظ النتائج في قاعدة البيانات للاستفادة منها لاحقاً
        await db.collected_sources.insert_one({
            'collection_id': str(uuid.uuid4()),
            'results': results,
            'collection_date': datetime.utcnow(),
            'status': 'completed' if results.get('collection_completed') else 'failed'
        })
        
        return results
    except Exception as e:
        logging.error(f"خطأ في الجمع البسيط: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في الجمع: {str(e)}")

@api_router.get("/collect/author/{author_name}")
async def collect_for_specific_author(author_name: str):
    """جمع مصادر لمؤلف محدد"""
    try:
        results = await simple_collector.collect_sources_for_author(author_name)
        
        # حفظ نتائج هذا المؤلف
        await db.author_sources.insert_one({
            'author_name': author_name,
            'sources': results,
            'collection_date': datetime.utcnow()
        })
        
        return results
    except Exception as e:
        logging.error(f"خطأ في جمع مصادر المؤلف: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في الجمع: {str(e)}")

@api_router.get("/sources/stats")
async def get_sources_stats():
    """إحصائيات المصادر المجمعة"""
    try:
        total_collections = await db.collected_sources.count_documents({})
        total_authors = await db.author_sources.count_documents({})
        
        # آخر عمليات الجمع
        recent_collections = await db.collected_sources.find().sort('collection_date', -1).limit(3).to_list(3)
        
        return {
            'total_collections': total_collections,
            'total_author_collections': total_authors,
            'recent_collections': recent_collections,
            'last_updated': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logging.error(f"خطأ في إحصائيات المصادر: {e}")
        return {'error': str(e)}

@api_router.get("/collect/author/{author_name}")
async def collect_for_specific_author(author_name: str):
    """جمع مصادر لمؤلف محدد"""
    try:
        results = await simple_collector.collect_sources_for_author(author_name)
        
        # حفظ نتائج هذا المؤلف
        await db.author_sources.insert_one({
            'author_name': author_name,
            'sources': results,
            'collection_date': datetime.utcnow()
        })
        
        return results
    except Exception as e:
        logging.error(f"خطأ في جمع مصادر المؤلف: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في الجمع: {str(e)}")

@api_router.get("/sources/stats")
async def get_sources_stats():
    """إحصائيات المصادر المجمعة"""
    try:
        total_collections = await db.collected_sources.count_documents({})
        total_authors = await db.author_sources.count_documents({})
        
        # آخر عمليات الجمع
        recent_collections = await db.collected_sources.find().sort('collection_date', -1).limit(3).to_list(3)
        
        return {
            'total_collections': total_collections,
            'total_author_collections': total_authors,
            'recent_collections': recent_collections,
            'last_updated': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logging.error(f"خطأ في إحصائيات المصادر: {e}")
        return {'error': str(e)}

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
