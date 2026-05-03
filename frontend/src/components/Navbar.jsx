import { Link, useLocation } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import './Navbar.css';

export default function Navbar() {
  const { t, toggleLanguage } = useLanguage();
  const { user } = useAuth();
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'nav_home' },
    { path: '/my-vote', label: 'nav_my_vote' },
    { path: '/election', label: 'nav_election' },
    { path: '/live', label: 'nav_live' },
    { path: '/volunteer', label: 'nav_volunteer' },
  ];

  // Get user initials for avatar
  const initials = user?.fullName
    ? user.fullName.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : '?';

  return (
    <header className="navbar" role="banner">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand" aria-label="LokMat Home">
          <img
            src="/lokmat-logo.png"
            alt="LokMat — voting hand logo"
            className="navbar-logo"
            width="36"
            height="36"
          />
          <span className="navbar-title">LokMat</span>
        </Link>

        <nav className="navbar-links" aria-label="Main navigation">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`navbar-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              {t(item.label)}
            </Link>
          ))}
        </nav>

        <div className="navbar-actions">
          <button
            className="lang-toggle"
            onClick={toggleLanguage}
            aria-label="Toggle language between English and Hindi"
          >
            {t('lang_toggle')}
          </button>

          <Link to="/sos" className="sos-badge" aria-label="Emergency SOS">
            SOS
          </Link>

          <Link
            to="/profile"
            className={`profile-pill ${location.pathname === '/profile' ? 'active' : ''}`}
            aria-label="User profile"
          >
            <span className="profile-pill-avatar">{initials}</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
