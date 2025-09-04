import React, { useState, useRef, useEffect } from 'react';
import { Send, BookOpen, MessageCircle, Search, Globe } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ScrollArea } from '../ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { ChatService } from '../../services/chatService';

export const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const scrollAreaRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // إنشاء جلسة جديدة عند التحميل
  useEffect(() => {
    const initializeChat = async () => {
      try {
        // اختبار الاتصال
        const connectionTest = await ChatService.testConnection();
        if (connectionTest.success) {
          setIsConnected(true);
          
          // إنشاء جلسة جديدة
          const sessionResult = await ChatService.createNewSession();
          if (sessionResult.success) {
            setSessionId(sessionResult.data.session_id);
            
            // إضافة رسالة ترحيبية
            const welcomeMessage = {
              id: 'welcome_' + Date.now(),
              text: 'أهلاً وسهلاً! أنا غسان، مساعدك الأدبي العُماني الذكي. كيف يمكنني مساعدتك اليوم في عالم الأدب العُماني؟',
              sender: 'ghassan',
              timestamp: new Date().toISOString(),
              hasWebSearch: false
            };
            setMessages([welcomeMessage]);
          }
        } else {
          setIsConnected(false);
          console.error('فشل في الاتصال بالخادم');
        }
      } catch (error) {
        console.error('خطأ في تهيئة الدردشة:', error);
        setIsConnected(false);
      }
    };

    initializeChat();
  }, []);

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !sessionId || !isConnected) return;

    const userMessage = {
      id: Date.now(),
      text: newMessage,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    const messageText = newMessage;
    setNewMessage('');
    
    // التحقق من الحاجة للبحث
    const needsSearch = messageText.includes('أخبرني عن') || 
                       messageText.includes('معلومات عن') ||
                       messageText.includes('من هو') ||
                       messageText.includes('ما هي') ||
                       messageText.includes('بحث') ||
                       messageText.includes('اعثر على');

    if (needsSearch) {
      setIsSearching(true);
    } else {
      setIsTyping(true);
    }

    try {
      // إرسال الرسالة للـ backend
      const response = await ChatService.sendMessage(messageText, sessionId);
      
      if (response.success) {
        const aiResponse = {
          id: response.data.message_id,
          text: response.data.text,
          sender: 'ghassan',
          timestamp: response.data.timestamp,
          hasWebSearch: response.data.has_web_search,
          modelUsed: response.data.model_used
        };
        
        setMessages(prev => [...prev, aiResponse]);
      } else {
        // رسالة خطأ
        const errorMessage = {
          id: Date.now() + 1,
          text: 'عذراً، حدث خطأ في معالجة رسالتك. أرجو المحاولة مرة أخرى.',
          sender: 'ghassan',
          timestamp: new Date().toISOString(),
          hasWebSearch: false
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('خطأ في إرسال الرسالة:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'عذراً، لا أستطيع الاتصال بالخادم حالياً. أرجو المحاولة لاحقاً.',
        sender: 'ghassan',
        timestamp: new Date().toISOString(),
        hasWebSearch: false
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSearching(false);
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
      {/* Header */}
      <div className="bg-white border-b border-emerald-100 px-4 py-3 shadow-sm">
        <div className="flex items-center gap-3">
          <Avatar className="h-10 w-10 ring-2 ring-emerald-200">
            <AvatarImage src="/ghassan-avatar.jpg" alt="غسان" />
            <AvatarFallback className="bg-emerald-500 text-white font-bold">
              غ
            </AvatarFallback>
          </Avatar>
          <div>
            <h1 className="font-bold text-emerald-800 text-lg">غسان</h1>
            <p className="text-sm text-emerald-600">المساعد الأدبي العُماني الذكي</p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-emerald-600" />
            <MessageCircle className="h-5 w-5 text-emerald-600" />
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <ScrollArea className="flex-1 px-4 py-4" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className="flex items-end gap-2 max-w-xs sm:max-w-md lg:max-w-lg">
                {message.sender === 'ghassan' && (
                  <Avatar className="h-8 w-8 ring-2 ring-emerald-200">
                    <AvatarImage src="/ghassan-avatar.jpg" alt="غسان" />
                    <AvatarFallback className="bg-emerald-500 text-white text-sm">
                      غ
                    </AvatarFallback>
                  </Avatar>
                )}
                <div
                  className={`rounded-2xl px-4 py-2 shadow-sm transition-all duration-200 ${
                    message.sender === 'user'
                      ? 'bg-emerald-500 text-white rounded-br-sm'
                      : 'bg-white text-emerald-900 border border-emerald-100 rounded-bl-sm'
                  }`}
                >
                  <p className="text-sm leading-relaxed" style={{ direction: 'rtl', textAlign: 'right' }}>
                    {message.text}
                  </p>
                  {message.hasWebSearch && (
                    <div className="flex items-center gap-1 mt-2 text-xs text-emerald-600">
                      <Globe className="h-3 w-3" />
                      <span>تم البحث عبر الإنترنت</span>
                    </div>
                  )}
                  <p className={`text-xs mt-1 ${
                    message.sender === 'user' ? 'text-emerald-100' : 'text-emerald-500'
                  }`}>
                    {new Date(message.timestamp).toLocaleTimeString('ar-SA', { 
                      hour: '2-digit', 
                      minute: '2-digit',
                      hour12: false 
                    })}
                  </p>
                </div>
              </div>
            </div>
          ))}
          
          {isSearching && (
            <div className="flex justify-start">
              <div className="flex items-end gap-2 max-w-xs">
                <Avatar className="h-8 w-8 ring-2 ring-emerald-200">
                  <AvatarImage src="/ghassan-avatar.jpg" alt="غسان" />
                  <AvatarFallback className="bg-emerald-500 text-white text-sm">
                    غ
                  </AvatarFallback>
                </Avatar>
                <div className="bg-white border border-emerald-100 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                  <div className="flex items-center gap-2">
                    <Search className="h-4 w-4 text-emerald-500 animate-pulse" />
                    <span className="text-sm text-emerald-700">يبحث عبر الإنترنت...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {isTyping && !isSearching && (
            <div className="flex justify-start">
              <div className="flex items-end gap-2 max-w-xs">
                <Avatar className="h-8 w-8 ring-2 ring-emerald-200">
                  <AvatarImage src="/ghassan-avatar.jpg" alt="غسان" />
                  <AvatarFallback className="bg-emerald-500 text-white text-sm">
                    غ
                  </AvatarFallback>
                </Avatar>
                <div className="bg-white border border-emerald-100 rounded-2xl rounded-bl-sm px-4 py-2 shadow-sm">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Message Input */}
      <div className="bg-white border-t-2 border-emerald-200 p-4 shadow-lg sticky bottom-0">
        <div className="flex gap-3 items-center max-w-4xl mx-auto">
          <div className="flex-1">
            <Input
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="اكتب رسالتك هنا..."
              className="h-12 text-right border-2 border-emerald-200 focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 rounded-xl px-4 py-3 shadow-sm"
              style={{ direction: 'rtl' }}
              disabled={!newMessage.trim() || isTyping || isSearching || !isConnected || !sessionId}
            />
          </div>
          <Button 
            onClick={handleSendMessage}
            disabled={!newMessage.trim() || isTyping || isSearching || !isConnected || !sessionId}
            className="h-12 w-12 bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg transition-all duration-200 rounded-xl"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
};