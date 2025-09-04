export const mockChatData = {
  messages: [
    {
      id: 1,
      text: 'أهلاً وسهلاً! أنا غسان، مساعدك الأدبي العُماني الذكي. كيف يمكنني مساعدتك اليوم في عالم الأدب العُماني؟',
      sender: 'ghassan',
      timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    },
    {
      id: 2,
      text: 'السلام عليكم، أريد أن أتعرف على أهم الشعراء العُمانيين المعاصرين',
      sender: 'user',
      timestamp: new Date(Date.now() - 3000000).toISOString(), // 50 minutes ago
    },
    {
      id: 3,
      text: 'وعليكم السلام ورحمة الله وبركاته! سعيد جداً لاستفسارك. من أبرز الشعراء العُمانيين المعاصرين:\n\n• سيف الرحبي - شاعر مبدع حاز على جائزة الشعر العربي\n• هدى حمد - من رائدات الشعر النسائي في عُمان\n• عبدالله الريامي - شاعر معروف بأسلوبه المتميز\n• سعيد الصقلاوي - من الأصوات الشعرية المهمة\n\nهل تريد التعمق في شاعر معين منهم؟',
      sender: 'ghassan',
      timestamp: new Date(Date.now() - 2400000).toISOString(), // 40 minutes ago
    }
  ],
  
  userSessions: [
    {
      id: 'session_1',
      title: 'مناقشة الشعر المعاصر',
      lastMessage: 'شكراً لك على المعلومات المفيدة',
      timestamp: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
      messageCount: 15
    },
    {
      id: 'session_2', 
      title: 'الأدب العُماني التراثي',
      lastMessage: 'ما رأيك في قصائد ابن دريد؟',
      timestamp: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
      messageCount: 8
    }
  ]
};