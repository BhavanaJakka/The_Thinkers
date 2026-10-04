import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import Logo from '../components/Logo';
import { ArrowLeft, RefreshCw, CheckCircle2, ShieldAlert } from 'lucide-react';

export default function SignUpStep1() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirm_password: '',
    mobile: '',
    captcha_answer: '',
    captcha_token: ''
  });

  const [captchaText, setCaptchaText] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [liveValidation, setLiveValidation] = useState({
    length: false,
    upper: false,
    lower: false,
    digit: false,
    symbol: false,
    match: false,
    mobile: false,
    name: false
  });

  const fetchCaptcha = async () => {
    try {
      const res = await api.get('/auth/captcha');
      setCaptchaText(res.data.captcha_text);
      setFormData(prev => ({ ...prev, captcha_token: res.data.captcha_token }));
    } catch (err) {
      console.error('Failed to fetch captcha');
    }
  };

  useEffect(() => {
    fetchCaptcha();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const updated = { ...formData, [name]: value };
    setFormData(updated);

    // Live Validation Updates
    if (name === 'password' || name === 'confirm_password') {
      const pwd = updated.password;
      setLiveValidation(prev => ({
        ...prev,
        length: pwd.length >= 8,
        upper: /[A-Z]/.test(pwd),
        lower: /[a-z]/.test(pwd),
        digit: /\d/.test(pwd),
        symbol: /[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]/.test(pwd),
        match: pwd !== '' && pwd === updated.confirm_password
      }));
    }

    if (name === 'mobile') {
      setLiveValidation(prev => ({ ...prev, mobile: /^\d{10}$/.test(value) }));
    }

    if (name === 'name') {
      setLiveValidation(prev => ({ ...prev, name: /^[A-Za-z\s]{2,50}$/.test(value) }));
    }

    if (errors[name]) {
      setErrors({ ...errors, [name]: null });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      const res = await api.post('/auth/signup-step1', formData);
      // Navigate to Step 2 with email
      navigate('/signup-step2', { state: { email: formData.email } });
    } catch (err) {
      if (err.response && err.response.data) {
        if (err.response.data.errors) {
          setErrors(err.response.data.errors);
        } else if (err.response.data.error) {
          setErrors({ general: err.response.data.error });
        }
      } else {
        setErrors({ general: 'Registration failed. Please check inputs.' });
      }
      fetchCaptcha(); // Refresh captcha on failure
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem 1rem'
    }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
          <ArrowLeft size={16} /> Back to main page
        </Link>
      </div>

      <div className="card" style={{ width: '100%', maxWidth: '480px' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <Logo size={40} className="text-danger-red" />
          <h2 style={{ fontSize: '1.75rem', marginTop: '0.5rem' }}>Create Deptrix Account</h2>
          <span style={{ color: 'var(--accent-gold)', fontSize: '0.85rem', fontWeight: 600 }}>
            STEP 1 OF 2: ACCOUNT DETAILS
          </span>
        </div>

        {errors.general && (
          <div style={{
            backgroundColor: 'var(--danger-red-bg)',
            border: '1px solid var(--danger-red)',
            color: 'var(--danger-red)',
            padding: '0.75rem',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '1rem',
            fontSize: '0.88rem'
          }}>
            {errors.general}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Name */}
          <div className="form-group">
            <label className="form-label" htmlFor="reg-name">Full Name</label>
            <input
              id="reg-name"
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="form-control"
              placeholder="e.g. Omkar Nalawade"
              required
            />
            {errors.name && <span className="error-text">{errors.name[0]}</span>}
          </div>

          {/* Email */}
          <div className="form-group">
            <label className="form-label" htmlFor="reg-email">Email Address</label>
            <input
              id="reg-email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="form-control"
              placeholder="name@company.com"
              required
            />
            {errors.email && <span className="error-text">{errors.email[0]}</span>}
          </div>

          {/* Mobile */}
          <div className="form-group">
            <label className="form-label" htmlFor="reg-mobile">Mobile Number (10 Digits)</label>
            <input
              id="reg-mobile"
              type="text"
              name="mobile"
              value={formData.mobile}
              onChange={handleChange}
              className="form-control"
              placeholder="9876543210"
              maxLength={10}
              required
            />
            {errors.mobile && <span className="error-text">{errors.mobile[0]}</span>}
          </div>

          {/* Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="reg-password">Password</label>
            <input
              id="reg-password"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="form-control"
              placeholder="Min 8 chars, 1 upper, 1 lower, 1 digit, 1 symbol"
              required
            />
            {errors.password && <span className="error-text">{errors.password[0]}</span>}
          </div>

          {/* Confirm Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="reg-confirm">Confirm Password</label>
            <input
              id="reg-confirm"
              type="password"
              name="confirm_password"
              value={formData.confirm_password}
              onChange={handleChange}
              className="form-control"
              placeholder="Re-enter password"
              required
            />
            {errors.confirm_password && <span className="error-text">{errors.confirm_password[0]}</span>}
          </div>

          {/* Inline Live Password Criteria */}
          <div style={{
            backgroundColor: '#120d0b',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-sm)',
            padding: '0.75rem',
            marginBottom: '1.25rem',
            fontSize: '0.8rem'
          }}>
            <div style={{ color: 'var(--text-muted)', fontWeight: 600, marginBottom: '0.4rem' }}>Live Password Criteria:</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.25rem' }}>
              <span style={{ color: liveValidation.length ? '#30a46c' : 'var(--text-dim)' }}>✓ Min 8 Characters</span>
              <span style={{ color: liveValidation.upper ? '#30a46c' : 'var(--text-dim)' }}>✓ 1 Uppercase Letter</span>
              <span style={{ color: liveValidation.lower ? '#30a46c' : 'var(--text-dim)' }}>✓ 1 Lowercase Letter</span>
              <span style={{ color: liveValidation.digit ? '#30a46c' : 'var(--text-dim)' }}>✓ 1 Digit</span>
              <span style={{ color: liveValidation.symbol ? '#30a46c' : 'var(--text-dim)' }}>✓ 1 Special Symbol</span>
              <span style={{ color: liveValidation.match ? '#30a46c' : 'var(--text-dim)' }}>✓ Passwords Match</span>
            </div>
          </div>

          {/* Server Captcha */}
          <div className="form-group">
            <label className="form-label" htmlFor="reg-captcha">Security Captcha</label>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <div style={{
                backgroundColor: 'var(--accent-gold-glow)',
                border: '1px dashed var(--accent-gold)',
                color: 'var(--accent-gold)',
                padding: '0.6rem 1rem',
                borderRadius: 'var(--radius-sm)',
                fontWeight: 700,
                fontSize: '1.1rem',
                letterSpacing: '2px'
              }}>
                {captchaText || 'Loading...'}
              </div>
              <button
                type="button"
                onClick={fetchCaptcha}
                className="btn btn-outline"
                style={{ padding: '0.6rem' }}
                title="Refresh Captcha"
              >
                <RefreshCw size={16} />
              </button>
              <input
                id="reg-captcha"
                type="text"
                name="captcha_answer"
                value={formData.captcha_answer}
                onChange={handleChange}
                className="form-control"
                placeholder="Result"
                required
                style={{ flex: 1 }}
              />
            </div>
            {errors.captcha_answer && <span className="error-text">{errors.captcha_answer[0]}</span>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '0.5rem', padding: '0.8rem' }}
          >
            {loading ? 'Validating...' : 'Continue to Security Question (Step 2)'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--accent-gold)' }}>Sign In</Link>
        </div>
      </div>
    </div>
  );
}
