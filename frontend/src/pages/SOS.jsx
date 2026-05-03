import { useLanguage } from '../context/LanguageContext.jsx';
import './SOS.css';

const reportCategories = [
  { key: 'coercion', icon: 'warning' },
  { key: 'capture', icon: 'gavel' },
  { key: 'malfunction', icon: 'build' },
  { key: 'complaint', icon: 'report' },
];

export default function SOS() {
  const { t, lang } = useLanguage();

  return (
    <main className="page" role="main">
      <div className="page-content stagger-children">
        {/* Title */}
        <div className="sos-page-header" style={{ textAlign: 'center' }}>
          <h1 className="sos-page-title">{t('sos_title')}</h1>
          {lang === 'en' && (
            <h2 className="sos-page-title-hi">आपातकालीन सहायता</h2>
          )}
          <p className="sos-page-desc">{t('sos_desc')}</p>
        </div>

        {/* Emergency Buttons */}
        <div className="sos-emergency-grid">
          <a href="tel:100" className="sos-dial-card sos-dial-police">
            <div className="sos-dial-icon">
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1", color: 'var(--error)' }}>
                shield
              </span>
            </div>
            <h3 className="text-error">{t('sos_police')}</h3>
            <p>{t('sos_police_desc')}</p>
            <button className="btn btn-danger" style={{ width: '100%' }}>
              <span className="material-symbols-outlined">call</span>
              {t('sos_dial_100')}
            </button>
          </a>

          <a href="tel:1950" className="sos-dial-card sos-dial-helpline">
            <div className="sos-dial-icon">
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1", color: 'var(--navy)' }}>
                support_agent
              </span>
            </div>
            <h3 className="text-navy">{t('sos_helpline')}</h3>
            <p>{t('sos_helpline_desc')}</p>
            <button className="btn btn-danger" style={{ width: '100%', background: 'var(--saffron-dark)' }}>
              <span className="material-symbols-outlined">call</span>
              {t('sos_dial_1950')}
            </button>
          </a>
        </div>

        {/* File Report */}
        <section aria-label="File an urgent report">
          <h2 className="section-title">{t('sos_file_report')}</h2>
          <p className="sos-report-desc">{t('sos_file_report_desc')}</p>

          <div className="sos-report-grid">
            {reportCategories.map((cat) => (
              <button key={cat.key} className="sos-report-card card card-interactive">
                <div className="sos-report-left">
                  <div className="icon-circle icon-circle-navy" style={{ width: '40px', height: '40px' }}>
                    <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>{cat.icon}</span>
                  </div>
                  <div>
                    <h3>{t(`sos_${cat.key}`)}</h3>
                    <p>{t(`sos_${cat.key}_desc`)}</p>
                  </div>
                </div>
                <span className="material-symbols-outlined" style={{ color: 'var(--outline)' }}>
                  chevron_right
                </span>
              </button>
            ))}
          </div>
        </section>

        {/* Secure Notice */}
        <section className="sos-secure-notice" aria-label="Security notice">
          <span className="material-symbols-outlined" style={{ fontSize: '28px', color: 'var(--navy)' }}>
            lock
          </span>
          <h3>{t('sos_secure')}</h3>
          <p>{t('sos_secure_desc')}</p>
        </section>
      </div>
    </main>
  );
}
