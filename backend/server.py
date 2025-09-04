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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# إنشاء خدمة الدردشة وقاعدة المعرفة
chat_service = ChatService(db)
knowledge_base = OmaniLiteratureKnowledgeBase(db)

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

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "مرحباً! أنا غسان، مساعدك الأدبي العُماني الذكي"}

@api_router.post("/chat/message", response_model=ChatResponse)
async def send_message(request: ChatMessageRequest):
    """إرسال رسالة لغسان والحصول على رد ذكي"""
    try:
        result = await chat_service.process_user_message(
            message_text=request.message,
            session_id=request.session_id
        )
        
        return ChatResponse(
            message_id=result['message_id'],
            text=result['text'],
            session_id=result['session_id'],
            timestamp=result['timestamp'].isoformat() if hasattr(result['timestamp'], 'isoformat') else str(result['timestamp']),
            has_web_search=result.get('has_web_search', False),
            model_used=result.get('model_used')
        )
    except Exception as e:
        logging.error(f"خطأ في إرسال الرسالة: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في معالجة الرسالة: {str(e)}")

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
