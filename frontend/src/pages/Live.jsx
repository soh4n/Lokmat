import { useLanguage } from '../context/LanguageContext.jsx';
import './Live.css';

const parkingSpots = [
  { name: 'Main School Ground', distance: '50m', status: 'full', spots: 0 },
  { name: 'Community Center', distance: '200m', status: 'available', spots: 45, recommended: true },
  { name: 'Street Parking East', distance: '350m', status: 'filling', spots: 12 },
];

export default function Live() {
  const { t, lang } = useLanguage();

  return (
    <main className="page" role="main">
      <div className="page-content stagger-children">
        {/* Header */}
        <div className="live-header">
          <div>
            <div className="live-badge">
              <span className="live-dot" />
              <span className="text-label" style={{ color: 'var(--green-india)' }}>
                {t('live_title')}
              </span>
            </div>
            <h1 className="section-title" style={{ marginBottom: '4px' }}>
              Booth 42 - Kendriya Vidyalaya
            </h1>
            <p className="text-muted">Vasant Vihar, New Delhi</p>
          </div>
          <div className="weather-chip">
            <span className="material-symbols-outlined">wb_sunny</span>
            <div>
              <strong>32°C</strong>
              <span>Clear, Sunny</span>
            </div>
          </div>
        </div>

        {/* Queue + Best Time Row */}
        <div className="live-grid">
          {/* Queue Status */}
          <section className="queue-card card" aria-label="Queue status">
            <h2>{t('live_queue_title')}</h2>
            <div className="queue-big-number">
              <span className="queue-num">15</span>
              <div>
                <span>{lang === 'hi' ? 'मिनट प्रतीक्षा समय' : 'mins wait time'}</span>
                <p className="text-muted" style={{ fontSize: '12px' }}>{t('live_queue_estimated')}</p>
              </div>
            </div>

            <div className="queue-scale">
              <div className="queue-scale-bar">
                <div className="queue-scale-fill" style={{ width: '30%' }} />
              </div>
              <div className="queue-scale-labels">
                <span>{t('live_queue_short')}</span>
                <span>{t('live_queue_moderate')}</span>
                <span>{t('live_queue_long')}</span>
              </div>
            </div>
          </section>

          {/* Best Time */}
          <section className="best-time-card card" aria-label="Best time to vote">
            <h2>
              <span className="material-symbols-outlined" style={{ color: 'var(--saffron)', verticalAlign: 'middle' }}>
                auto_awesome
              </span>
              {' '}{t('live_best_time')}
            </h2>
            <div className="bar-chart">
              <div className="bar-item">
                <div className="bar" style={{ height: '40%', background: 'var(--green-muted)' }} />
                <span>8AM</span>
              </div>
              <div className="bar-item">
                <div className="bar" style={{ height: '65%', background: 'var(--green-india)' }} />
                <span>10AM</span>
              </div>
              <div className="bar-item">
                <div className="bar" style={{ height: '90%', background: 'var(--error)' }} />
                <span>12PM</span>
              </div>
              <div className="bar-item">
                <div className="bar" style={{ height: '70%', background: 'var(--amber)' }} />
                <span>2PM</span>
              </div>
              <div className="bar-item">
                <div className="bar" style={{ height: '35%', background: 'var(--green-muted)' }} />
                <span>4PM</span>
              </div>
            </div>
            <p style={{ fontSize: '13px', marginTop: '12px' }}>
              <strong>{t('live_recommendation')}</strong>{' '}
              <span className="text-green" style={{ fontWeight: 600 }}>{t('live_come_between')}</span>{' '}
              {t('live_to_avoid')}
            </p>
          </section>
        </div>

        {/* Parking Guide */}
        <section className="parking-section" aria-label="Parking guide">
          <div className="parking-header">
            <h2>
              <span className="material-symbols-outlined" style={{ color: 'var(--navy)', verticalAlign: 'middle' }}>
                local_parking
              </span>
              {' '}{t('live_parking')}
            </h2>
            <span className="badge badge-navy">{t('live_parking_updates')}</span>
          </div>

          <div className="parking-grid">
            {parkingSpots.map((spot) => (
              <div key={spot.name} className={`parking-card card ${spot.recommended ? 'parking-recommended' : ''}`}>
                <div className="parking-card-header">
                  <h3>{spot.name}</h3>
                  <span className={`badge ${
                    spot.status === 'full' ? 'badge-error' :
                    spot.status === 'available' ? 'badge-green' :
                    'badge-amber'
                  }`}>
                    {spot.status === 'full' ? t('live_full') :
                     spot.status === 'available' ? t('live_available') :
                     t('live_filling')}
                  </span>
                </div>

                <div className="parking-distance">
                  <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>directions_walk</span>
                  {spot.distance} {t('live_away')}
                </div>

                {spot.spots > 0 && (
                  <>
                    <div className="progress-bar" style={{ marginTop: '8px' }}>
                      <div className="progress-bar-fill" style={{
                        width: `${spot.status === 'filling' ? '75%' : '40%'}`,
                        background: spot.status === 'filling' ? 'var(--amber)' : 'var(--green-india)'
                      }} />
                    </div>
                    <span className="parking-spots">{spot.spots} {t('live_spots_left')}</span>
                  </>
                )}

                {spot.recommended && (
                  <span className="badge badge-green" style={{ marginTop: '8px' }}>
                    {t('live_recommended')}
                  </span>
                )}
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
