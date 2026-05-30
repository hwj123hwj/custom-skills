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
        className="px-1.5 py-0.5 rounded transition-all duration-200"
        style={{
          color: current === 'zh' ? '#22C55E' : 'var(--text-muted)',
          fontWeight: current === 'zh' ? 600 : 400,
        }}
      >
        中文
      </button>
      <span style={{ color: 'var(--text-muted)' }}>/</span>
      <button
        onClick={() => setLang('en')}
        className="px-1.5 py-0.5 rounded transition-all duration-200"
        style={{
          color: current === 'en' ? '#22C55E' : 'var(--text-muted)',
          fontWeight: current === 'en' ? 600 : 400,
        }}
      >
        EN
      </button>
    </div>
  );
}
