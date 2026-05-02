import { useTranslation } from 'react-i18next';

export function LangSwitch() {
  const { i18n } = useTranslation();
  const current = i18n.language;

  const setLang = (lang: string) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('custom-skills-lang', lang);
  };

  return (
    <div className="flex items-center gap-1 text-sm select-none">
      <button
        onClick={() => setLang('zh')}
        className={`transition-colors ${
          current === 'zh' ? 'text-white font-medium' : 'text-gray-500 hover:text-gray-300'
        }`}
      >
        中文
      </button>
      <span className="text-gray-600">/</span>
      <button
        onClick={() => setLang('en')}
        className={`transition-colors ${
          current === 'en' ? 'text-white font-medium' : 'text-gray-500 hover:text-gray-300'
        }`}
      >
        EN
      </button>
    </div>
  );
}
