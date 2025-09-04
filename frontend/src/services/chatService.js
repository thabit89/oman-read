import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export class ChatService {
  static async sendMessage(message, sessionId = null) {
    try {
      const response = await axios.post(`${API}/chat/message`, {
        message,
        session_id: sessionId
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('خطأ في إرسال الرسالة:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'حدث خطأ في الإرسال'
      };
    }
  }
  
  static async getChatHistory(sessionId, limit = 50) {
    try {
      const response = await axios.get(`${API}/chat/history/${sessionId}`, {
        params: { limit }
      });
      
      return {
        success: true,
        data: response.data.messages
      };
    } catch (error) {
      console.error('خطأ في جلب التاريخ:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'حدث خطأ في جلب التاريخ'
      };
    }
  }
  
  static async createNewSession() {
    try {
      const response = await axios.post(`${API}/chat/session`);
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('خطأ في إنشاء الجلسة:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'حدث خطأ في إنشاء الجلسة'
      };
    }
  }
  
  static async testConnection() {
    try {
      const response = await axios.get(`${API}/`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('خطأ في الاتصال:', error);
      return {
        success: false,
        error: 'خطأ في الاتصال بالخادم'
      };
    }
  }
  
  static async sendAdvancedMessage(message, sessionId = null) {
    try {
      const response = await axios.post(`${API}/chat/message-advanced`, {
        message,
        session_id: sessionId
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('خطأ في إرسال الرسالة المتقدمة:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'حدث خطأ في الإرسال'
      };
    }
  }
}