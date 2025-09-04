import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { BookOpen, Upload, CheckCircle, AlertCircle } from 'lucide-react';
import { ChatService } from '../../services/chatService';

export const KnowledgeManager = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    source_type: 'article',
    author: '',
    publication_date: '',
    reliability_score: 0.8,
    tags: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      const payload = {
        ...formData,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        reliability_score: parseFloat(formData.reliability_score)
      };

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/knowledge/add-source`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      // تحقق من حالة الاستجابة
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      // تحقق من وجود النتيجة
      if (!result) {
        throw new Error('لم يتم الحصول على استجابة من الخادم');
      }

      if (result.success) {
        setMessage(`تم إضافة المصدر بنجاح! تم إنشاء ${result.knowledge_entries || 'عدة'} مدخل معرفي.`);
        setMessageType('success');
        
        // إعادة تعيين النموذج
        setFormData({
          title: '',
          content: '',
          source_type: 'article',
          author: '',
          publication_date: '',
          reliability_score: 0.8,
          tags: ''
        });
      } else {
        setMessage(`خطأ: ${result.message || result.error || 'خطأ غير معروف'}`);
        setMessageType('error');
      }
    } catch (error) {
      setMessage(`خطأ في الاتصال: ${error.message}`);
      setMessageType('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <BookOpen className="h-12 w-12 text-emerald-600 mr-3" />
            <h1 className="text-4xl font-bold text-emerald-800">إدارة مصادر غسان</h1>
          </div>
          <p className="text-emerald-700 text-lg">
            إضافة مصادر جديدة لقاعدة المعرفة الأدبية العُمانية
          </p>
        </div>

        {/* Message */}
        {message && (
          <Card className={`mb-6 ${messageType === 'success' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
            <CardContent className="p-4">
              <div className="flex items-center">
                {messageType === 'success' ? (
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
                )}
                <p className={messageType === 'success' ? 'text-green-800' : 'text-red-800'}>
                  {message}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle className="text-right text-emerald-800">إضافة مصدر جديد</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Title */}
              <div>
                <label className="block text-right text-emerald-700 font-medium mb-2">
                  العنوان *
                </label>
                <Input
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  placeholder="عنوان المصدر..."
                  className="text-right"
                  style={{ direction: 'rtl' }}
                  required
                />
              </div>

              {/* Content */}
              <div>
                <label className="block text-right text-emerald-700 font-medium mb-2">
                  المحتوى *
                </label>
                <Textarea
                  value={formData.content}
                  onChange={(e) => handleInputChange('content', e.target.value)}
                  placeholder="محتوى المصدر الأدبي..."
                  className="text-right min-h-40"
                  style={{ direction: 'rtl' }}
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Source Type */}
                <div>
                  <label className="block text-right text-emerald-700 font-medium mb-2">
                    نوع المصدر
                  </label>
                  <Select
                    value={formData.source_type}
                    onValueChange={(value) => handleInputChange('source_type', value)}
                  >
                    <SelectTrigger className="text-right">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="article">مقال</SelectItem>
                      <SelectItem value="book">كتاب</SelectItem>
                      <SelectItem value="poem">قصيدة</SelectItem>
                      <SelectItem value="biography">سيرة ذاتية</SelectItem>
                      <SelectItem value="research">بحث أكاديمي</SelectItem>
                      <SelectItem value="novel">رواية</SelectItem>
                      <SelectItem value="story">قصة</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Author */}
                <div>
                  <label className="block text-right text-emerald-700 font-medium mb-2">
                    المؤلف
                  </label>
                  <Input
                    value={formData.author}
                    onChange={(e) => handleInputChange('author', e.target.value)}
                    placeholder="اسم المؤلف..."
                    className="text-right"
                    style={{ direction: 'rtl' }}
                  />
                </div>

                {/* Publication Date */}
                <div>
                  <label className="block text-right text-emerald-700 font-medium mb-2">
                    تاريخ النشر
                  </label>
                  <Input
                    value={formData.publication_date}
                    onChange={(e) => handleInputChange('publication_date', e.target.value)}
                    placeholder="2024 أو 1445هـ..."
                    className="text-right"
                    style={{ direction: 'rtl' }}
                  />
                </div>

                {/* Reliability Score */}
                <div>
                  <label className="block text-right text-emerald-700 font-medium mb-2">
                    درجة الموثوقية (0.1 - 1.0)
                  </label>
                  <Input
                    type="number"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    value={formData.reliability_score}
                    onChange={(e) => handleInputChange('reliability_score', e.target.value)}
                    className="text-right"
                  />
                </div>
              </div>

              {/* Tags */}
              <div>
                <label className="block text-right text-emerald-700 font-medium mb-2">
                  الكلمات المفتاحية
                </label>
                <Input
                  value={formData.tags}
                  onChange={(e) => handleInputChange('tags', e.target.value)}
                  placeholder="شعر, أدب عُماني, سيف الرحبي (مفصولة بفاصلة)"
                  className="text-right"
                  style={{ direction: 'rtl' }}
                />
              </div>

              {/* Submit Button */}
              <div className="text-center">
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-3 text-lg"
                >
                  {isLoading ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      جاري الحفظ...
                    </div>
                  ) : (
                    <div className="flex items-center">
                      <Upload className="h-5 w-5 ml-2" />
                      إضافة المصدر
                    </div>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};