import React from 'react';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Badge } from '../ui/badge';
import { 
  BookOpen, Brain, Music, Mail, MessageCircle, Sparkles, Home
} from 'lucide-react';

export const GlobalHeader = ({ currentPage = 'chat' }) => {
  return (
    <div className="bg-white/70 backdrop-blur-xl border-b border-white/30 shadow-lg sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 py-4">
        <div className="flex items-center gap-4">
          
          {/* غسان Avatar and Title */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full blur animate-pulse"></div>
              <Avatar className="relative h-14 w-14 ring-2 ring-emerald-200 shadow-lg hover:scale-105 transition-all duration-200">
                <AvatarImage 
                  src={`${process.env.REACT_APP_BACKEND_URL}/uploads/ghassan-avatar.png`}
                  alt="غسان - المساعد الأدبي العُماني" 
                  className="object-cover"
                />
                <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-teal-500 text-white font-bold text-lg">
                  غ
                </AvatarFallback>
              </Avatar>
            </div>

            <div>
              <div className="flex items-center gap-2 mb-1">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-700 to-teal-700 bg-clip-text text-transparent">
                  غسان
                </h1>
                <Badge className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white border-none">
                  <Sparkles className="h-3 w-3 mr-1" />
                  ذكي ومتطور
                </Badge>
              </div>
              <p className="text-sm text-gray-600">
                🇴🇲 المساعد الأدبي العُماني المتخصص
              </p>
            </div>
          </div>

          {/* Navigation */}
          <div className="ml-auto flex items-center gap-2">
            <Button
              variant={currentPage === 'chat' ? 'default' : 'ghost'}
              size="sm"
              asChild
              className={currentPage === 'chat' 
                ? 'bg-emerald-600 text-white' 
                : 'text-emerald-600 hover:bg-emerald-50'
              }
            >
              <a href="/" className="flex items-center gap-2">
                <MessageCircle className="h-4 w-4" />
                <span className="hidden md:inline">الدردشة</span>
              </a>
            </Button>
            
            <Button
              variant={currentPage === 'audiobooks' ? 'default' : 'ghost'}
              size="sm"
              asChild
              className={currentPage === 'audiobooks' 
                ? 'bg-purple-600 text-white' 
                : 'text-purple-600 hover:bg-purple-50'
              }
            >
              <a href="/audiobooks" className="flex items-center gap-2">
                <Music className="h-4 w-4" />
                <span className="hidden md:inline">الصوتيات</span>
              </a>
            </Button>
            
            <Button
              variant={currentPage === 'contact' ? 'default' : 'ghost'}
              size="sm"
              asChild
              className={currentPage === 'contact' 
                ? 'bg-orange-600 text-white' 
                : 'text-orange-600 hover:bg-orange-50'
              }
            >
              <a href="/contact" className="flex items-center gap-2">
                <Mail className="h-4 w-4" />
                <span className="hidden md:inline">التواصل</span>
              </a>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};