import React, { useState, useRef, useEffect } from 'react';
import { Send, BookOpen, Search, Globe, Sparkles, Brain } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ScrollArea } from '../ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { ChatService } from '../../services/chatService';

export const EnhancedChat = () => {
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
        const connectionTest = await ChatService.testConnection();
        if (connectionTest.success) {
          setIsConnected(true);
          
          const sessionResult = await ChatService.createNewSession();
          if (sessionResult.success) {
            setSessionId(sessionResult.data.session_id);
            
            const welcomeMessage = {
              id: 'welcome_' + Date.now(),
              text: 'أهلاً وسهلاً! أنا غسان، مساعدك الأدبي العُماني الذكي. أستطيع مساعدتك في الأدب العُماني، التحليل النحوي والبلاغي، والبحث في المصادر الموثوقة.',
              sender: 'ghassan',
              timestamp: new Date().toISOString(),
              hasWebSearch: false,
              isWelcome: true
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
      const response = await ChatService.sendMessage(messageText, sessionId);
      
      if (response.success) {
        const aiResponse = {
          id: response.data.message_id,
          text: response.data.text,
          sender: 'ghassan',
          timestamp: response.data.timestamp,
          hasWebSearch: response.data.has_web_search,
          modelUsed: response.data.model_used,
          reliabilityScore: response.data.reliability_score,
          confidenceLevel: response.data.confidence_level
        };
        
        setMessages(prev => [...prev, aiResponse]);
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          text: 'عذراً، حدث خطأ في معالجة رسالتك. أرجو المحاولة مرة أخرى.',
          sender: 'ghassan',
          timestamp: new Date().toISOString(),
          hasWebSearch: false,
          isError: true
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
        hasWebSearch: false,
        isError: true
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/50 to-indigo-50">
      
      {/* Floating Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-32 h-32 bg-gradient-to-br from-emerald-200/30 to-teal-200/30 rounded-full blur-2xl animate-pulse"></div>
        <div className="absolute top-1/3 right-16 w-48 h-48 bg-gradient-to-br from-blue-200/20 to-indigo-200/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-40 h-40 bg-gradient-to-br from-purple-200/25 to-pink-200/25 rounded-full blur-2xl animate-pulse delay-2000"></div>
      </div>

      {/* Main Chat Container */}
      <div className="relative z-10 max-w-5xl mx-auto h-screen flex flex-col">
        
        {/* Glassmorphism Header */}
        <div className="bg-white/70 backdrop-blur-xl border-b border-white/30 shadow-lg sticky top-0 z-20">
          <div className="px-6 py-5">
            <div className="flex items-center gap-4">
              
              {/* Enhanced Avatar */}
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 rounded-full blur-md group-hover:blur-lg transition-all duration-300 animate-pulse"></div>
                <Avatar className="relative h-16 w-16 ring-2 ring-white/60 shadow-xl transition-all duration-300 group-hover:scale-105">
                  <AvatarImage src="/ghassan-avatar.jpg" alt="غسان" className="object-cover" />
                  <AvatarFallback className="bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 text-white font-bold text-xl">
                    غ
                  </AvatarFallback>
                </Avatar>
              </div>

              {/* Title Section */}
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-700 via-teal-600 to-cyan-600 bg-clip-text text-transparent">
                    غسان
                  </h1>
                  <Badge className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white border-none shadow-md">
                    <Sparkles className="h-3 w-3 mr-1" />
                    مساعد ذكي
                  </Badge>
                  {isConnected && (
                    <Badge variant="outline" className="border-green-300 text-green-700 bg-green-50">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></div>
                      متصل
                    </Badge>
                  )}
                </div>
                <p className="text-gray-600 text-base">
                  🇴🇲 المساعد الأدبي العُماني المتخصص • مدعوم بـ Claude + GPT-4o + Tavily
                </p>
              </div>

              {/* Navigation Buttons */}
              <div className="hidden md:flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  asChild
                  className="text-emerald-600 hover:bg-emerald-50 hover:text-emerald-700 transition-all duration-200"
                >
                  <a href="/knowledge" className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4" />
                    <span className="text-xs">المصادر</span>
                  </a>
                </Button>
                
                <Button
                  variant="ghost"
                  size="sm"
                  asChild
                  className="text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700 transition-all duration-200"
                >
                  <a href="/advanced" className="flex items-center gap-2">
                    <Brain className="h-4 w-4" />
                    <span className="text-xs">متقدم</span>
                  </a>
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Messages Area */}
        <ScrollArea className="flex-1 px-6 py-6" ref={scrollAreaRef}>
          <div className="space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex items-end gap-3 max-w-xs sm:max-w-md lg:max-w-2xl ${message.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                  
                  {/* Ghassan Avatar for AI messages */}
                  {message.sender === 'ghassan' && (
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full blur-sm group-hover:blur-md transition-all duration-300"></div>
                      <Avatar className="relative h-10 w-10 ring-2 ring-white/60 shadow-lg transition-all duration-200 group-hover:scale-105">
                        <AvatarImage src="/ghassan-avatar.jpg" alt="غسان" />
                        <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-teal-500 text-white text-sm font-semibold">
                          غ
                        </AvatarFallback>
                      </Avatar>
                    </div>
                  )}

                  {/* Message Card */}
                  <Card
                    className={`transition-all duration-300 hover:shadow-lg hover:-translate-y-1 ${
                      message.sender === 'user'
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white border-none shadow-lg'
                        : message.isWelcome
                        ? 'bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200/50 shadow-md'
                        : message.isError
                        ? 'bg-gradient-to-br from-red-50 to-pink-50 border border-red-200/50 shadow-md'
                        : 'bg-white/90 backdrop-blur-sm border border-gray-200/50 shadow-md'
                    }`}
                  >
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        
                        {/* Message Content */}
                        <p 
                          className={`text-sm leading-relaxed whitespace-pre-wrap ${
                            message.sender === 'user' 
                              ? 'text-white' 
                              : message.isWelcome 
                              ? 'text-blue-800'
                              : message.isError
                              ? 'text-red-800'
                              : 'text-gray-800'
                          }`}
                          style={{ direction: 'rtl', textAlign: 'right' }}
                        >
                          {message.text}
                        </p>

                        {/* Message Metadata */}
                        {message.sender === 'ghassan' && !message.isWelcome && (
                          <div className="flex flex-wrap gap-2 justify-end">
                            {message.hasWebSearch && (
                              <Badge variant="outline" className="text-xs border-emerald-200 text-emerald-700 bg-emerald-50">
                                <Globe className="h-3 w-3 mr-1" />
                                بحث متقدم
                              </Badge>
                            )}
                            {message.modelUsed && (
                              <Badge variant="outline" className="text-xs border-blue-200 text-blue-700 bg-blue-50">
                                <Brain className="h-3 w-3 mr-1" />
                                {message.modelUsed.includes('claude') ? 'Claude' : 'GPT-4o'}
                              </Badge>
                            )}
                            {message.reliabilityScore && (
                              <Badge 
                                variant="outline" 
                                className={`text-xs ${
                                  message.reliabilityScore > 0.8 
                                    ? 'border-green-200 text-green-700 bg-green-50'
                                    : 'border-yellow-200 text-yellow-700 bg-yellow-50'
                                }`}
                              >
                                <Sparkles className="h-3 w-3 mr-1" />
                                ثقة: {(message.reliabilityScore * 100).toFixed(0)}%
                              </Badge>
                            )}
                          </div>
                        )}

                        {/* Timestamp */}
                        <div className={`text-xs ${
                          message.sender === 'user' ? 'text-emerald-100' : 'text-gray-500'
                        }`} style={{ direction: 'rtl' }}>
                          {new Date(message.timestamp).toLocaleTimeString('ar-SA', { 
                            hour: '2-digit', 
                            minute: '2-digit',
                            hour12: false 
                          })}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            ))}
            
            {/* Searching Indicator */}
            {isSearching && (
              <div className="flex justify-start">
                <div className="flex items-end gap-3 max-w-sm">
                  <div className="relative group">
                    <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full blur-sm animate-pulse"></div>
                    <Avatar className="relative h-10 w-10 ring-2 ring-white/60 shadow-lg">
                      <AvatarImage src="/ghassan-avatar.jpg" alt="غسان" />
                      <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-teal-500 text-white text-sm">
                        غ
                      </AvatarFallback>
                    </Avatar>
                  </div>
                  
                  <Card className="bg-white/95 backdrop-blur-sm border border-blue-200/50 shadow-lg">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <Search className="h-5 w-5 text-blue-500 animate-pulse" />
                        <span className="text-sm text-blue-700 font-medium">يبحث في المصادر الموثوقة...</span>
                        <div className="flex gap-1">
                          <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"></div>
                          <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce delay-100"></div>
                          <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce delay-200"></div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}
            
            {/* Typing Indicator */}
            {isTyping && !isSearching && (
              <div className="flex justify-start">
                <div className="flex items-end gap-3 max-w-sm">
                  <div className="relative group">
                    <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full blur-sm animate-pulse"></div>
                    <Avatar className="relative h-10 w-10 ring-2 ring-white/60 shadow-lg">
                      <AvatarImage src="/ghassan-avatar.jpg" alt="غسان" />
                      <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-teal-500 text-white text-sm">
                        غ
                      </AvatarFallback>
                    </Avatar>
                  </div>
                  
                  <Card className="bg-white/95 backdrop-blur-sm border border-emerald-200/50 shadow-lg">
                    <CardContent className="p-3">
                      <div className="flex gap-2">
                        <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-bounce"></div>
                        <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-bounce delay-100"></div>
                        <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-bounce delay-200"></div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Enhanced Message Input */}
        <div className="bg-white/80 backdrop-blur-xl border-t border-white/30 shadow-lg sticky bottom-0 p-6">
          <div className="flex gap-4 items-end max-w-4xl mx-auto">
            <div className="flex-1 relative group">
              
              {/* Input with Glassmorphism Effect */}
              <div className="relative">
                <Input
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="اكتب سؤالك حول الأدب العُماني هنا..."
                  className="h-14 pr-6 pl-4 text-right border-2 border-emerald-200/50 focus:ring-2 focus:ring-emerald-400/50 focus:border-emerald-400 rounded-2xl px-6 py-4 shadow-lg bg-white/90 backdrop-blur-sm text-gray-800 placeholder:text-gray-500 transition-all duration-200 hover:shadow-xl focus:shadow-xl"
                  style={{ direction: 'rtl' }}
                  disabled={isTyping || isSearching || !isConnected || !sessionId}
                />
                
                {/* Input Glow Effect */}
                {newMessage && (
                  <div className="absolute inset-0 bg-gradient-to-r from-emerald-400/20 to-teal-400/20 rounded-2xl blur-xl transition-opacity duration-300"></div>
                )}
              </div>
              
              {/* Connection Status */}
              {!isConnected && (
                <div className="absolute top-full left-0 mt-2 text-xs text-red-500 bg-red-50 px-2 py-1 rounded">
                  غير متصل بالخادم
                </div>
              )}
            </div>
            
            {/* Enhanced Send Button */}
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl blur group-hover:blur-md transition-all duration-300"></div>
              <Button 
                onClick={handleSendMessage}
                disabled={!newMessage.trim() || isTyping || isSearching || !isConnected || !sessionId}
                className="relative h-14 w-14 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white shadow-lg transition-all duration-200 rounded-2xl group-hover:scale-105 border-none"
              >
                <Send className="h-6 w-6 group-hover:scale-110 transition-transform duration-200" />
              </Button>
            </div>
          </div>
          
          {/* Quick Actions */}
          <div className="flex gap-2 mt-4 justify-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setNewMessage("أعرب لي: والشمس تشرق على عُمان")}
              className="text-xs text-gray-600 hover:text-emerald-600 hover:bg-emerald-50 transition-all duration-200"
            >
              مثال: تحليل نحوي
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setNewMessage("أخبرني عن الشاعر سيف الرحبي")}
              className="text-xs text-gray-600 hover:text-blue-600 hover:bg-blue-50 transition-all duration-200"
            >
              مثال: بحث عن شاعر
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};