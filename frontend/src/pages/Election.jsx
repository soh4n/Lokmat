import { useState } from 'react';
import { useLanguage } from '../context/LanguageContext.jsx';
import './Election.css';

const candidates = [
  { id: 1, name: 'Rajesh Kumar', name_hi: 'राजेश कुमार', party: 'National Progress Party', party_hi: 'राष्ट्रीय प्रगति पार्टी', assets: '₹2.5 Cr', criminal: 'none' },
  { id: 2, name: 'Meera Sharma', name_hi: 'मीरा शर्मा', party: 'United Democratic Front', party_hi: 'संयुक्त लोकतांत्रिक मोर्चा', assets: '₹1.8 Cr', criminal: '2' },
  { id: 3, name: 'Arjun Patel', name_hi: 'अर्जुन पटेल', party: 'Peoples Alliance', party_hi: 'जन गठबंधन', assets: '₹4.2 Cr', criminal: 'none' },
];

const manifestoTopics = [
  { topic: 'Education', topic_hi: 'शिक्षा', icon: 'school', parties: [
    { name: 'NPP', promise: 'Build 5 new tech-focused high schools.', promise_hi: '5 नए तकनीकी हाई स्कूल बनाएं।' },
    { name: 'UDF', promise: 'Increase teacher salaries by 15% across district.', promise_hi: 'जिले भर में शिक्षक वेतन 15% बढ़ाएं।' },
  ]},
  { topic: 'Healthcare', topic_hi: 'स्वास्थ्य', icon: 'local_hospital', parties: [
    { name: 'NPP', promise: 'Subsidized medicines for senior citizens.', promise_hi: 'वरिष्ठ नागरिकों के लिए सब्सिडी वाली दवाएं।' },
    { name: 'UDF', promise: 'Upgrade local clinic to a 100-bed hospital.', promise_hi: 'स्थानीय क्लिनिक को 100-बेड अस्पताल में अपग्रेड।' },
  ]},
  { topic: 'Infrastructure', topic_hi: 'बुनियादी ढांचा', icon: 'construction', parties: [
    { name: 'NPP', promise: 'Complete metro extension by 2026.', promise_hi: '2026 तक मेट्रो विस्तार पूरा करें।' },
    { name: 'UDF', promise: 'Smart city pilot in 3 wards.', promise_hi: '3 वार्डों में स्मार्ट सिटी पायलट।' },
  ]},
];

const upcomingElections = [
  { year: '2024', type: 'Lok Sabha', type_hi: 'लोक सभा', name: '18th Lok Sabha General Election', name_hi: '18वीं लोक सभा आम चुनाव', months: 'Apr–Jun 2024', status: 'completed', seats: '543', icon: 'check_circle' },
  { year: '2024', type: 'Vidhan Sabha', type_hi: 'विधान सभा', name: 'Haryana & J&K Assembly', name_hi: 'हरियाणा और जम्मू-कश्मीर विधानसभा', months: 'Sep–Oct 2024', status: 'completed', seats: '90 + 90', icon: 'check_circle' },
  { year: '2024', type: 'Vidhan Sabha', type_hi: 'विधान सभा', name: 'Maharashtra & Jharkhand Assembly', name_hi: 'महाराष्ट्र और झारखंड विधानसभा', months: 'Nov 2024', status: 'completed', seats: '288 + 81', icon: 'check_circle' },
  { year: '2025', type: 'Vidhan Sabha', type_hi: 'विधान सभा', name: 'Delhi Assembly Election', name_hi: 'दिल्ली विधानसभा चुनाव', months: 'Feb 2025', status: 'completed', seats: '70', icon: 'check_circle' },
  { year: '2025', type: 'Vidhan Sabha', type_hi: 'विधान सभा', name: 'Bihar Assembly Election', name_hi: 'बिहार विधानसभा चुनाव', months: 'Oct–Nov 2025', status: 'upcoming', seats: '243', icon: 'event' },
  { year: '2026', type: 'Vidhan Sabha', type_hi: 'विधान सभा', name: 'West Bengal, Assam, Tamil Nadu, Kerala, Puducherry', name_hi: 'पश्चिम बंगाल, असम, तमिलनाडु, केरल, पुडुचेरी', months: 'Apr–May 2026', status: 'upcoming', seats: '824 total', icon: 'event' },
  { year: '2027', type: 'Vidhan Sabha', type_hi: 'विधान सभा', name: 'Uttar Pradesh, Punjab, Uttarakhand, Manipur, Goa', name_hi: 'उत्तर प्रदेश, पंजाब, उत्तराखंड, मणिपुर, गोवा', months: 'Feb–Mar 2027', status: 'upcoming', seats: '690 total', icon: 'event' },
  { year: '2027', type: 'Vidhan Sabha', type_hi: 'विधान सभा', name: 'Gujarat & Himachal Pradesh Assembly', name_hi: 'गुजरात और हिमाचल प्रदेश विधानसभा', months: 'Dec 2027', status: 'upcoming', seats: '182 + 68', icon: 'event' },
  { year: '2028', type: 'Vidhan Sabha', type_hi: 'विधान सभा', name: 'Karnataka, Madhya Pradesh, Rajasthan, Chhattisgarh, Telangana, Mizoram', name_hi: 'कर्नाटक, मध्य प्रदेश, राजस्थान, छत्तीसगढ़, तेलंगाना, मिजोरम', months: '2028', status: 'upcoming', seats: '1000+ total', icon: 'event' },
];

