import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import './MyVote.css';

export default function MyVote() {
  const { t, lang } = useLanguage();
  const { user, isProfileComplete } = useAuth();

  // If profile not complete, show prompt
  if (!isProfileComplete) {
    return (
      <main className="page" role="main">
        <div className="page-content">
          <div className="myvote-incomplete animate-fade-in-up">
            <div className="icon-circle icon-circle-saffron" style={{ width: '64px', height: '64px' }}>
              <span className="material-symbols-outlined" style={{ fontSize: '32px' }}>assignment_ind</span>
            </div>
            <h1>{lang === 'hi' ? 'पहले अपनी प्रोफ़ाइल पूरी करें' : 'Complete Your Profile First'}</h1>
            <p>
              {lang === 'hi'
                ? 'मतदाता पर्ची प्राप्त करने के लिए कृपया अपना EPIC नंबर और अन्य विवरण भरें।'
                : 'Please fill in your EPIC number and other details to access your voter slip.'}
            </p>
            <Link to="/profile" className="btn btn-primary">
              <span className="material-symbols-outlined">edit</span>
              {lang === 'hi' ? 'प्रोफ़ाइल भरें' : 'Fill Profile'}
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="page" role="main">
      <div className="page-content stagger-children">
        {/* Voter Slip */}
        <section className="voter-slip-card" aria-label="Voter Information Slip">
          <div className="voter-slip-header">
            <span className="text-label" style={{ color: 'var(--on-surface-variant)' }}>
              {t('voter_slip_eci')}
            </span>
            <span className="badge badge-green">{t('voter_slip_status')}</span>
          </div>
          <h1 className="voter-slip-title">{t('voter_slip_title')}</h1>

          <div className="divider" />

          <div className="voter-slip-logo">
            <img src="/lokmat-logo.png" alt="LokMat logo" width="80" height="80" />
          </div>

          <div className="voter-slip-grid">
            <div className="voter-field">
              <span className="text-label">{t('voter_slip_epic')}</span>
              <strong>{user?.epicNo || 'N/A'}</strong>
            </div>
            <div className="voter-field">
              <span className="text-label">{t('voter_slip_name')}</span>
              <strong>{lang === 'hi' ? (user?.fullNameHi || user?.fullName || 'N/A') : (user?.fullName || 'N/A')}</strong>
            </div>
            <div className="voter-field">
              <span className="text-label">{t('voter_slip_part')}</span>
              <strong>{user?.partNo ? `${user.partNo} - ${user.constituency || ''}` : 'N/A'}</strong>
            </div>
            <div className="voter-field">
              <span className="text-label">{t('voter_slip_serial')}</span>
              <strong>{user?.serialNo || 'N/A'}</strong>
            </div>
          </div>

          <div className="voter-slip-extra-grid">
            <div className="voter-field">
              <span className="text-label">{lang === 'hi' ? 'पिता/पति का नाम' : "Father's/Husband's Name"}</span>
              <strong>{user?.fatherName || 'N/A'}</strong>
            </div>
            <div className="voter-field">
              <span className="text-label">{lang === 'hi' ? 'राज्य' : 'State'}</span>
              <strong>{user?.state || 'N/A'}</strong>
            </div>
          </div>

          <div className="voter-slip-date">
            <span className="text-label">{t('voter_slip_date')}</span>
            <strong className="text-saffron">May 15, 2024 • 07:00 AM - 06:00 PM</strong>
          </div>

          <div className="voter-slip-actions">
            <button className="btn btn-primary">
              <span className="material-symbols-outlined">download</span>
              {t('voter_slip_download')}
            </button>
            <button className="btn btn-secondary">
              <span className="material-symbols-outlined">share</span>
              {t('voter_slip_share')}
            </button>
          </div>

          <div className="voter-slip-edit">
            <Link to="/profile" className="edit-profile-link">
              <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>edit</span>
              {lang === 'hi' ? 'विवरण संपादित करें' : 'Edit Details'}
            </Link>
          </div>
        </section>

        {/* Assigned Polling Booth */}
        <section className="booth-section" aria-label="Assigned Polling Booth">
          <h2 className="section-title">{t('booth_title')}</h2>

          <div className="booth-map-placeholder">
            <div className="booth-map-overlay">
              <span className="material-symbols-outlined" style={{ fontSize: '48px', color: 'var(--saffron)' }}>
                location_on
              </span>
              <p>{lang === 'hi' ? 'मानचित्र लोड हो रहा है...' : 'Map loading...'}</p>
            </div>
            <div className="booth-walk-badge">
              <span className="material-symbols-outlined">directions_walk</span>
              12 {t('booth_walk_time')}
            </div>
          </div>

          <div className="booth-info">
            <h3>{user?.constituency ? `${user.constituency} High School` : 'Central District High School'}</h3>
            <p>{user?.address || 'Room No. 4, Ground Floor, Main Building'}</p>
          </div>

          <div className="booth-queue-status">
            <div className="queue-status-header">
              <span className="material-symbols-outlined" style={{ color: 'var(--green-india)' }}>
                groups
              </span>
              <span className="text-label" style={{ color: 'var(--green-india)' }}>
                {t('booth_live_queue')}
              </span>
            </div>
            <div className="queue-status-body">
              <span className="queue-time">~15</span>
              <span>{t('booth_wait_time')}</span>
              <span className="queue-dot pulse" />
            </div>
          </div>

          <a
            href="https://maps.google.com"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-outline"
            style={{ width: '100%', justifyContent: 'center' }}
          >
            <span className="material-symbols-outlined">navigation</span>
            {t('booth_get_directions')}
          </a>
        </section>
      </div>
    </main>
  );
}
