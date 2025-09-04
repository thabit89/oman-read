import os
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
import asyncio
from dotenv import load_dotenv
from pathlib import Path
import pickle

load_dotenv()

logger = logging.getLogger(__name__)

class AdvancedGhassanService:
    """خدمة غسان المتقدمة باستخدام LangChain و FAISS"""
    
    def __init__(self):
        # إعداد API Keys
        self.openai_api_key = os.environ.get('EMERGENT_LLM_KEY')
        self.claude_api_key = os.environ.get('ANTHROPIC_API_KEY')
        
        # إعداد النماذج
        if self.openai_api_key:
            self.gpt_model = ChatOpenAI(
                model="gpt-4o",
                temperature=0.8,  # للإبداع والسلاسة
                openai_api_key=self.openai_api_key
            )
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        
        if self.claude_api_key:
            self.claude_model = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.5,  # للتحليل العميق والدقة
                api_key=self.claude_api_key
            )
        
        # مسار قاعدة البيانات المتجهة
        self.vectorstore_path = "/app/backend/data/omani_literature_vectordb"
        self.vectorstore = None
        
        # إعداد Prompt لشخصية غسان
        self.ghassan_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""أنت غسان - المساعد الأدبي العُماني المرح والذكي!

🌟 أنت صديق أدبي محبوب، مُلم بالأدب العُماني حصرياً، مرح ولطيف، ودقيق علمياً.

📚 المعرفة المتاحة من قاعدة البيانات:
{context}

❓ سؤال الصديق:
{question}

🎯 تعليمات الرد:
• كن مرحاً وودوداً: "أهلاً يا صديقي!" "ما أجمل سؤالك!"
• استخدم عبارات عُمانية أصيلة: "بارك الله فيك" "ما شاء الله"
• لغة عربية فصيحة سليمة 100%
• إذا لم تجد معلومات دقيقة، اعترف بذلك بلطف
• قدم تحليلاً عميقاً عند الطلب
• ركز على الأدب العُماني فقط
• استخدم المصطلحات النقدية والنحوية بدقة

