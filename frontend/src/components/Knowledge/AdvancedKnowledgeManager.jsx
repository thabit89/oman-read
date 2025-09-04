import React, { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { 
  BookOpen, Database, Search, TrendingUp, Users, 
  FileText, Upload, Download, CheckCircle, AlertCircle 
} from 'lucide-react';

export const AdvancedKnowledgeManager = () => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  
  // نماذج البيانات
  const [authorForm, setAuthorForm] = useState({
    full_name: '',
    biography: '',
    birth_date: '',
    birth_place: '',
    main_genres: [],
    influences: '',
    literary_periods: ''
  });
  
  const [workForm, setWorkForm] = useState({
    title: '',
    author_id: '',
    publication_year: '',
    category: 'شعر',
    style: 'معاصر',
    main_theme: '',
    summary: '',
    text_content: ''
  });
  
  const [searchResults, setSearchResults] = useState([]);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/rag/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('خطأ في جلب الإحصائيات:', error);
    }
  };

  const handleAutoCollect = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/collect/simple`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.collection_completed) {
        setMessage(`تم جمع ${result.total_sources_found} مصدر من ${result.authors_processed} مؤلف بنجاح!`);
        setMessageType('success');
      } else {
        setMessage(`خطأ في الجمع: ${result.error || 'خطأ غير معروف'}`);
        setMessageType('error');
      }
    } catch (error) {
      setMessage(`خطأ في الاتصال: ${error.message}`);
      setMessageType('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSemanticSearch = async (query) => {
    if (!query.trim()) return;
    
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/search/semantic?query=${encodeURIComponent(query)}&limit=10`
      );
      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('خطأ في البحث الدلالي:', error);
    }
  };

  const handleAddAuthor = async () => {
    setIsLoading(true);
    try {
      const payload = {
        ...authorForm,
        main_genres: authorForm.main_genres,
        influences: authorForm.influences.split(',').map(i => i.trim()).filter(i => i),
        literary_periods: authorForm.literary_periods.split(',').map(p => p.trim()).filter(p => p)
      };

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/authors/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      
      if (result.success) {
        setMessage(`تم إضافة المؤلف بنجاح! معرف التضمين: ${result.embedding_id}`);
        setMessageType('success');
        setAuthorForm({
          full_name: '', biography: '', birth_date: '', birth_place: '',
          main_genres: [], influences: '', literary_periods: ''
        });
        fetchStats();
      } else {
        setMessage(`خطأ: ${result.error}`);
        setMessageType('error');
      }
    } catch (error) {
      setMessage(`خطأ: ${error.message}`);
      setMessageType('error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <Database className="h-12 w-12 text-blue-600 mr-3" />
            <h1 className="text-4xl font-bold text-blue-800">نظام RAG المتقدم لغسان</h1>
          </div>
          <p className="text-blue-700 text-lg">
            قاعدة معرفة شاملة للأدب العُماني مع البحث الدلالي والتضمين المتجه
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

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center text-sm font-medium">
                  <Users className="h-4 w-4 mr-2 text-blue-600" />
                  المؤلفون
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">{stats.authors_count || 0}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center text-sm font-medium">
                  <BookOpen className="h-4 w-4 mr-2 text-green-600" />
                  الأعمال الأدبية
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{stats.works_count || 0}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center text-sm font-medium">
                  <FileText className="h-4 w-4 mr-2 text-purple-600" />
                  المصادر الأكاديمية
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-600">{stats.sources_count || 0}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center text-sm font-medium">
                  <TrendingUp className="h-4 w-4 mr-2 text-orange-600" />
                  التضمينات المتجهة
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {stats.embeddings?.total_embeddings || 0}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <Tabs defaultValue="collect" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="collect">جمع المصادر</TabsTrigger>
            <TabsTrigger value="authors">إدارة المؤلفين</TabsTrigger>
            <TabsTrigger value="works">إدارة الأعمال</TabsTrigger>
            <TabsTrigger value="search">البحث المتقدم</TabsTrigger>
          </TabsList>

          {/* جمع المصادر التلقائي */}
          <TabsContent value="collect" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-right">جمع المصادر التلقائي</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-right text-gray-600">
                  <p>سيقوم النظام بجمع:</p>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li>أبحاث أكاديمية من الجامعات العُمانية</li>
                    <li>مقابلات مع الأدباء من المواقع الإخبارية</li>
                    <li>مقالات من المجلات الأدبية العربية</li>
                    <li>معلومات الكتب والدواوين المنشورة</li>
                  </ul>
                </div>
                
                <Button 
                  onClick={handleAutoCollect}
                  disabled={isLoading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {isLoading ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      جاري الجمع...
                    </div>
                  ) : (
                    <div className="flex items-center">
                      <Download className="h-4 w-4 ml-2" />
                      بدء الجمع التلقائي للمصادر
                    </div>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* إدارة المؤلفين */}
          <TabsContent value="authors" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-right">إضافة مؤلف محقق</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="text-right">
                    <label className="block text-gray-700 font-medium mb-2">الاسم الكامل *</label>
                    <Input
                      value={authorForm.full_name}
                      onChange={(e) => setAuthorForm({...authorForm, full_name: e.target.value})}
                      placeholder="الاسم الكامل للمؤلف..."
                      className="text-right"
                      style={{ direction: 'rtl' }}
                    />
                  </div>

                  <div className="text-right">
                    <label className="block text-gray-700 font-medium mb-2">تاريخ الميلاد</label>
                    <Input
                      value={authorForm.birth_date}
                      onChange={(e) => setAuthorForm({...authorForm, birth_date: e.target.value})}
                      placeholder="1956 أو غير محدد..."
                      className="text-right"
                      style={{ direction: 'rtl' }}
                    />
                  </div>

                  <div className="text-right">
                    <label className="block text-gray-700 font-medium mb-2">مكان الميلاد</label>
                    <Input
                      value={authorForm.birth_place}
                      onChange={(e) => setAuthorForm({...authorForm, birth_place: e.target.value})}
                      placeholder="مسقط، نزوى، صحار..."
                      className="text-right"
                      style={{ direction: 'rtl' }}
                    />
                  </div>

                  <div className="text-right">
                    <label className="block text-gray-700 font-medium mb-2">التأثيرات الأدبية</label>
                    <Input
                      value={authorForm.influences}
                      onChange={(e) => setAuthorForm({...authorForm, influences: e.target.value})}
                      placeholder="أبو تمام، المتنبي، شعراء المهجر (مفصولة بفاصلة)"
                      className="text-right"
                      style={{ direction: 'rtl' }}
                    />
                  </div>
                </div>

                <div className="text-right">
                  <label className="block text-gray-700 font-medium mb-2">السيرة الذاتية *</label>
                  <Textarea
                    value={authorForm.biography}
                    onChange={(e) => setAuthorForm({...authorForm, biography: e.target.value})}
                    placeholder="سيرة ذاتية مفصلة ومحققة للمؤلف..."
                    className="text-right min-h-32"
                    style={{ direction: 'rtl' }}
                  />
                </div>

                <Button
                  onClick={handleAddAuthor}
                  disabled={isLoading || !authorForm.full_name || !authorForm.biography}
                  className="w-full bg-green-600 hover:bg-green-700 text-white"
                >
                  <Upload className="h-4 w-4 ml-2" />
                  إضافة المؤلف المحقق
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* البحث المتقدم */}
          <TabsContent value="search" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-right">البحث الدلالي المتقدم</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-3">
                  <Input
                    placeholder="ابحث في قاعدة المعرفة..."
                    className="text-right"
                    style={{ direction: 'rtl' }}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleSemanticSearch(e.target.value);
                      }
                    }}
                  />
                  <Button
                    onClick={() => {
                      const input = document.querySelector('input[placeholder*="ابحث في قاعدة المعرفة"]');
                      if (input) handleSemanticSearch(input.value);
                    }}
                    className="bg-purple-600 hover:bg-purple-700 text-white"
                  >
                    <Search className="h-4 w-4" />
                  </Button>
                </div>

                {/* نتائج البحث */}
                {searchResults.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-right font-semibold text-gray-800">نتائج البحث الدلالي:</h3>
                    {searchResults.map((result, index) => (
                      <Card key={index} className="border-purple-200">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start mb-2">
                            <Badge variant="outline">{result.content_type}</Badge>
                            <div className="text-right">
                              <div className="text-sm font-semibold">
                                درجة التشابه: {(result.similarity_score * 100).toFixed(1)}%
                              </div>
                            </div>
                          </div>
                          <p className="text-right text-sm text-gray-600 leading-relaxed">
                            {result.text_content.substring(0, 200)}...
                          </p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* إدارة الأعمال */}
          <TabsContent value="works" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-right">إضافة عمل أدبي محقق</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="text-right">
                    <label className="block text-gray-700 font-medium mb-2">عنوان العمل *</label>
                    <Input
                      value={workForm.title}
                      onChange={(e) => setWorkForm({...workForm, title: e.target.value})}
                      placeholder="عنوان الكتاب أو الديوان..."
                      className="text-right"
                      style={{ direction: 'rtl' }}
                    />
                  </div>

                  <div className="text-right">
                    <label className="block text-gray-700 font-medium mb-2">سنة النشر</label>
                    <Input
                      value={workForm.publication_year}
                      onChange={(e) => setWorkForm({...workForm, publication_year: e.target.value})}
                      placeholder="2024 أو 1445هـ..."
                      className="text-right"
                      style={{ direction: 'rtl' }}
                    />
                  </div>

                  <div className="text-right">
                    <label className="block text-gray-700 font-medium mb-2">الفئة الأدبية</label>
                    <Select
                      value={workForm.category}
                      onValueChange={(value) => setWorkForm({...workForm, category: value})}
                    >
                      <SelectTrigger className="text-right">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="شعر">شعر</SelectItem>
                        <SelectItem value="رواية">رواية</SelectItem>
                        <SelectItem value="قصة قصيرة">قصة قصيرة</SelectItem>
                        <SelectItem value="مسرحية">مسرحية</SelectItem>
                        <SelectItem value="نقد أدبي">نقد أدبي</SelectItem>
                        <SelectItem value="أدب شعبي">أدب شعبي</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="text-right">
                    <label className="block text-gray-700 font-medium mb-2">الأسلوب الأدبي</label>
                    <Select
                      value={workForm.style}
                      onValueChange={(value) => setWorkForm({...workForm, style: value})}
                    >
                      <SelectTrigger className="text-right">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="تقليدي">تقليدي</SelectItem>
                        <SelectItem value="حداثي">حداثي</SelectItem>
                        <SelectItem value="معاصر">معاصر</SelectItem>
                        <SelectItem value="تجريبي">تجريبي</SelectItem>
                        <SelectItem value="رمزي">رمزي</SelectItem>
                        <SelectItem value="واقعي">واقعي</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="text-right">
                  <label className="block text-gray-700 font-medium mb-2">الموضوع الرئيسي</label>
                  <Input
                    value={workForm.main_theme}
                    onChange={(e) => setWorkForm({...workForm, main_theme: e.target.value})}
                    placeholder="الحب، الوطن، الطبيعة، التراث..."
                    className="text-right"
                    style={{ direction: 'rtl' }}
                  />
                </div>

                <div className="text-right">
                  <label className="block text-gray-700 font-medium mb-2">ملخص العمل *</label>
                  <Textarea
                    value={workForm.summary}
                    onChange={(e) => setWorkForm({...workForm, summary: e.target.value})}
                    placeholder="ملخص مفصل ودقيق للعمل الأدبي..."
                    className="text-right min-h-24"
                    style={{ direction: 'rtl' }}
                  />
                </div>

                <Button
                  disabled={isLoading || !workForm.title || !workForm.summary}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white"
                >
                  <Upload className="h-4 w-4 ml-2" />
                  إضافة العمل الأدبي
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Recent Queries */}
        {stats?.recent_queries && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="text-right">آخر الاستعلامات</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {stats.recent_queries.map((query, index) => (
                  <div key={index} className="text-right p-2 bg-gray-50 rounded text-sm">
                    {query}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};