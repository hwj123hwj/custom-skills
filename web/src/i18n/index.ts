import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import en from './locales/en.json';
import zh from './locales/zh.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      zh: { translation: zh },
    },
    fallbackLng: 'en',
    // 检测顺序：localStorage 优先，初次访问回退到浏览器语言
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'custom-skills-lang',
    },
    // 将 zh-CN、zh-TW 等都映射到 zh
    load: 'languageOnly',
    interpolation: {
      escapeValue: false, // React 已做 XSS 防护
    },
  });

export default i18n;
