import { useTranslation } from 'react-i18next';
import { ensureI18n } from '../lib/i18n';
ensureI18n();

export default function LangSwitch() {
  const { i18n } = useTranslation();
  const current = i18n.language;

  const toggle = () => {
    const next = current === 'zh' ? 'en' : 'zh';
    i18n.changeLanguage(next);
    localStorage.setItem('custom-skills-lang', next);
    // 同步到 URL 参数
    const url = new URL(window.location.href);
    url.searchParams.set('lng', next);
    window.history.replaceState({}, '', url);
  };

  return (
    <button
      onClick={toggle}
      className="px-2 py-1 rounded-lg text-xs font-medium transition-colors"
      style={{
        color: 'var(--text-muted)',
        border: '1px solid var(--border-default)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.color = 'var(--text-primary)';
        e.currentTarget.style.borderColor = 'var(--border-hover)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.color = 'var(--text-muted)';
        e.currentTarget.style.borderColor = 'var(--border-default)';
      }}
    >
      {current === 'zh' ? '中' : 'EN'}
    </button>
  );
}
