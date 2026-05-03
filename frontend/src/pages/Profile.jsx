import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import './Profile.css';

const STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan',
  'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh',
  'Uttarakhand', 'West Bengal',
];

export default function Profile() {
  const { t, lang } = useLanguage();
  const { user, updateProfile, logout, isProfileComplete } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    fullName: user?.fullName || '',
    fullNameHi: user?.fullNameHi || '',
    epicNo: user?.epicNo || '',
    dob: user?.dob || '',
    gender: user?.gender || '',
    fatherName: user?.fatherName || '',
    address: user?.address || '',
    state: user?.state || '',
    constituency: user?.constituency || '',
    partNo: user?.partNo || '',
    serialNo: user?.serialNo || '',
  });

  const [errors, setErrors] = useState({});
  const [saved, setSaved] = useState(false);

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: '' }));
    setSaved(false);
  };

  const validate = () => {
    const newErrors = {};
    if (!form.fullName.trim()) newErrors.fullName = lang === 'hi' ? 'नाम आवश्यक है' : 'Full name is required';
    if (!form.epicNo.trim()) newErrors.epicNo = lang === 'hi' ? 'EPIC नंबर आवश्यक है' : 'EPIC number is required';
    if (form.epicNo && !/^[A-Z]{3}\d{7}$/i.test(form.epicNo.trim())) {
      newErrors.epicNo = lang === 'hi' ? 'अमान्य EPIC प्रारूप (उदा: ABC1234567)' : 'Invalid EPIC format (e.g. ABC1234567)';
    }
    if (!form.dob) newErrors.dob = lang === 'hi' ? 'जन्म तिथि आवश्यक है' : 'Date of birth is required';
    if (!form.gender) newErrors.gender = lang === 'hi' ? 'लिंग चुनें' : 'Select gender';
    if (!form.state) newErrors.state = lang === 'hi' ? 'राज्य चुनें' : 'Select state';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;

    updateProfile(form);
    setSaved(true);

    if (!isProfileComplete) {
      // First time profile completion — go to home
      setTimeout(() => navigate('/'), 1200);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <main className="page" role="main">
      <div className="page-content">
        {/* Profile Header */}
        <div className="profile-header stagger-children">
          <div className="profile-avatar-section">
            <div className="profile-avatar">
              <span className="material-symbols-outlined" style={{ fontSize: '40px' }}>
                person
              </span>
            </div>
            <div className="profile-name-section">
              <h1>{user?.fullName || (lang === 'hi' ? 'अपनी प्रोफ़ाइल बनाएं' : 'Complete Your Profile')}</h1>
              <p className="text-muted">{user?.phone}</p>
              {isProfileComplete && (
                <span className="badge badge-green">
                  <span className="material-symbols-outlined" style={{ fontSize: '12px' }}>check_circle</span>
                  {lang === 'hi' ? 'सत्यापित' : 'Verified'}
                </span>
              )}
            </div>
          </div>

          {!isProfileComplete && (
            <div className="profile-banner">
              <span className="material-symbols-outlined">info</span>
              <p>
                {lang === 'hi'
                  ? 'मतदाता पर्ची प्राप्त करने के लिए कृपया अपनी जानकारी भरें।'
                  : 'Please fill in your details to access your voter slip.'}
              </p>
            </div>
          )}
        </div>

        {/* Saved Success */}
        {saved && (
          <div className="profile-success" role="alert" aria-live="assertive">
            <span className="material-symbols-outlined">check_circle</span>
            <p>{lang === 'hi' ? 'प्रोफ़ाइल सफलतापूर्वक सहेजा गया!' : 'Profile saved successfully!'}</p>
          </div>
        )}

        {/* Profile Form */}
        <form className="profile-form" onSubmit={handleSubmit} noValidate>
          {/* Personal Info Section */}
          <fieldset className="profile-fieldset">
            <legend>
              <span className="material-symbols-outlined">person</span>
              {lang === 'hi' ? 'व्यक्तिगत जानकारी' : 'Personal Information'}
            </legend>

            <div className="form-grid">
              <div className="form-field">
                <label htmlFor="fullName">{lang === 'hi' ? 'पूरा नाम (अंग्रेजी)' : 'Full Name (English)'} *</label>
                <input
                  id="fullName"
                  type="text"
                  value={form.fullName}
                  onChange={(e) => handleChange('fullName', e.target.value)}
                  placeholder="e.g. Aarav Sharma"
                  aria-required="true"
                  aria-describedby={errors.fullName ? 'fullName-error' : undefined}
                />
                {errors.fullName && <p id="fullName-error" className="field-error">{errors.fullName}</p>}
              </div>

              <div className="form-field">
                <label htmlFor="fullNameHi">{lang === 'hi' ? 'पूरा नाम (हिंदी)' : 'Full Name (Hindi)'}</label>
                <input
                  id="fullNameHi"
                  type="text"
                  value={form.fullNameHi}
                  onChange={(e) => handleChange('fullNameHi', e.target.value)}
                  placeholder="उदा: आरव शर्मा"
                />
              </div>

              <div className="form-field">
                <label htmlFor="dob">{lang === 'hi' ? 'जन्म तिथि' : 'Date of Birth'} *</label>
                <input
                  id="dob"
                  type="date"
                  value={form.dob}
                  onChange={(e) => handleChange('dob', e.target.value)}
                  aria-required="true"
                  aria-describedby={errors.dob ? 'dob-error' : undefined}
                />
                {errors.dob && <p id="dob-error" className="field-error">{errors.dob}</p>}
              </div>

              <div className="form-field">
                <label htmlFor="gender">{lang === 'hi' ? 'लिंग' : 'Gender'} *</label>
                <select
                  id="gender"
                  value={form.gender}
                  onChange={(e) => handleChange('gender', e.target.value)}
                  aria-required="true"
                  aria-describedby={errors.gender ? 'gender-error' : undefined}
                >
                  <option value="">{lang === 'hi' ? '-- चुनें --' : '-- Select --'}</option>
                  <option value="male">{lang === 'hi' ? 'पुरुष' : 'Male'}</option>
                  <option value="female">{lang === 'hi' ? 'महिला' : 'Female'}</option>
                  <option value="other">{lang === 'hi' ? 'अन्य' : 'Other'}</option>
                </select>
                {errors.gender && <p id="gender-error" className="field-error">{errors.gender}</p>}
              </div>

              <div className="form-field form-field-full">
                <label htmlFor="fatherName">{lang === 'hi' ? 'पिता/पति का नाम' : "Father's / Husband's Name"}</label>
                <input
                  id="fatherName"
                  type="text"
                  value={form.fatherName}
                  onChange={(e) => handleChange('fatherName', e.target.value)}
                />
              </div>
            </div>
          </fieldset>

          {/* Voter Details Section */}
          <fieldset className="profile-fieldset">
            <legend>
              <span className="material-symbols-outlined">how_to_vote</span>
              {lang === 'hi' ? 'मतदाता विवरण' : 'Voter Details'}
            </legend>

            <div className="form-grid">
              <div className="form-field">
                <label htmlFor="epicNo">{lang === 'hi' ? 'EPIC / मतदाता पहचान पत्र नंबर' : 'EPIC / Voter ID No.'} *</label>
                <input
                  id="epicNo"
                  type="text"
                  value={form.epicNo}
                  onChange={(e) => handleChange('epicNo', e.target.value.toUpperCase())}
                  placeholder="ABC1234567"
                  maxLength={10}
                  aria-required="true"
                  aria-describedby={errors.epicNo ? 'epicNo-error' : undefined}
                  style={{ textTransform: 'uppercase', letterSpacing: '1px' }}
                />
                {errors.epicNo && <p id="epicNo-error" className="field-error">{errors.epicNo}</p>}
              </div>

              <div className="form-field">
                <label htmlFor="state">{lang === 'hi' ? 'राज्य' : 'State'} *</label>
                <select
                  id="state"
                  value={form.state}
                  onChange={(e) => handleChange('state', e.target.value)}
                  aria-required="true"
                  aria-describedby={errors.state ? 'state-error' : undefined}
                >
                  <option value="">{lang === 'hi' ? '-- राज्य चुनें --' : '-- Select State --'}</option>
                  {STATES.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
                {errors.state && <p id="state-error" className="field-error">{errors.state}</p>}
              </div>

              <div className="form-field">
                <label htmlFor="constituency">{lang === 'hi' ? 'निर्वाचन क्षेत्र' : 'Constituency'}</label>
                <input
                  id="constituency"
                  type="text"
                  value={form.constituency}
                  onChange={(e) => handleChange('constituency', e.target.value)}
                  placeholder={lang === 'hi' ? 'उदा: नई दिल्ली' : 'e.g. New Delhi'}
                />
              </div>

              <div className="form-field">
                <label htmlFor="partNo">{lang === 'hi' ? 'भाग संख्या' : 'Part Number'}</label>
                <input
                  id="partNo"
                  type="text"
                  value={form.partNo}
                  onChange={(e) => handleChange('partNo', e.target.value)}
                  placeholder="42"
                />
              </div>

              <div className="form-field">
                <label htmlFor="serialNo">{lang === 'hi' ? 'क्रम संख्या' : 'Serial Number'}</label>
                <input
                  id="serialNo"
                  type="text"
                  value={form.serialNo}
                  onChange={(e) => handleChange('serialNo', e.target.value)}
                  placeholder="874"
                />
              </div>

              <div className="form-field form-field-full">
                <label htmlFor="address">{lang === 'hi' ? 'पता' : 'Address'}</label>
                <textarea
                  id="address"
                  rows={3}
                  value={form.address}
                  onChange={(e) => handleChange('address', e.target.value)}
                  placeholder={lang === 'hi' ? 'अपना पूरा पता दर्ज करें' : 'Enter your full address'}
                />
              </div>
            </div>
          </fieldset>

          {/* Actions */}
          <div className="profile-actions">
            <button type="submit" className="btn btn-primary">
              <span className="material-symbols-outlined">save</span>
              {lang === 'hi' ? 'प्रोफ़ाइल सहेजें' : 'Save Profile'}
            </button>
          </div>
        </form>

        {/* Logout */}
        <div className="profile-logout-section">
          <button className="btn btn-secondary" onClick={handleLogout}>
            <span className="material-symbols-outlined">logout</span>
            {lang === 'hi' ? 'लॉग आउट करें' : 'Log Out'}
          </button>
        </div>
      </div>
    </main>
  );
}
