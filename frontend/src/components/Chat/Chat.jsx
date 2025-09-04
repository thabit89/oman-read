import React, { useState, useRef, useEffect } from 'react';
import { Send, BookOpen, MessageCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ScrollArea } from '../ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { mockChatData } from '../../data/mock';

export const Chat = () => {
  const [messages, setMessages] = useState(mockChatData.messages);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollAreaRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: newMessage,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        text: 'أهلاً وسهلاً! أنا غسان، مساعدك الأدبي العُماني الذكي. سأكون سعيداً بمساعدتك في استكشاف الأدب العُماني الغني والإجابة على أسئلتك حول الشعر والرواية والقصص القصيرة والمسرحيات.',
        sender: 'ghassan',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
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
          
          {isTyping && (
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
              disabled={isTyping}
            />
          </div>
          <Button 
            onClick={handleSendMessage}
            disabled={!newMessage.trim() || isTyping}
            className="h-12 w-12 bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg transition-all duration-200 rounded-xl"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
};