تذكر: أنت لست مجرد أداة، بل صديق أدبي يجمع بين المرح والعلم والصدق!"""
        )
        
        # إعداد text splitter للمحتوى العربي
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "؟", "!", "؛"]
        )
        
        # تحميل قاعدة البيانات المتجهة إذا كانت موجودة
        asyncio.create_task(self._initialize_vectorstore())
    
    async def _initialize_vectorstore(self):
        """تهيئة قاعدة البيانات المتجهة"""
        try:
            # إنشاء مجلد البيانات إذا لم يكن موجوداً
            Path(self.vectorstore_path).parent.mkdir(parents=True, exist_ok=True)
            
            if os.path.exists(f"{self.vectorstore_path}.pkl") and self.embeddings:
                # تحميل قاعدة بيانات موجودة
                self.vectorstore = FAISS.load_local(
                    self.vectorstore_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("تم تحميل قاعدة البيانات المتجهة الموجودة")
            else:
                # إنشاء قاعدة بيانات جديدة مع محتوى أساسي
                await self._create_initial_vectorstore()
                
        except Exception as e:
            logger.error(f"خطأ في تهيئة قاعدة البيانات المتجهة: {e}")
            self.vectorstore = None
    
    async def _create_initial_vectorstore(self):
        """إنشاء قاعدة بيانات متجهة أولية بمحتوى أساسي"""
        try:
            # محتوى أساسي عن الأدب العُماني
            initial_content = [
                Document(
                    page_content="سيف الرحبي شاعر عُماني معاصر وُلد عام 1956، يُعتبر من أبرز أصوات الشعر العربي الحديث. يتميز شعره بالتأمل الفلسفي والارتباط بالطبيعة العُمانية. من أشهر أعماله ديوان 'رأس المسافر'.",
                    metadata={"source": "معلومات أساسية", "topic": "شعراء", "author": "سيف الرحبي"}
                ),
                Document(
                    page_content="هدى حمد شاعرة عُمانية معاصرة، تُعتبر من رائدات الشعر النسائي في السلطنة. تتناول في أشعارها قضايا المرأة والمجتمع العُماني بأسلوب معاصر وحساس.",
                    metadata={"source": "معلومات أساسية", "topic": "شعراء", "author": "هدى حمد"}
                ),
                Document(
                    page_content="الأدب العُماني له تاريخ عريق يمتد عبر القرون، من الشعر الكلاسيكي إلى النثر المعاصر. يتميز بارتباطه الوثيق بالبيئة والثقافة العُمانية الأصيلة.",
                    metadata={"source": "معلومات أساسية", "topic": "تاريخ أدبي"}
                )
            ]
            
            if self.embeddings:
                self.vectorstore = FAISS.from_documents(initial_content, self.embeddings)
                
                # حفظ قاعدة البيانات
                self.vectorstore.save_local(self.vectorstore_path)
                logger.info("تم إنشاء قاعدة البيانات المتجهة الأولية")
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء قاعدة البيانات الأولية: {e}")
    
    async def add_content_to_vectorstore(self, content: str, metadata: Dict[str, Any]):
        """إضافة محتوى جديد لقاعدة البيانات المتجهة"""
        try:
            if not self.vectorstore or not self.embeddings:
                logger.warning("قاعدة البيانات المتجهة غير متاحة")
                return False
            
            # تقسيم المحتوى
            chunks = self.text_splitter.split_text(content)
            
            # إنشاء documents
            documents = [
                Document(page_content=chunk, metadata=metadata)
                for chunk in chunks
            ]
            
            # إضافة للقاعدة
            self.vectorstore.add_documents(documents)
            
            # حفظ التحديث
            self.vectorstore.save_local(self.vectorstore_path)
            
            logger.info(f"تم إضافة {len(documents)} قطعة جديدة لقاعدة البيانات")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إضافة المحتوى: {e}")
            return False
    
    async def answer_with_advanced_rag(self, user_query: str) -> Dict[str, Any]:
        """الإجابة المتقدمة باستخدام RAG (Retrieval Augmented Generation)"""
        
        try:
            # البحث في قاعدة البيانات المتجهة
            relevant_docs = []
            if self.vectorstore:
                relevant_docs = self.vectorstore.similarity_search(user_query, k=3)
            
            # تجميع السياق
            context = "\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else "لا توجد معلومات متاحة في قاعدة البيانات"
            
            # تحديد النموذج المناسب
            is_analytical_query = self._is_analytical_query(user_query)
            
            if is_analytical_query and self.claude_model:
                # استخدام Claude للتحليل العميق
                analysis = await self._claude_analysis(context, user_query)
                
                if self.gpt_model:
                    # GPT للصياغة النهائية المرحة
                    final_response = await self._gpt_final_polish(analysis, user_query)
                else:
                    final_response = analysis
                    
                return {
                    'text': final_response,
                    'model_used': 'claude+gpt-hybrid',
                    'has_vectorstore_context': bool(relevant_docs),
                    'context_sources': len(relevant_docs)
                }
            
            elif self.gpt_model:
                # استخدام GPT للاستفسارات العامة
                response = await self._gpt_response(context, user_query)
                
                return {
                    'text': response,
                    'model_used': 'gpt-4o-rag',
                    'has_vectorstore_context': bool(relevant_docs),
                    'context_sources': len(relevant_docs)
                }
            
            else:
                return {
                    'text': 'عذراً، الخدمة غير متاحة حالياً.',
                    'model_used': 'none',
                    'has_vectorstore_context': False,
                    'context_sources': 0
                }
                
        except Exception as e:
            logger.error(f"خطأ في الإجابة المتقدمة: {e}")
            return {
                'text': 'عذراً، حدث خطأ في معالجة طلبك.',
                'model_used': 'error',
                'has_vectorstore_context': False,
                'context_sources': 0,
                'error': str(e)
            }
    
    def _is_analytical_query(self, query: str) -> bool:
        """تحديد إذا كان السؤال يحتاج تحليل عميق"""
        analytical_keywords = [
            'تحليل', 'نقد', 'إعراب', 'بلاغة', 'عروض',
            'نحو', 'صرف', 'أسلوب', 'بنية', 'نظرية'
        ]
        return any(keyword in query.lower() for keyword in analytical_keywords)
    
    async def _claude_analysis(self, context: str, question: str) -> str:
        """تحليل عميق باستخدام Claude"""
        if not self.claude_model:
            raise ValueError("Claude model not available")
        
        # تحديد نوع التحليل المطلوب
        analysis_type = self._determine_analysis_type(question)
        
        enhanced_prompt = f"""
{self.ghassan_prompt.template}

