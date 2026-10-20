"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import {
  Calculator, BookOpen, Users, Trophy, Globe, Zap,
  Star, Award, TrendingUp, Cpu, Shield, Mail
} from "lucide-react";

export default function Home() {
  const [lang, setLang] = useState<"fa" | "en" | "ar">("fa");
  const [stats, setStats] = useState({
    contributions: 18474,
    frontier: 200000000,
    series: 7,
    articles: 0,
    users: 0,
  });

  const t = {
    fa: {
      title: "پلتفرم ریاضی پارسی",
      subtitle: "به افتخار ریاضیدانان پارسی-اسلامی",
      dedicated: "تقدیم به Jamshid al-Kashi (الکاشی)",
      tabHome: "خانه",
      tabSeries: "سری‌ها",
      tabRange: "بازه‌ها",
      tabMagazine: "مجله",
      tabAbout: "درباره",
      contributions: "مشارکت‌ها در FactorDB",
      frontier: "فرانتیر پیوسته",
      series: "سری‌های ریاضی",
      articles: "مقالات مجله",
      users: "کاربران",
      startFactoring: "شروع فاکتور کردن",
      joinNetwork: "پیوستن به شبکه",
      readMagazine: "خواندن مجله",
      kashani: "کاشانی",
      khayyam: "خیام",
      biruni: "بیرونی",
      karaji: "کرجی",
      khwarizmi: "خوارزمی",
      tusi: "طوسی",
      soltani: "سلطانی",
      forProcessing: "برای پردازش ریاضی و علمی",
      medicalResearch: "تحقیقات پزشکی و دارویی",
      volunteerNetwork: "شبکه داوطلبین",
      securePlatform: "پلتفرم امن",
      loginGmail: "ورود با Gmail",
      loginPhone: "ورود با شماره موبایل",
      description: "پلتفرم چندزبانه برای فاکتور کردن اعداد، مجله ریاضی، و شبکه داوطلبین پردازش",
      rangeComplete: "کامل شده",
      rangeInProgress: "در حال اجرا",
      digits: "رقم",
      numbers: "عدد",
      primes: "اعداد اول",
      composites: "مرکب فاکتور شده",
      noGaps: "بدون شکست",
      motivation: "با هم بریم برای جایزه بزرگ",
    },
    en: {
      title: "Persian Math Platform",
      subtitle: "Honoring Persian-Islamic mathematicians",
      dedicated: "Dedicated to Jamshid al-Kashi",
      tabHome: "Home",
      tabSeries: "Series",
      tabRange: "Ranges",
      tabMagazine: "Magazine",
      tabAbout: "About",
      contributions: "FactorDB Contributions",
      frontier: "Continuous Frontier",
      series: "Math Series",
      articles: "Magazine Articles",
      users: "Users",
      startFactoring: "Start Factoring",
      joinNetwork: "Join Network",
      readMagazine: "Read Magazine",
      kashani: "Kashani",
      khayyam: "Khayyam",
      biruni: "Biruni",
      karaji: "Karaji",
      khwarizmi: "Khwarizmi",
      tusi: "Tusi",
      soltani: "Soltani",
      forProcessing: "For mathematical and scientific processing",
      medicalResearch: "Medical and pharmaceutical research",
      volunteerNetwork: "Volunteer Network",
      securePlatform: "Secure Platform",
      loginGmail: "Login with Gmail",
      loginPhone: "Login with Phone",
      description: "Multilingual platform for number factoring, math magazine, and volunteer computing network",
      rangeComplete: "Complete",
      rangeInProgress: "In Progress",
      digits: "digits",
      numbers: "numbers",
      primes: "primes",
      composites: "factored composites",
      noGaps: "no gaps",
      motivation: "Let's go for the grand prize together",
    },
    ar: {
      title: "منصة الرياضيات الفارسية",
      subtitle: "تكريماً للرياضيين الفرس",
      dedicated: "إهداء إلى جمشيد الكاشاني",
      tabHome: "الرئيسية",
      tabSeries: "السلاسل",
      tabRange: "النطاقات",
      tabMagazine: "المجلة",
      tabAbout: "حول",
      contributions: "مساهمات FactorDB",
      frontier: "الحد المستمر",
      series: "السلاسل الرياضية",
      articles: "مقالات المجلة",
      users: "المستخدمون",
      startFactoring: "ابدأ التحليل",
      joinNetwork: "انضم للشبكة",
      readMagazine: "اقرأ المجلة",
      kashani: "الكاشاني",
      khayyam: "الخيام",
      biruni: "البيروني",
      karaji: "الكرجي",
      khwarizmi: "الخوارزمي",
      tusi: "الطوسي",
      soltani: "السلطاني",
      forProcessing: "للمعالجة الرياضية والعلمية",
      medicalResearch: "البحوث الطبية والصيدلانية",
      volunteerNetwork: "شبكة المتطوعين",
      securePlatform: "منصة آمنة",
      loginGmail: "تسجيل الدخول بـ Gmail",
      loginPhone: "تسجيل الدخول بالهاتف",
      description: "منصة متعددة اللغات لتحليل الأرقام ومجلة الرياضيات وشبكة الحوسبة التطوعية",
      rangeComplete: "مكتمل",
      rangeInProgress: "قيد التنفيذ",
      digits: "أرقام",
      numbers: "أرقام",
      primes: "أعداد أولية",
      composites: "أعداد مركبة محللة",
      noGaps: "بدون فجوات",
      motivation: "لنذهب للجائزة الكبرى معاً",
    },
  };

  const tr = t[lang];

  const series = [
    { name: tr.kashani, icon: "🔢", color: "from-amber-500 to-orange-600", desc: lang === "fa" ? "اعشار π" : lang === "ar" ? "كسور π" : "Digits of π", oeis: "—" },
    { name: tr.khayyam, icon: "📐", color: "from-emerald-500 to-teal-600", desc: lang === "fa" ? "مثلث خیام" : lang === "ar" ? "مثلث الخيام" : "Khayyam Triangle", oeis: "A007318" },
    { name: tr.biruni, icon: "🌍", color: "from-blue-500 to-indigo-600", desc: lang === "fa" ? "فاصله‌های اول" : lang === "ar" ? "فجوات الأعداد الأولية" : "Prime gaps", oeis: "A005250" },
    { name: tr.karaji, icon: "🔺", color: "from-purple-500 to-violet-600", desc: lang === "fa" ? "اعداد مثلثی" : lang === "ar" ? "أعداد مثلثية" : "Triangular numbers", oeis: "A000217" },
    { name: tr.khwarizmi, icon: "📝", color: "from-rose-500 to-pink-600", desc: lang === "fa" ? "جبر" : lang === "ar" ? "الجبر" : "Algebra", oeis: "A007917" },
    { name: tr.tusi, icon: "♊", color: "from-cyan-500 to-blue-600", desc: lang === "fa" ? "زوج‌های اول" : lang === "ar" ? "أولية توأمة" : "Twin primes", oeis: "A001359" },
    { name: tr.soltani, icon: "⭐", color: "from-yellow-500 to-amber-600", desc: lang === "fa" ? "اعداد کامل" : lang === "ar" ? "أعداد كاملة" : "Perfect numbers", oeis: "A000396" },
  ];

  const ranges = [
    { range: "1 - 100K", digits: 5, primes: 9592, composites: 90407, complete: true },
    { range: "1 - 1M", digits: 6, primes: 78498, composites: 921501, complete: true },
    { range: "1 - 10M", digits: 7, primes: 664579, composites: 9335420, complete: true },
    { range: "1 - 100M", digits: 8, primes: 5761455, composites: 94238544, complete: true },
    { range: "1 - 200M", digits: 9, primes: 5317482, composites: 94682519, complete: true },
    { range: "200M - 1B", digits: 9, primes: 0, composites: 0, complete: false },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900" dir={lang === "fa" || lang === "ar" ? "rtl" : "ltr"}>
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-white/80 backdrop-blur-md dark:bg-slate-950/80">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-3xl">🕌</div>
            <div>
              <h1 className="text-xl font-bold">{tr.title}</h1>
              <p className="text-xs text-slate-500">{tr.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* Language switcher */}
            <div className="flex gap-1">
              <Button size="sm" variant={lang === "fa" ? "default" : "ghost"} onClick={() => setLang("fa")}>🇮🇷 فارسی</Button>
              <Button size="sm" variant={lang === "en" ? "default" : "ghost"} onClick={() => setLang("en")}>🇬🇧 EN</Button>
              <Button size="sm" variant={lang === "ar" ? "default" : "ghost"} onClick={() => setLang("ar")}>🇵🇸 عربی</Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <div className="text-6xl mb-4">🔢</div>
          <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
            {tr.title}
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-400 mb-2">{tr.description}</p>
          <Badge variant="secondary" className="text-sm">
            {tr.dedicated} (1380-1429)
          </Badge>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <Button size="lg" className="gap-2">
              <Calculator className="w-5 h-5" />
              {tr.startFactoring}
            </Button>
            <Button size="lg" variant="outline" className="gap-2">
              <Users className="w-5 h-5" />
              {tr.joinNetwork}
            </Button>
            <Button size="lg" variant="outline" className="gap-2">
              <BookOpen className="w-5 h-5" />
              {tr.readMagazine}
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <Card className="text-center">
            <CardHeader className="pb-2">
              <Trophy className="w-8 h-8 mx-auto text-amber-500" />
              <CardTitle className="text-3xl font-bold">{stats.contributions.toLocaleString()}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-500">{tr.contributions}</p>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardHeader className="pb-2">
              <TrendingUp className="w-8 h-8 mx-auto text-emerald-500" />
              <CardTitle className="text-3xl font-bold">200M</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-500">{tr.frontier}</p>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardHeader className="pb-2">
              <Star className="w-8 h-8 mx-auto text-purple-500" />
              <CardTitle className="text-3xl font-bold">{stats.series}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-500">{tr.series}</p>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardHeader className="pb-2">
              <Users className="w-8 h-8 mx-auto text-blue-500" />
              <CardTitle className="text-3xl font-bold">{stats.users}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-500">{tr.users}</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Tabs */}
        <Tabs defaultValue="home" className="w-full">
          <TabsList className="grid w-full grid-cols-5 mb-6">
            <TabsTrigger value="home">{tr.tabHome}</TabsTrigger>
            <TabsTrigger value="series">{tr.tabSeries}</TabsTrigger>
            <TabsTrigger value="range">{tr.tabRange}</TabsTrigger>
            <TabsTrigger value="magazine">{tr.tabMagazine}</TabsTrigger>
            <TabsTrigger value="about">{tr.tabAbout}</TabsTrigger>
          </TabsList>

          {/* Home Tab */}
          <TabsContent value="home" className="space-y-6">
            <div className="grid md:grid-cols-3 gap-6">
              <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950 dark:to-cyan-950">
                <CardHeader>
                  <Cpu className="w-10 h-10 mb-2 text-blue-600" />
                  <CardTitle>{tr.forProcessing}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    {lang === "fa" ? "پردازش ریاضی، علمی، پزشکی و دارویی با شبکه داوطلبین" : lang === "ar" ? "معالجة الرياضيات والعلوم والطب والصيدلة مع شبكة المتطوعين" : "Math, science, medical and pharmaceutical processing with volunteer network"}
                  </p>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-950 dark:to-green-950">
                <CardHeader>
                  <Shield className="w-10 h-10 mb-2 text-emerald-600" />
                  <CardTitle>{tr.securePlatform}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    {lang === "fa" ? "امنیت بالا، احراز هویت با Gmail و شماره موبایل" : lang === "ar" ? "أمان عالي، مصادقة بـ Gmail والهاتف" : "High security, authentication with Gmail and phone"}
                  </p>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950 dark:to-orange-950">
                <CardHeader>
                  <Globe className="w-10 h-10 mb-2 text-amber-600" />
                  <CardTitle>{tr.volunteerNetwork}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    {lang === "fa" ? "نرم‌افزار Rust برای پردازش سریع، شبکه داوطلبین" : lang === "ar" ? "برنامج Rust للمعالجة السريعة، شبكة المتطوعين" : "Rust software for fast processing, volunteer network"}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Login buttons */}
            <Card>
              <CardHeader>
                <CardTitle className="text-center">{lang === "fa" ? "ورود / ثبت‌نام" : lang === "ar" ? "تسجيل الدخول / التسجيل" : "Login / Register"}</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-wrap justify-center gap-3">
                <Button variant="outline" className="gap-2">
                  <Mail className="w-5 h-5" />
                  {tr.loginGmail}
                </Button>
                <Button variant="outline" className="gap-2">
                  <span className="text-lg">📱</span>
                  {tr.loginPhone}
                </Button>
              </CardContent>
            </Card>

            {/* Motivation */}
            <div className="text-center py-8">
              <div className="text-4xl mb-2">🏆</div>
              <p className="text-xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                {tr.motivation}
              </p>
              <p className="text-sm text-slate-500 mt-2">
                {lang === "fa" ? "EFF Prize: $150,000 برای عدد اول ۱۰۰ میلیون رقمی" : lang === "ar" ? "جائزة EFF: 150,000$ للعدد الأولي 100 مليون رقم" : "EFF Prize: $150,000 for 100-million-digit prime"}
              </p>
            </div>
          </TabsContent>

          {/* Series Tab */}
          <TabsContent value="series">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {series.map((s, i) => (
                <Card key={i} className={`bg-gradient-to-br ${s.color} text-white overflow-hidden`}>
                  <CardHeader>
                    <div className="text-4xl mb-2">{s.icon}</div>
                    <CardTitle className="text-2xl">{s.name}</CardTitle>
                    <Badge variant="secondary" className="w-fit">{s.oeis}</Badge>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm opacity-90">{s.desc}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Range Tab */}
          <TabsContent value="range">
            <Card>
              <CardHeader>
                <CardTitle>{lang === "fa" ? "پیشرفت بازه‌ها" : lang === "ar" ? "تقدم النطاقات" : "Range Progress"}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {ranges.map((r, i) => (
                    <div key={i} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Badge variant={r.complete ? "default" : "secondary"}>
                            {r.complete ? `✅ ${tr.rangeComplete}` : `⏳ ${tr.rangeInProgress}`}
                          </Badge>
                          <span className="font-mono text-sm">{r.range}</span>
                          <span className="text-xs text-slate-500">({r.digits} {tr.digits})</span>
                        </div>
                        <div className="text-sm text-slate-500">
                          {r.primes > 0 ? `${r.primes.toLocaleString()} ${tr.primes}` : "—"}
                        </div>
                      </div>
                      <Progress value={r.complete ? 100 : 30} className="h-2" />
                      <div className="flex justify-between text-xs text-slate-500">
                        <span>{r.composites > 0 ? `${r.composites.toLocaleString()} ${tr.composites}` : "—"}</span>
                        <span>{r.complete ? `✅ ${tr.noGaps}` : ""}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Magazine Tab */}
          <TabsContent value="magazine">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="w-6 h-6" />
                  {lang === "fa" ? "مجله ریاضی" : lang === "ar" ? "مجلة الرياضيات" : "Math Magazine"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <div className="text-5xl mb-4">📚</div>
                  <p className="text-slate-500">
                    {lang === "fa" ? "مجله به‌زودی راه‌اندازی می‌شه — با AI تولید محتوا و SEO" : lang === "ar" ? "المجلة قريباً — مع الذكاء الاصطناعي وتحسين محركات البحث" : "Magazine coming soon — with AI content generation and SEO"}
                  </p>
                  <p className="text-sm text-slate-400 mt-2">
                    {lang === "fa" ? "اخبار ریاضی، علمی، پزشکی از منابع انگلیسی و ترجمه" : lang === "ar" ? "أخبار الرياضيات والعلوم والطب من مصادر إنجليزية وترجمة" : "Math, science, medical news from English sources with translation"}
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* About Tab */}
          <TabsContent value="about">
            <Card>
              <CardHeader>
                <CardTitle>{lang === "fa" ? "درباره ما" : lang === "ar" ? "من نحن" : "About Us"}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-slate-600 dark:text-slate-400">
                  {lang === "fa" ? "این پلتفرم به افتخار ریاضیدانان پارسی-اسلامی ساخته شده است. هدف ما ساخت یه پایگاه داده کامل از اعداد فاکتور شده، مجله ریاضی، و شبکه داوطلبین پردازش است." : lang === "ar" ? "تم بناء هذه المنصة تكريماً للرياضيين الفرس. هدفنا بناء قاعدة بيانات كاملة للأعداد المحللة ومجلة رياضية وشبكة متطوعين." : "This platform is built to honor Persian-Islamic mathematicians. Our goal is to build a complete database of factored numbers, a math magazine, and a volunteer computing network."}
                </p>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-amber-500" />
                    <span className="text-sm">Rust + Assembly</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Shield className="w-5 h-5 text-emerald-500" />
                    <span className="text-sm">Security + Anti-hack</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Globe className="w-5 h-5 text-blue-500" />
                    <span className="text-sm">Multilingual (FA/EN/AR)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-purple-500" />
                    <span className="text-sm">FactorDB Integration</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t bg-white dark:bg-slate-950 py-6">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm text-slate-500">
            © 2026 {tr.title} — {tr.dedicated}
          </p>
          <div className="flex justify-center gap-4 mt-2 text-xs text-slate-400">
            <span>FactorDB API</span>
            <span>OEIS</span>
            <span>Cunningham Project</span>
            <span>GIMPS</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
