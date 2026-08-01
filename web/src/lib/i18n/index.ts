// i18n context provider for Astro islands
// Replaces i18next-browser-languagedetector (which depends on browser APIs)
// Detection: URL ?lng= param > localStorage > navigator.language

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from '../../i18n/locales/en.json';
import zh from '../../i18n/locales/zh.json';
import { generateCategoryTranslations } from '../../config/tags';

// 动态生成分类翻译
const enCategories = generateCategoryTranslations('en');
const zhCategories = generateCategoryTranslations('zh');

en.skill = { ...en.skill, category: { ...en.skill?.category, ...enCategories } };
zh.skill = { ...zh.skill, category: { ...zh.skill?.category, ...zhCategories } };

let initialized = false;

export function ensureI18n() {
  if (initialized) return i18n;
  initialized = true;

  i18n.use(initReactI18next).init({
    resources: {
      en: { translation: en },
      zh: { translation: zh },
    },
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
  });

  // 在浏览器端检测语言
  if (typeof window !== 'undefined') {
    const params = new URLSearchParams(window.location.search);
    const lang = params.get('lng')
      || localStorage.getItem('custom-skills-lang')
      || (navigator.language.startsWith('zh') ? 'zh' : 'en');
    i18n.changeLanguage(lang);
  }

  return i18n;
}

export default i18n;
