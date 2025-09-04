import React, { useState } from 'react';
import { Upload, Image, Save, X, Check } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';

export const ImageUploader = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const handleImageSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // التحقق من نوع الملف
      if (!file.type.startsWith('image/')) {
        setMessage('يرجى اختيار ملف صورة صالح');
        setMessageType('error');
        return;
      }

      // التحقق من حجم الملف (أقل من 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setMessage('حجم الصورة كبير جداً. يرجى اختيار صورة أقل من 5MB');
        setMessageType('error');
        return;
      }

      setSelectedImage(file);
      
      // إنشاء preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target.result);
      };
      reader.readAsDataURL(file);
      
      setMessage('');
    }
  };

  const handleUpload = async () => {
    if (!selectedImage) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('image', selectedImage);
      formData.append('type', 'avatar');
      formData.append('name', 'ghassan-avatar');

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/upload/avatar`, {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (result.success) {
        setMessage(`تم رفع صورة غسان بنجاح! ${result.filename}`);
        setMessageType('success');
        
        // إعادة تحميل الصفحة بعد ثوانٍ لتحديث الصورة
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      } else {
        setMessage(`خطأ في الرفع: ${result.error}`);
        setMessageType('error');
      }
    } catch (error) {
      setMessage(`خطأ في الاتصال: ${error.message}`);
      setMessageType('error');
    } finally {
      setIsUploading(false);
    }
  };

  const handleCancel = () => {
    setSelectedImage(null);
    setPreviewUrl(null);
    setMessage('');
    setMessageType('');
  };

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="text-right text-emerald-800 flex items-center gap-2">
          <Image className="h-5 w-5" />
          رفع صورة غسان
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        
        {/* Message */}
        {message && (
          <div className={`p-3 rounded-lg text-center text-sm ${
            messageType === 'success' 
              ? 'bg-green-50 text-green-800 border border-green-200' 
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}>
            {message}
          </div>
        )}

        {/* Preview Area */}
        {previewUrl ? (
          <div className="text-center space-y-3">
            <div className="relative inline-block">
              <Avatar className="h-24 w-24 ring-2 ring-emerald-300 shadow-lg">
                <AvatarImage src={previewUrl} alt="معاينة صورة غسان" className="object-cover" />
                <AvatarFallback className="bg-emerald-500 text-white text-2xl">غ</AvatarFallback>
              </Avatar>
              <Button
                size="sm"
                variant="destructive"
                className="absolute -top-2 -right-2 h-6 w-6 rounded-full p-0"
                onClick={handleCancel}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
            <p className="text-sm text-gray-600">معاينة صورة غسان</p>
            
            <div className="flex gap-2 justify-center">
              <Button
                onClick={handleUpload}
                disabled={isUploading}
                className="bg-emerald-500 hover:bg-emerald-600 text-white"
              >
                {isUploading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    جاري الرفع...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <Save className="h-4 w-4" />
                    حفظ الصورة
                  </div>
                )}
              </Button>
              
              <Button
                onClick={handleCancel}
                variant="outline"
                disabled={isUploading}
              >
                إلغاء
              </Button>
            </div>
          </div>
        ) : (
          <div className="text-center space-y-4">
            <div className="border-2 border-dashed border-emerald-300 rounded-lg p-8 hover:border-emerald-400 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="hidden"
                id="avatar-upload"
              />
              <label 
                htmlFor="avatar-upload"
                className="cursor-pointer flex flex-col items-center gap-3 text-emerald-600 hover:text-emerald-700"
              >
                <Upload className="h-12 w-12" />
                <div className="text-center">
                  <p className="font-medium">اختر صورة غسان</p>
                  <p className="text-sm text-gray-500 mt-1">PNG, JPG أو JPEG (أقل من 5MB)</p>
                </div>
              </label>
            </div>
            
            <p className="text-xs text-gray-500 text-center">
              ستصبح هذه الصورة avatar غسان في جميع أنحاء التطبيق
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};