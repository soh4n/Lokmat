import { NavLink } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext.jsx';
import './BottomNav.css';

export default function BottomNav() {
  const { t } = useLanguage();

  const items = [
    { path: '/', label: 'nav_home', icon: 'home' },
    { path: '/my-vote', label: 'nav_booth', icon: 'location_on' },
    { path: '/sos', label: 'nav_sos', icon: 'emergency', isSOS: true },
    { path: '/ai-guide', label: 'nav_ai_guide', icon: 'smart_toy' },
    { path: '/profile', label: 'profile', icon: 'person', isProfile: true },
  ];

  return (
    <nav className="bottom-nav" aria-label="Mobile navigation">
      {items.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className={({ isActive }) =>
            `bottom-nav-item ${isActive ? 'active' : ''} ${item.isSOS ? 'sos-item' : ''}`
          }
          aria-label={item.isProfile ? 'Profile' : t(item.label)}
        >
          <span
            className="material-symbols-outlined bottom-nav-icon"
            style={item.path === '/' || item.isSOS ? { fontVariationSettings: "'FILL' 1" } : undefined}
          >
            {item.icon}
          </span>
          <span className="bottom-nav-label">
            {item.isProfile ? (t('lang_toggle').includes('हिंदी') ? 'Profile' : 'प्रोफ़ाइल') : t(item.label)}
          </span>
        </NavLink>
      ))}
    </nav>
  );
}
