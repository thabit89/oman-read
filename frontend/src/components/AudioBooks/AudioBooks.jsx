import React, { useState, useRef } from 'react';
import { Upload, Play, Pause, Volume2, Search, BookOpen, Music, Clock, Download, Tag } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';

export const AudioBooks = () => {
  const [audioBooks, setAudioBooks] = useState([
    {
      id: 1,
      title: 'ديوان سيف الرحبي - مختارات شعرية',
      author: 'سيف الرحبي',
      category: 'شعر',
      duration: '45:30',
      narrator: 'صوت المؤلف',
      description: 'مختارات من أجمل قصائد سيف الرحبي بصوت المؤلف نفسه'
    },
    {
      id: 2,
      title: 'قصص من التراث العُماني',
      author: 'مجموعة مؤلفين',
      category: 'أدب شعبي',
      duration: '32:15',
      narrator: 'راوي تراثي',
      description: 'مجموعة من الحكايات والقصص الشعبية العُمانية التراثية'
    }
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [currentlyPlaying, setCurrentlyPlaying] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);

  const categories = [
    { value: 'all', label: 'جميع الفئات' },
    { value: 'شعر', label: 'شعر' },
    { value: 'رواية', label: 'رواية' },
    { value: 'قصة قصيرة', label: 'قصة قصيرة' },
    { value: 'نقد أدبي', label: 'نقد أدبي' },
    { value: 'أدب شعبي', label: 'أدب شعبي' }
  ];

  const filteredBooks = audioBooks.filter(book => {
    const matchesSearch = book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         book.author.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || book.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handlePlayPause = (bookId) => {
    setCurrentlyPlaying(currentlyPlaying === bookId && isPlaying ? null : bookId);
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <Music className="h-12 w-12 text-purple-600 mr-3" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-700 to-blue-700 bg-clip-text text-transparent">
              الكتب الصوتية العُمانية
            </h1>
          </div>
          <p className="text-gray-700 text-lg">
            استمع لأجمل الأعمال الأدبية العُمانية
          </p>
        </div>

        {/* Search and Filter */}
        <div className="flex gap-4 mb-8 bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute right-3 top-3 h-5 w-5 text-gray-400" />
              <Input
                placeholder="ابحث في الكتب الصوتية..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="text-right pr-12 h-12 rounded-xl"
                style={{ direction: 'rtl' }}
              />
            </div>
          </div>
          
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-48 h-12 rounded-xl">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {categories.map(cat => (
                <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Button
            onClick={() => setShowUploadForm(!showUploadForm)}
            className="h-12 bg-purple-600 hover:bg-purple-700 text-white px-6 rounded-xl"
          >
            <Upload className="h-5 w-5 ml-2" />
            رفع كتاب صوتي
          </Button>
        </div>

        {/* Audio Books Grid */}
        <div className="grid gap-6">
          {filteredBooks.map((book) => (
            <Card key={book.id} className="overflow-hidden hover:shadow-xl transition-all duration-300">
              <CardContent className="p-6">
                <div className="flex items-start gap-6">
                  
                  {/* Book Cover */}
                  <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center shadow-lg">
                    <BookOpen className="h-8 w-8 text-white" />
                  </div>
                  
                  {/* Book Info */}
                  <div className="flex-1 text-right">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex gap-2">
                        <Badge variant="outline" className="text-purple-700 border-purple-200">
                          <Tag className="h-3 w-3 mr-1" />
                          {book.category}
                        </Badge>
                        <Badge variant="outline" className="text-blue-700 border-blue-200">
                          <Clock className="h-3 w-3 mr-1" />
                          {book.duration}
                        </Badge>
                      </div>
                    </div>
                    
                    <h3 className="text-xl font-bold text-gray-900 mb-2">{book.title}</h3>
                    <p className="text-purple-700 font-medium mb-2">المؤلف: {book.author}</p>
                    <p className="text-gray-600 text-sm mb-2">الراوي: {book.narrator}</p>
                    <p className="text-gray-600 text-sm leading-relaxed mb-4">{book.description}</p>
                    
                    {/* Audio Controls */}
                    <div className="flex items-center gap-4">
                      <Button
                        onClick={() => handlePlayPause(book.id)}
                        className={`${
                          currentlyPlaying === book.id && isPlaying
                            ? 'bg-red-500 hover:bg-red-600'
                            : 'bg-green-500 hover:bg-green-600'
                        } text-white`}
                      >
                        {currentlyPlaying === book.id && isPlaying ? (
                          <>
                            <Pause className="h-4 w-4 ml-1" />
                            إيقاف
                          </>
                        ) : (
                          <>
                            <Play className="h-4 w-4 ml-1" />
                            تشغيل
                          </>
                        )}
                      </Button>
                      
                      <div className="flex items-center gap-2 flex-1">
                        <Volume2 className="h-4 w-4 text-gray-500" />
                        <Progress value={currentlyPlaying === book.id ? 30 : 0} className="flex-1" />
                        <span className="text-sm text-gray-500">{book.duration}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Back to Chat */}
        <div className="text-center mt-8">
          <Button asChild variant="outline" className="bg-white/80 backdrop-blur-sm">
            <a href="/">العودة للدردشة مع غسان</a>
          </Button>
        </div>
      </div>
    </div>
  );
};