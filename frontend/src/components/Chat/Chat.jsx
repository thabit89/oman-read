import React, { useState, useRef, useEffect } from 'react';
import { Send, BookOpen, MessageCircle, Search, Globe, Sparkles, Brain } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ScrollArea } from '../ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
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
          hasWebSearch: response.data.has_web_search
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
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-blue-50 to-cyan-50">
      {/* Animated Background Pattern */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-4 -left-4 w-72 h-72 bg-gradient-to-r from-blue-400/10 to-purple-400/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/3 right-8 w-96 h-96 bg-gradient-to-r from-emerald-400/8 to-teal-400/8 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-8 left-1/4 w-64 h-64 bg-gradient-to-r from-amber-400/10 to-orange-400/10 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>

      {/* Main Container */}
      <div className="relative z-10 flex flex-col h-screen max-w-6xl mx-auto">
        
        {/* Enhanced Header */}
        <div className="bg-white/80 backdrop-blur-xl border-b border-white/20 shadow-lg sticky top-0 z-20">
          <div className="px-6 py-4">
            <div className="flex items-center gap-4">
              
              {/* Avatar with Glow Effect - Enhanced */}
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full blur animate-pulse"></div>
                <Avatar className="relative h-18 w-18 ring-2 ring-emerald-200 shadow-lg hover:scale-105 transition-all duration-200">
                  <AvatarImage 
                    src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face&auto=format&q=80"
                    alt="غسان - المساعد الأدبي العُماني" 
                    className="object-cover"
                  />
                  <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-teal-500 text-white font-bold text-lg">
                    غ
                  </AvatarFallback>
                </Avatar>
              </div>

              {/* Title and Description */}
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-800 to-teal-700 bg-clip-text text-transparent">
                    غسان
                  </h1>
                  <Badge variant="secondary" className="bg-gradient-to-r from-emerald-100 to-teal-100 text-emerald-700 border-emerald-200">
                    <Sparkles className="h-3 w-3 mr-1" />
                    ذكي ومتطور
                  </Badge>
                </div>
                <p className="text-emerald-600 text-sm mt-1">
                  المساعد الأدبي العُماني الذكي • مدعوم بالذكاء الاصطناعي والبحث المتقدم
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-3">
                <Button
                  variant="ghost"
                  size="sm"
                  asChild
                  className="text-emerald-600 hover:bg-emerald-50 hover:text-emerald-700"
                >
                  <a href="/knowledge" title="إدارة المصادر">
                    <BookOpen className="h-5 w-5" />
                  </a>
                </Button>
                
                <Button
                  variant="ghost"
                  size="sm"
                  asChild
                  className="text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700"
                >
                  <a href="/advanced" title="النظام المتقدم">
                    <Brain className="h-5 w-5" />
                  </a>
                </Button>
              </div>
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
                  <Avatar className="h-12 w-12 ring-2 ring-white/60 shadow-lg transition-all duration-200 group-hover:scale-105">
                    <AvatarImage 
                      src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face&auto=format&q=80"
                      alt="غسان" 
                      className="object-cover"
                    />
                    <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-teal-500 text-white text-sm font-semibold">
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
                <Avatar className="h-12 w-12 ring-2 ring-white/60 shadow-lg transition-all duration-200 group-hover:scale-105">
                  <AvatarImage 
                    src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face&auto=format&q=80"
                    alt="غسان" 
                    className="object-cover"
                  />
                  <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-teal-500 text-white text-sm font-semibold">
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
                <Avatar className="h-12 w-12 ring-2 ring-white/60 shadow-lg transition-all duration-200 group-hover:scale-105">
                  <AvatarImage 
                    src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face&auto=format&q=80"
                    alt="غسان" 
                    className="object-cover"
                  />
                  <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-teal-500 text-white text-sm font-semibold">
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
              disabled={isTyping || isSearching || !isConnected || !sessionId}
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
    </div>
  );
};