export default function Election() {
  const { t, lang } = useLanguage();
  const [activeTab, setActiveTab] = useState('upcoming');

  const tabs = [
    { id: 'upcoming', label: lang === 'hi' ? 'आगामी चुनाव' : 'Upcoming' },
    { id: 'learn', label: lang === 'hi' ? 'जानें' : 'Learn' },
    { id: 'candidates', label: lang === 'hi' ? 'उम्मीदवार' : 'Candidates' },
    { id: 'manifesto', label: lang === 'hi' ? 'घोषणापत्र' : 'Manifestos' },
  ];

  return (
    <main className="page" role="main">
      <div className="page-content">
        <h1 className="section-title">{t('candidates_title')}</h1>
        <p className="section-subtitle">
          <span className="material-symbols-outlined" style={{ fontSize: '18px', verticalAlign: 'middle' }}>location_on</span>
          {' '}New Delhi {t('candidates_constituency')}
        </p>

        <div className="election-tabs" role="tablist">
          {tabs.map((tab) => (
            <button key={tab.id} role="tab" aria-selected={activeTab === tab.id}
              className={`election-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}>{tab.label}</button>
          ))}
        </div>

        {/* Upcoming Elections Tab */}
        {activeTab === 'upcoming' && (
          <div className="upcoming-section" role="tabpanel">
            <div className="upcoming-header">
              <span className="material-symbols-outlined" style={{ color: 'var(--saffron)' }}>calendar_month</span>
              <div>
                <h2>{t('election_upcoming_title')}</h2>
                <p className="text-muted">{t('election_upcoming_desc')}</p>
              </div>
            </div>
            <div className="upcoming-timeline stagger-children">
              {upcomingElections.map((e, i) => (
                <article key={i} className={`timeline-item ${e.status}`}>
                  <div className="timeline-dot">
                    <span className="material-symbols-outlined" style={{ fontSize: '16px', color: e.status === 'completed' ? 'var(--green-india)' : 'var(--saffron)' }}>{e.icon}</span>
                  </div>
                  <div className="timeline-content">
                    <div className="timeline-meta">
                      <span className="timeline-year">{e.year}</span>
                      <span className={`badge ${e.status === 'completed' ? 'badge-green' : 'badge-saffron'}`}>
                        {lang === 'hi' ? e.type_hi : e.type}
                      </span>
                      {e.status === 'completed' && <span className="badge badge-outline">{lang === 'hi' ? 'पूर्ण' : 'Done'}</span>}
                    </div>
                    <h3>{lang === 'hi' ? e.name_hi : e.name}</h3>
                    <div className="timeline-details">
                      <span><span className="material-symbols-outlined" style={{ fontSize: '14px' }}>event</span> {e.months}</span>
                      <span><span className="material-symbols-outlined" style={{ fontSize: '14px' }}>groups</span> {e.seats} {lang === 'hi' ? 'सीटें' : 'seats'}</span>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        )}

        {/* Learn Tab */}
        {activeTab === 'learn' && (
          <div className="learn-section" role="tabpanel">
            <div className="learn-card">
              <div className="learn-card-icon" style={{ background: 'var(--navy)' }}>
                <span className="material-symbols-outlined" style={{ color: '#fff' }}>account_balance</span>
              </div>
              <h2>{t('election_lok_sabha_title')}</h2>
              <p>{t('election_lok_sabha_desc')}</p>
              <div className="learn-stats">
                <div className="learn-stat"><strong>543</strong><span>{lang === 'hi' ? 'सीटें' : 'Seats'}</span></div>
                <div className="learn-stat"><strong>5 {lang === 'hi' ? 'वर्ष' : 'Years'}</strong><span>{lang === 'hi' ? 'कार्यकाल' : 'Term'}</span></div>
                <div className="learn-stat"><strong>{lang === 'hi' ? 'प्रधानमंत्री' : 'PM'}</strong><span>{lang === 'hi' ? 'चुनता है' : 'Selects'}</span></div>
              </div>
            </div>
            <div className="learn-card">
              <div className="learn-card-icon" style={{ background: 'var(--saffron)' }}>
                <span className="material-symbols-outlined" style={{ color: '#fff' }}>domain</span>
              </div>
              <h2>{t('election_vidhan_sabha_title')}</h2>
              <p>{t('election_vidhan_sabha_desc')}</p>
              <div className="learn-stats">
                <div className="learn-stat"><strong>{lang === 'hi' ? 'भिन्न' : 'Varies'}</strong><span>{lang === 'hi' ? 'सीटें' : 'Seats'}</span></div>
                <div className="learn-stat"><strong>5 {lang === 'hi' ? 'वर्ष' : 'Years'}</strong><span>{lang === 'hi' ? 'कार्यकाल' : 'Term'}</span></div>
                <div className="learn-stat"><strong>{lang === 'hi' ? 'मुख्यमंत्री' : 'CM'}</strong><span>{lang === 'hi' ? 'चुनता है' : 'Selects'}</span></div>
              </div>
            </div>
            <div className="learn-card learn-card-tip">
              <span className="material-symbols-outlined" style={{ color: 'var(--green-india)' }}>lightbulb</span>
              <p>{lang === 'hi' ? 'लोक सभा केंद्र सरकार बनाती है, जबकि विधान सभा राज्य सरकार बनाती है। दोनों में मतदान का अधिकार 18+ भारतीय नागरिकों को है।' : 'Lok Sabha forms the central government while Vidhan Sabha forms the state government. All Indian citizens aged 18+ can vote in both elections.'}</p>
            </div>
          </div>
        )}

        {/* Candidates Tab */}
        {activeTab === 'candidates' && (
          <div className="candidates-list stagger-children" role="tabpanel">
            {candidates.map((c) => (
              <article key={c.id} className="candidate-card card">
                <div className="candidate-header">
                  <div className="candidate-avatar"><span className="material-symbols-outlined" style={{ fontSize: '32px' }}>person</span></div>
                  <div className="candidate-info">
                    <h3>{lang === 'hi' ? c.name_hi : c.name}</h3>
                    <p className="text-saffron">{lang === 'hi' ? c.party_hi : c.party}</p>
                  </div>
                  <button className="badge badge-green" aria-label="View AI summary">
                    <span className="material-symbols-outlined" style={{ fontSize: '14px' }}>psychology</span>
                    {t('candidates_ai_summary')}
                  </button>
                </div>
                <div className="candidate-stats">
                  <div className="candidate-stat"><span className="text-label">{t('candidates_assets')}</span><strong>{c.assets}</strong></div>
                  <div className="candidate-stat">
                    <span className="text-label">{t('candidates_criminal')}</span>
                    {c.criminal === 'none'
                      ? <strong className="text-green"><span className="material-symbols-outlined" style={{ fontSize: '16px', verticalAlign: 'middle' }}>check_circle</span> {t('candidates_none')}</strong>
                      : <strong className="text-amber"><span className="material-symbols-outlined" style={{ fontSize: '16px', verticalAlign: 'middle' }}>warning</span> {c.criminal} {t('candidates_pending')}</strong>}
                  </div>
                </div>
                <button className="btn btn-secondary btn-sm" style={{ width: '100%' }}>{t('candidates_view_affidavit')}</button>
              </article>
            ))}
          </div>
        )}

        {/* Manifesto Tab */}
        {activeTab === 'manifesto' && (
          <div className="manifesto-section" role="tabpanel">
            <div className="manifesto-header">
              <span className="material-symbols-outlined" style={{ color: 'var(--saffron)' }}>balance</span>
              <div><h2>{t('manifesto_title')}</h2><p className="text-muted">{t('manifesto_desc')}</p></div>
            </div>
            <div className="manifesto-topics stagger-children">
              {manifestoTopics.map((topic) => (
                <div key={topic.topic} className="manifesto-topic">
                  <div className="manifesto-topic-header">
                    <span className="material-symbols-outlined">{topic.icon}</span>
                    <h3>{lang === 'hi' ? topic.topic_hi : topic.topic}</h3>
                  </div>
                  <div className="manifesto-compare">
                    {topic.parties.map((p) => (
                      <div key={p.name} className="manifesto-party-card">
                        <span className="badge badge-navy">{p.name}</span>
                        <p>{lang === 'hi' ? p.promise_hi : p.promise}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            <button className="btn btn-primary" style={{ width: '100%', marginTop: '16px' }}>
              <span className="material-symbols-outlined">compare_arrows</span>{t('manifesto_full')}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
