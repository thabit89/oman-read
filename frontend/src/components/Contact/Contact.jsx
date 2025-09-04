import React, { useState } from 'react';
import { Mail, Send, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { GlobalHeader } from '../Layout/GlobalHeader';

export const Contact = () => {
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');
  const [submitStatus, setSubmitStatus] = useState('');

  const handleInputChange = (field, value) => {
    setContactForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // إرسال البيانات للخادم
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/contact/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(contactForm)
      });

      const result = await response.json();

      if (result.success) {
        setSubmitMessage('تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.');
        setSubmitStatus('success');
        setContactForm({ name: '', email: '', subject: '', message: '' });
      } else {
        setSubmitMessage(`خطأ في الإرسال: ${result.error}`);
        setSubmitStatus('error');
      }
    } catch (error) {
      setSubmitMessage('خطأ في الاتصال. يرجى المحاولة لاحقاً.');
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 p-6">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <div className="mb-12 text-center">
          <div className="flex items-center justify-center mb-4">
            <MessageSquare className="h-12 w-12 text-emerald-600 mr-3" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-700 to-teal-700 bg-clip-text text-transparent">
              تواصل معنا
            </h1>
          </div>
          <p className="text-gray-700 text-lg max-w-2xl mx-auto">
            نحن سعداء لتواصلك معنا! سواء كان لديك استفسار عن غسان أو اقتراح لتطوير المشروع، نرحب بجميع رسائلك
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          
          {/* Contact Form */}
          <Card className="shadow-xl bg-white/90 backdrop-blur-sm border-white/50">
            <CardHeader>
              <CardTitle className="text-right text-emerald-800 flex items-center gap-2">
                <Mail className="h-6 w-6" />
                نموذج التواصل
              </CardTitle>
            </CardHeader>
            <CardContent>
              
              {/* Message */}
              {submitMessage && (
                <div className={`p-4 rounded-lg mb-6 text-center ${
                  submitStatus === 'success' 
                    ? 'bg-green-50 text-green-800 border border-green-200' 
                    : 'bg-red-50 text-red-800 border border-red-200'
                }`}>
                  <div className="flex items-center justify-center gap-2">
                    {submitStatus === 'success' ? (
                      <CheckCircle className="h-5 w-5" />
                    ) : (
                      <AlertCircle className="h-5 w-5" />
                    )}
                    {submitMessage}
                  </div>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="text-right">
                    <label className="block text-gray-700 font-medium mb-2">الاسم *</label>
                    <Input
                      value={contactForm.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      placeholder="اسمك الكريم..."
                      className="text-right"
                      style={{ direction: 'rtl' }}
                      required
                    />
                  </div>

                  <div className="text-right">
                    <label className="block text-gray-700 font-medium mb-2">البريد الإلكتروني *</label>
                    <Input
                      type="email"
                      value={contactForm.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      placeholder="your@email.com"
                      required
                    />
                  </div>
                </div>

                <div className="text-right">
                  <label className="block text-gray-700 font-medium mb-2">الموضوع *</label>
                  <Input
                    value={contactForm.subject}
                    onChange={(e) => handleInputChange('subject', e.target.value)}
                    placeholder="موضوع الرسالة..."
                    className="text-right"
                    style={{ direction: 'rtl' }}
                    required
                  />
                </div>

                <div className="text-right">
                  <label className="block text-gray-700 font-medium mb-2">الرسالة *</label>
                  <Textarea
                    value={contactForm.message}
                    onChange={(e) => handleInputChange('message', e.target.value)}
                    placeholder="اكتب رسالتك هنا..."
                    className="text-right min-h-32"
                    style={{ direction: 'rtl' }}
                    required
                  />
                </div>

                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full h-12 bg-emerald-600 hover:bg-emerald-700 text-white text-lg"
                >
                  {isSubmitting ? (
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      جاري الإرسال...
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <Send className="h-5 w-5" />
                      إرسال الرسالة
                    </div>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <div className="space-y-6">
            
            {/* About Ghassan */}
            <Card className="shadow-xl bg-white/90 backdrop-blur-sm border-white/50">
              <CardHeader>
                <CardTitle className="text-right text-emerald-800">عن غسان</CardTitle>
              </CardHeader>
              <CardContent className="text-right space-y-3">
                <p className="text-gray-700 leading-relaxed">
                  غسان هو المساعد الأدبي العُماني الذكي المصمم خصيصاً لخدمة الطلاب والباحثين 
                  والمهتمين بالأدب العُماني. يجمع بين الذكاء الاصطناعي المتقدم والمعرفة 
                  المتخصصة في الأدب والثقافة العُمانية.
                </p>
                
                <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-200">
                  <h4 className="font-semibold text-emerald-800 mb-2">قدرات غسان:</h4>
                  <ul className="text-sm text-emerald-700 space-y-1">
                    <li>• التحليل النحوي والبلاغي الدقيق</li>
                    <li>• البحث في مصادر الأدب العُماني الموثوقة</li>
                    <li>• تطبيق النظريات النقدية الحديثة</li>
                    <li>• توليد نصوص أدبية على الطراز العُماني</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Team Information */}
            <Card className="shadow-xl bg-white/90 backdrop-blur-sm border-white/50">
              <CardHeader>
                <CardTitle className="text-right text-emerald-800">الفريق التطويري</CardTitle>
              </CardHeader>
              <CardContent className="text-right space-y-4">
                <div className="space-y-2">
                  <h4 className="font-semibold text-gray-800">التقنيات المستخدمة:</h4>
                  <div className="flex flex-wrap gap-2 justify-end">
                    <Badge className="bg-blue-100 text-blue-800">OpenAI GPT-4o</Badge>
                    <Badge className="bg-purple-100 text-purple-800">Claude 3.5 Sonnet</Badge>
                    <Badge className="bg-green-100 text-green-800">Tavily Search</Badge>
                    <Badge className="bg-yellow-100 text-yellow-800">React + FastAPI</Badge>
                  </div>
                </div>
                
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <h4 className="font-semibold text-blue-800 mb-2">رؤيتنا:</h4>
                  <p className="text-sm text-blue-700">
                    جعل الأدب العُماني الغني في متناول الجميع من خلال تقنيات الذكاء 
                    الاصطناعي، مع الحفاظ على الدقة العلمية والأصالة الثقافية.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Project Stats */}
            <Card className="shadow-xl bg-white/90 backdrop-blur-sm border-white/50">
              <CardHeader>
                <CardTitle className="text-right text-emerald-800">إحصائيات المشروع</CardTitle>
              </CardHeader>
              <CardContent className="text-right">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">58</div>
                    <div className="text-sm text-purple-700">مصدر موثوق</div>
                  </div>
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">12</div>
                    <div className="text-sm text-blue-700">كاتب عُماني</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">100%</div>
                    <div className="text-sm text-green-700">دقة المعلومات</div>
                  </div>
                  <div className="text-center p-3 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">24/7</div>
                    <div className="text-sm text-orange-700">متاح دائماً</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Back to Main */}
        <div className="text-center mt-12">
          <Button asChild className="bg-emerald-600 hover:bg-emerald-700 text-white text-lg px-8 py-3">
            <a href="/">العودة للدردشة مع غسان</a>
          </Button>
        </div>
      </div>
    </div>
  );
};