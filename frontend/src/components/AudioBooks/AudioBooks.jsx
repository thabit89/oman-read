import React from 'react';
import { Music, ExternalLink, Radio, BookOpen, Headphones } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { GlobalHeader } from '../Layout/GlobalHeader';

export const AudioBooks = () => {
  const audioResources = [
    {
      id: 1,
      title: 'الكتب الصوتية على منصة عين',
      description: 'مجموعة متنوعة من الكتب الصوتية العربية والعُمانية',
      url: 'https://ayn.om/audiobooks',
      type: 'مكتبة صوتية',
      icon: '📚',
      category: 'كتب'
    },
    {
      id: 2,
      title: 'كتاب أعجبني مع سليمان المعمري',
      description: 'برنامج إذاعي يناقش الكتب والأعمال الأدبية المميزة',
      url: 'https://ayn.om/radio_show/217124/%D9%83%D8%AA%D8%A7%D8%A8-%D8%A3%D8%B9%D8%AC%D8%A8%D9%86%D9%8A',
      type: 'برنامج إذاعي',
      icon: '🎙️',
      category: 'برنامج'
    },
    {
      id: 3,
      title: 'إصدارات عمانية مع أمل السعيدي',
      description: 'برنامج مخصص للإصدارات والأعمال الأدبية العُمانية الجديدة',
      url: 'https://ayn.om/radio_show/237773/%D8%A5%D8%B5%D8%AF%D8%A7%D8%B1%D8%A7%D8%AA-%D8%B9%D9%85%D8%A7%D9%86%D9%8A%D8%A9',
      type: 'برنامج إذاعي',
      icon: '📻',
      category: 'برنامج'
    },
    {
      id: 4,
      title: 'منصة ستوري تل',
      description: 'منصة عالمية للكتب الصوتية بمحتوى عربي وعالمي متنوع',
      url: 'https://www.storytel.com/ae/audiobooks',
      type: 'منصة عالمية',
      icon: '🌍',
      category: 'منصة'
    },
    {
      id: 5,
      title: 'منصة اقرألي',
      description: 'مكتبة صوتية عربية شاملة بمحتوى أدبي وثقافي متميز',
      url: 'https://iqraaly.com/home',
      type: 'منصة عربية',
      icon: '🎧',
      category: 'منصة'
    }
  ];

  const handleOpenLink = (url) => {
    window.open(url, '_blank');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <GlobalHeader currentPage="audiobooks" />
      
      <div className="p-6">
        <div className="max-w-6xl mx-auto">
        
          {/* Header */}
          <div className="mb-8 text-center">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-700 to-blue-700 bg-clip-text text-transparent mb-4">
              الكتب والبرامج المسموعة
            </h1>
            <p className="text-gray-700 text-lg">
              استكشف عالم الكتب الصوتية والبرامج الإذاعية العُمانية والعربية
            </p>
          </div>

          {/* Resources Grid */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {audioResources.map((resource) => (
              <Card 
                key={resource.id} 
                className="group hover:shadow-xl transition-all duration-300 cursor-pointer border-purple-100 hover:border-purple-300"
                onClick={() => handleOpenLink(resource.url)}
              >
                <CardHeader>
                  <CardTitle className="text-right flex items-center justify-between">
                    <ExternalLink className="h-5 w-5 text-purple-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{resource.icon}</span>
                      <div className="text-right">
                        <h3 className="text-lg font-bold text-gray-900">{resource.title}</h3>
                        <Badge variant="outline" className="mt-1 text-purple-700 border-purple-200">
                          {resource.type}
                        </Badge>
                      </div>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 text-sm leading-relaxed mb-4 text-right">
                    {resource.description}
                  </p>
                  
                  <Button 
                    className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenLink(resource.url);
                    }}
                  >
                    <ExternalLink className="h-4 w-4 ml-2" />
                    زيارة {resource.category === 'كتب' ? 'المكتبة' : resource.category === 'برنامج' ? 'البرنامج' : 'المنصة'}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Additional Info */}
          <Card className="mt-8 bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
            <CardContent className="p-6 text-center">
              <Headphones className="h-12 w-12 text-purple-600 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-purple-800 mb-2">نصائح للاستفادة القصوى</h3>
              <div className="text-right text-gray-700 space-y-2 max-w-2xl mx-auto">
                <p>• استمع للكتب الصوتية أثناء المشي أو ممارسة الرياضة</p>
                <p>• تابع البرامج الإذاعية لاكتشاف كتب جديدة</p>
                <p>• استخدم المنصات العالمية لتنويع مصادر المعرفة</p>
                <p>• شارك ما تعجبك من كتب مع الأصدقاء</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};