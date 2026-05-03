import { useLanguage } from '../context/LanguageContext.jsx';
import './Volunteer.css';

const roles = [
  { key: 'observer', icon: 'visibility', color: 'navy' },
  { key: 'awareness', icon: 'campaign', color: 'saffron' },
  { key: 'transport', icon: 'directions_car', color: 'green' },
  { key: 'doc', icon: 'description', color: 'amber' },
];

export default function Volunteer() {
  const { t, lang } = useLanguage();

  return (
    <main className="page" role="main">
      <div className="page-content">
        {/* Hero */}
        <section className="volunteer-hero" aria-label="Volunteer call to action">
          <div className="volunteer-hero-content">
            <h1 className="volunteer-hero-title">{t('volunteer_title')}</h1>
            {lang === 'hi' && (
              <h2 className="volunteer-hero-title-hi">लोकतंत्र में योगदान दें</h2>
            )}
            <p className="volunteer-hero-desc">{t('volunteer_desc')}</p>
            <button className="btn btn-primary">
              <span className="material-symbols-outlined">volunteer_activism</span>
              {t('volunteer_register')}
              {lang === 'en' && ' / स्वयंसेवक बनें'}
            </button>
          </div>
        </section>

        {/* Available Roles */}
        <section aria-label="Volunteer roles">
          <h2 className="section-title">{t('volunteer_roles_title')}</h2>
          {lang === 'hi' && (
            <p className="volunteer-roles-title-hi">उपलब्ध भूमिकाएं</p>
          )}
          <p className="volunteer-roles-desc">{t('volunteer_roles_desc')}</p>

          <div className="volunteer-roles-grid stagger-children">
            {roles.map((role) => (
              <article key={role.key} className="volunteer-role-card card">
                <div className={`icon-circle icon-circle-${role.color}`}>
                  <span className="material-symbols-outlined">{role.icon}</span>
                </div>
                <h3>{t(`volunteer_${role.key}`)}</h3>
                {lang === 'en' && (
                  <p className="volunteer-role-hi">
                    {role.key === 'observer' ? 'बूथ पर्यवेक्षक' :
                     role.key === 'awareness' ? 'मतदाता जागरूकता' :
                     role.key === 'transport' ? 'परिवहन सहायक' : 'दस्तावेज़ सहायता'}
                  </p>
                )}
                <p className="volunteer-role-desc">{t(`volunteer_${role.key}_desc`)}</p>
                <button className="btn btn-outline btn-sm" style={{ width: '100%', marginTop: 'auto' }}>
                  {t('volunteer_apply')}
                </button>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
