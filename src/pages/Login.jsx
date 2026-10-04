import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import Logo from '../components/Logo';
import { ArrowLeft, LogIn, Lock, Eye, EyeOff } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const [formData, setFormData] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (errorMsg) setErrorMsg('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    try {
      const res = await api.post('/auth/login', formData);
      login(res.data.user);
      navigate('/dashboard');
    } catch (err) {
      if (err.response && err.response.data) {
        const data = err.response.data;
        if (data.requires_otp) {
          // Redirect unverified account to OTP verification
          navigate('/verify-otp', { state: { email: data.email } });
        } else if (data.error) {
          setErrorMsg(data.error);
        } else {
          setErrorMsg('Authentication failed. Check your email and password.');
        }
      } else {
        setErrorMsg('Server connection failed.');
      }
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

      <div className="card" style={{ width: '100%', maxWidth: '420px' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <Logo size={42} className="text-danger-red" />
          <h2 style={{ fontSize: '1.75rem', marginTop: '0.5rem' }}>Sign In to Deptrix</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Enter your email and password to access dashboard scans
          </p>
        </div>

        {errorMsg && (
          <div style={{
            backgroundColor: 'var(--danger-red-bg)',
            border: '1px solid var(--danger-red)',
            color: 'var(--danger-red)',
            padding: '0.75rem',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '1.25rem',
            fontSize: '0.88rem'
          }}>
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="login-email">Email Address</label>
            <input
              id="login-email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="form-control"
              placeholder="name@company.com"
              required
            />
          </div>

          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label className="form-label" htmlFor="login-password">Password</label>
              <Link to="/forgot-password" style={{ fontSize: '0.82rem', color: 'var(--accent-gold)' }}>
                Forgot password?
              </Link>
            </div>
            <div style={{ position: 'relative' }}>
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="form-control"
                placeholder="••••••••"
                style={{ paddingRight: '2.5rem' }}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '0.75rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0.25rem'
                }}
                title={showPassword ? "Hide password" : "Show password"}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '1rem', padding: '0.8rem' }}
          >
            {loading ? 'Authenticating...' : <><LogIn size={16} /> Sign In</>}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          Don't have an account? <Link to="/signup-step1" style={{ color: 'var(--accent-gold)' }}>Sign Up</Link>
        </div>
      </div>
    </div>
  );
}
