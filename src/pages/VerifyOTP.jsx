import React, { useState, useContext } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import Logo from '../components/Logo';
import { ArrowLeft, KeyRound, CheckCircle } from 'lucide-react';

export default function VerifyOTP() {
  const location = useLocation();
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const email = location.state?.email || '';
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [infoMsg, setInfoMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    setInfoMsg('');

    try {
      const res = await api.post('/auth/verify-otp', { email, otp });
      login(res.data.user);
      navigate('/dashboard');
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setErrorMsg(err.response.data.error);
      } else {
        setErrorMsg('Invalid OTP verification code.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResending(true);
    setErrorMsg('');
    setInfoMsg('');

    try {
      const res = await api.post('/auth/resend-otp', { email, purpose: 'VERIFY_ACCOUNT' });
      setInfoMsg(res.data.message);
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setErrorMsg(err.response.data.error);
      } else {
        setErrorMsg('Failed to resend OTP. Please wait before trying again.');
      }
    } finally {
      setResending(false);
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

      <div className="card" style={{ width: '100%', maxWidth: '440px' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <Logo size={40} className="text-danger-red" />
          <h2 style={{ fontSize: '1.75rem', marginTop: '0.5rem' }}>Verify Email OTP</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.4rem' }}>
            We sent a 6-digit OTP code to <strong>{email}</strong>
          </p>
        </div>

        {errorMsg && (
          <div style={{
            backgroundColor: 'var(--danger-red-bg)',
            border: '1px solid var(--danger-red)',
            color: 'var(--danger-red)',
            padding: '0.75rem',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '1rem',
            fontSize: '0.88rem'
          }}>
            {errorMsg}
          </div>
        )}

        {infoMsg && (
          <div style={{
            backgroundColor: 'var(--success-green-bg)',
            border: '1px solid var(--success-green)',
            color: 'var(--success-green)',
            padding: '0.75rem',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '1rem',
            fontSize: '0.88rem'
          }}>
            {infoMsg}
          </div>
        )}

        <form onSubmit={handleVerify}>
          <div className="form-group">
            <label className="form-label" htmlFor="otp-input" style={{ textAlign: 'center', display: 'block' }}>
              6-Digit OTP Code
            </label>
            <input
              id="otp-input"
              type="text"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
              className="form-control"
              placeholder="000000"
              maxLength={6}
              style={{
                textAlign: 'center',
                letterSpacing: '8px',
                fontSize: '1.5rem',
                fontWeight: 'bold',
                fontFamily: 'monospace'
              }}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading || otp.length !== 6}
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '1rem', padding: '0.8rem' }}
          >
            {loading ? 'Verifying...' : 'Verify OTP & Activate Account'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.88rem' }}>
          Didn't receive the email?{' '}
          <button
            type="button"
            onClick={handleResend}
            disabled={resending}
            style={{ background: 'none', border: 'none', color: 'var(--accent-gold)', cursor: 'pointer', fontWeight: 600 }}
          >
            {resending ? 'Resending...' : 'Resend OTP (60s cooldown)'}
          </button>
        </div>
      </div>
    </div>
  );
}