نوع التحليل المطلوب: {analysis_type}

إرشادات خاصة:
- قدم تحليلاً أكاديمياً عميقاً
- استخدم النظريات النقدية المناسبة
- اربط بالسياق الثقافي العُماني
- كن دقيقاً في المصطلحات
"""

        response = self.claude_model.predict(
            enhanced_prompt.format(context=context, question=question)
        )
        return response
    
    async def _gpt_final_polish(self, analysis: str, original_question: str) -> str:
        """صياغة نهائية مرحة وودودة بـ GPT"""
        if not self.gpt_model:
            return analysis
        
        polish_prompt = f"""
أنت غسان الودود! خذ هذا التحليل الأكاديمي وأعد صياغته بطريقة مرحة ولطيفة:

التحليل الأكاديمي:
{analysis}

السؤال الأصلي:
{original_question}

اجعله:
- مرحاً وودوداً: استخدم "يا صديقي"، "ما أروعك!"
- بعبارات عُمانية أصيلة: "بارك الله فيك"، "ما شاء الله"
- محافظاً على الدقة العلمية
- منظماً وواضحاً
- متحمساً للأدب العُماني

احتفظ بجميع المعلومات والتفاصيل، فقط غير الأسلوب ليصبح أكثر مرحاً!
"""
        
        polished = self.gpt_model.predict(polish_prompt)
        return polished
    
    async def _gpt_response(self, context: str, question: str) -> str:
        """رد مباشر من GPT للاستفسارات العامة"""
        if not self.gpt_model:
            raise ValueError("GPT model not available")
        
        response = self.gpt_model.predict(
            self.ghassan_prompt.format(context=context, question=question)
        )
        return response
    
    def _determine_analysis_type(self, question: str) -> str:
        """تحديد نوع التحليل المطلوب"""
        if 'نحو' in question or 'إعراب' in question:
            return 'تحليل نحوي متخصص'
        elif 'بلاغة' in question or 'صورة شعرية' in question:
            return 'تحليل بلاغي وأسلوبي'
        elif 'عروض' in question or 'بحر' in question:
            return 'تحليل عروضي وإيقاعي'
        elif 'نقد' in question or 'نظرية' in question:
            return 'نقد أدبي بالنظريات الحديثة'
        else:
            return 'تحليل أدبي شامل'

    async def search_vectorstore(self, query: str, k: int = 5) -> List[Document]:
        """البحث في قاعدة البيانات المتجهة"""
        if not self.vectorstore:
            return []
        
        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"خطأ في البحث المتجه: {e}")
            return []
    
    async def get_vectorstore_stats(self) -> Dict[str, Any]:
        """إحصائيات قاعدة البيانات المتجهة"""
        try:
            if not self.vectorstore:
                return {"status": "غير متاح", "count": 0}
            
            # عدد تقريبي للوثائق
            index_size = self.vectorstore.index.ntotal if hasattr(self.vectorstore, 'index') else 0
            
            return {
                "status": "نشط",
                "documents_count": index_size,
                "embeddings_available": bool(self.embeddings),
                "vectorstore_path": self.vectorstore_path
            }
            
        except Exception as e:
            logger.error(f"خطأ في إحصائيات قاعدة البيانات: {e}")
            return {"status": "خطأ", "error": str(e)}

# إنشاء مثيل الخدمة المتقدمة
advanced_ghassan_service = AdvancedGhassanService()