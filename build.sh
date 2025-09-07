#!/bin/bash

# بناء Frontend
echo "🚀 بناء واجهة المستخدم..."
cd frontend
npm run build

# إنشاء مجلد النشر
echo "📦 تحضير ملفات النشر..."
cd ../
mkdir -p dist
cp -r frontend/build/* dist/
cp -r backend/* dist/api/

# نسخ الملفات المطلوبة
cp vercel.json dist/
cp requirements.txt dist/

echo "✅ المشروع جاهز للنشر على Vercel!"
echo "🌐 استخدم الأمر: vercel --prod"