import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import en from './locales/en.json';
import zh from './locales/zh.json';
import { generateCategoryTranslations } from '../config/tags.js';

// 从 tags.ts 动态生成分类翻译
const enCategories = generateCategoryTranslations('en');
const zhCategories = generateCategoryTranslations('zh');

// 合并到翻译文件
en.skill = { ...en.skill, category: { ...en.skill?.category, ...enCategories } };
zh.skill = { ...zh.skill, category: { ...zh.skill?.category, ...zhCategories } };

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
