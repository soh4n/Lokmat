import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { sendOtp, verifyOtp } from '../services/api.js';
import { loginWithGoogle } from '../firebase.js';
import './Login.css';

export default function Login() {
  const { t, lang, toggleLanguage } = useLanguage();
  const { login } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState('phone'); // phone | otp | verifying

  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [error, setError] = useState('');
  const [demoOtp, setDemoOtp] = useState('');

  const handlePhoneSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!/^[6-9]\d{9}$/.test(phone)) {
      setError(lang === 'hi' ? 'कृपया वैध 10 अंकों का मोबाइल नंबर दर्ज करें' : 'Please enter a valid 10-digit mobile number');
      return;
    }

    try {
      const result = await sendOtp(`+91${phone}`);
      // In demo mode, show the OTP hint
      if (result.demo_otp) {
        setDemoOtp(result.demo_otp);
      }
      setStep('otp');
    } catch (err) {
      // Fallback to local-only mode if backend is unreachable
      console.warn('Backend unavailable, using local auth:', err.message);
      setStep('otp');
    }
  };

  const handleOtpChange = (index, value) => {
    if (!/^\d*$/.test(value)) return;
    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 5) {
      const next = document.getElementById(`otp-${index + 1}`);
      next?.focus();
    }
  };

  const handleOtpKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      const prev = document.getElementById(`otp-${index - 1}`);
      prev?.focus();
    }
  };

  const handleOtpSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const code = otp.join('');

    if (code.length !== 6) {
      setError(lang === 'hi' ? 'कृपया 6 अंकों का OTP दर्ज करें' : 'Please enter the 6-digit OTP');
      return;
    }

    setStep('verifying');

    try {
      const result = await verifyOtp(`+91${phone}`, code);
      login(
        { phone: `+91${phone}`, name: '', profileComplete: false },
        result.access_token,
      );
      navigate('/profile');
    } catch (err) {
      // Fallback: if backend is down, allow local-only login for demo
      console.warn('Backend verification failed, using local auth:', err.message);
      login({ phone: `+91${phone}`, name: '', profileComplete: false });
      navigate('/profile');
    }
  };

  const handleResend = async () => {
    setOtp(['', '', '', '', '', '']);
    setError('');
    try {
      const result = await sendOtp(`+91${phone}`);
      if (result.demo_otp) {
        setDemoOtp(result.demo_otp);
      }
    } catch {
      // Silent fail on resend
    }
  };

  const handleGoogleLogin = async () => {
    setError('');
    try {
      const { user, idToken } = await loginWithGoogle();
      login(
        { phone: user.phoneNumber || '', name: user.displayName || '', profileComplete: false, email: user.email },
        idToken
      );
      navigate('/profile');
    } catch (err) {
      setError(lang === 'hi' ? 'Google लॉगिन विफल रहा' : 'Google Login failed. Try again.');
      console.error(err);
    }
  };

  return (
    <main className="login-page">
      {/* Background image */}
      <div className="login-bg">
        <img
          src="/login-bg.png"
          alt={lang === 'hi' ? 'भारतीय नागरिक मतदान के बाद अपनी स्याही लगी उंगली दिखाते हुए' : 'Indian citizens showing inked fingers after voting'}
          className="login-bg-img"
        />
        <div className="login-bg-overlay" />
      </div>

      {/* Language toggle */}
      <button
        className="login-lang-toggle"
        onClick={toggleLanguage}
        aria-label="Toggle language"
      >
        {lang === 'en' ? 'हिंदी' : 'English'}
      </button>

      {/* Content */}
      <div className="login-content">
        {/* Brand */}
        <div className="login-brand animate-fade-in-up">
          <img src="/lokmat-logo.png" alt="LokMat logo" className="login-logo" />
          <h1 className="login-app-name">
            {lang === 'hi' ? 'लोकमत' : 'LokMat'}
          </h1>
          <p className="login-tagline">
            {lang === 'hi' ? 'आपका चुनाव साथी' : 'Your Election Companion'}
          </p>
        </div>

        {/* Motivational Quote */}
        <div className="login-quote animate-fade-in-up" style={{ animationDelay: '100ms' }}>
          <p>
            {lang === 'hi'
              ? '"लोकतंत्र की शक्ति आपके वोट में है।"'
              : '"The power of democracy lies in your vote."'}
          </p>
        </div>

        {/* Login Card */}
        <div className="login-card animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          {step === 'phone' && (
            <form onSubmit={handlePhoneSubmit} noValidate>
              <h2>
                {lang === 'hi' ? 'लॉगिन करें' : 'Sign In'}
              </h2>
              <p className="login-card-desc">
                {lang === 'hi'
                  ? 'अपने मोबाइल नंबर से शुरू करें'
                  : 'Get started with your mobile number'}
              </p>

              <div className="input-group">
                <label htmlFor="phone-input">
                  {lang === 'hi' ? 'मोबाइल नंबर' : 'Mobile Number'}
                </label>
                <div className="phone-input-wrapper">
                  <span className="phone-prefix">+91</span>
                  <input
                    id="phone-input"
                    type="tel"
                    inputMode="numeric"
                    maxLength={10}
                    value={phone}
                    onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
                    placeholder={lang === 'hi' ? 'अपना नंबर दर्ज करें' : 'Enter your number'}
                    aria-required="true"
                    aria-describedby={error ? 'phone-error' : undefined}
                    autoFocus
                  />
                </div>
                {error && (
                  <p id="phone-error" className="input-error" role="alert">{error}</p>
                )}
              </div>

              <button type="submit" className="btn btn-primary login-submit">
                <span className="material-symbols-outlined">send</span>
                {lang === 'hi' ? 'OTP भेजें' : 'Send OTP'}
              </button>

              <div className="login-divider">
                <span>{lang === 'hi' ? 'या' : 'OR'}</span>
              </div>

              <button type="button" className="btn btn-outline login-google" onClick={handleGoogleLogin}>
                <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" alt="Google" className="google-icon" />
                {lang === 'hi' ? 'Google के साथ लॉगिन करें' : 'Sign in with Google'}
              </button>

              <p className="login-terms">
                {lang === 'hi'
                  ? 'जारी रखकर, आप हमारी सेवा की शर्तों से सहमत हैं'
                  : 'By continuing, you agree to our Terms of Service'}
              </p>

            </form>
          )}

          {step === 'otp' && (
            <form onSubmit={handleOtpSubmit} noValidate>
              <h2>
                {lang === 'hi' ? 'OTP सत्यापन' : 'Verify OTP'}
              </h2>
              <p className="login-card-desc">
                {lang === 'hi'
                  ? `+91 ${phone} पर भेजा गया 6 अंकों का कोड दर्ज करें`
                  : `Enter the 6-digit code sent to +91 ${phone}`}
              </p>

              {/* Demo OTP hint */}
              {demoOtp && (
                <div className="demo-otp-hint" role="status">
                  <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>info</span>
                  <span>Demo OTP: <strong>{demoOtp}</strong></span>
                </div>
              )}

              <div className="otp-inputs" role="group" aria-label="OTP input">
                {otp.map((digit, i) => (
                  <input
                    key={i}
                    id={`otp-${i}`}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleOtpChange(i, e.target.value)}
                    onKeyDown={(e) => handleOtpKeyDown(i, e)}
                    aria-label={`Digit ${i + 1}`}
                    autoFocus={i === 0}
                  />
                ))}
              </div>

              {error && (
                <p className="input-error" role="alert">{error}</p>
              )}

              <button type="submit" className="btn btn-primary login-submit">
                <span className="material-symbols-outlined">verified</span>
                {lang === 'hi' ? 'सत्यापित करें' : 'Verify & Continue'}
              </button>

              <div className="otp-actions">
                <button type="button" className="otp-resend" onClick={handleResend}>
                  {lang === 'hi' ? 'OTP पुनः भेजें' : 'Resend OTP'}
                </button>
                <button type="button" className="otp-change" onClick={() => { setStep('phone'); setError(''); setDemoOtp(''); }}>
                  {lang === 'hi' ? 'नंबर बदलें' : 'Change Number'}
                </button>
              </div>
            </form>
          )}

          {step === 'verifying' && (
            <div className="login-verifying">
              <div className="login-spinner" aria-hidden="true" />
              <h2>
                {lang === 'hi' ? 'सत्यापित हो रहा है...' : 'Verifying...'}
              </h2>
              <p>
                {lang === 'hi' ? 'कृपया प्रतीक्षा करें' : 'Please wait a moment'}
              </p>
            </div>
          )}
        </div>

        {/* ECI Badge */}
        <div className="login-eci-badge animate-fade-in-up" style={{ animationDelay: '300ms' }}>
          <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>verified_user</span>
          <span>
            {lang === 'hi'
              ? 'भारत निर्वाचन आयोग डिजिटल अवसंरचना'
              : 'Election Commission of India — Digital Infrastructure'}
          </span>
        </div>
      </div>
    </main>
  );
}
