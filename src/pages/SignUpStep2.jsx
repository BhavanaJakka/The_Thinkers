import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';
import Logo from '../components/Logo';
import { ArrowLeft, ShieldQuestion } from 'lucide-react';

export default function SignUpStep2() {
  const location = useLocation();
  const navigate = useNavigate();
  const email = location.state?.email || '';

  const [questions, setQuestions] = useState([]);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (!email) {
      navigate('/signup-step1');
      return;
    }
    const fetchQuestions = async () => {
      try {
        const res = await api.get('/auth/security-questions');
        setQuestions(res.data.questions);
      } catch (err) {
        console.error(err);
      }
    };
    fetchQuestions();
  }, [email, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      await api.post('/auth/signup-step2', {
        email,
        question_index: parseInt(questionIndex, 10),
        answer
      });
      // Navigate to OTP verification page
      navigate('/verify-otp', { state: { email, purpose: 'VERIFY_ACCOUNT' } });
    } catch (err) {
      if (err.response && err.response.data && err.response.data.errors) {
        setErrors(err.response.data.errors);
      } else if (err.response && err.response.data && err.response.data.error) {
        setErrors({ general: err.response.data.error });
      } else {
        setErrors({ general: 'Failed to save security profile.' });
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

      <div className="card" style={{ width: '100%', maxWidth: '480px' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <Logo size={40} className="text-danger-red" />
          <h2 style={{ fontSize: '1.75rem', marginTop: '0.5rem' }}>Security Question</h2>
          <span style={{ color: 'var(--accent-gold)', fontSize: '0.85rem', fontWeight: 600 }}>
            STEP 2 OF 2: RECOVERY SETTINGS
          </span>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.5rem' }}>
            Account: <strong>{email}</strong>
          </p>
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
          <div className="form-group">
            <label className="form-label" htmlFor="sec-question">Select Security Question</label>
            <select
              id="sec-question"
              value={questionIndex}
              onChange={(e) => setQuestionIndex(e.target.value)}
              className="form-control"
              required
            >
              {questions.map((q, idx) => (
                <option key={idx} value={idx}>{q}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="sec-answer">Security Answer (3-30 Chars)</label>
            <input
              id="sec-answer"
              type="text"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              className="form-control"
              placeholder="Enter answer (letters, numbers, spaces)"
              minLength={3}
              maxLength={30}
              required
            />
            {errors.answer && <span className="error-text">{errors.answer[0]}</span>}
          </div>

          <p style={{ color: 'var(--text-dim)', fontSize: '0.82rem', marginBottom: '1.5rem' }}>
            Note: Your answer will be normalized (lowercased/trimmed) and securely hashed. This answer will be required if you ever need to reset your password.
          </p>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.8rem' }}
          >
            {loading ? 'Saving Profile...' : 'Save & Send Verification Email OTP'}
          </button>
        </form>
      </div>
    </div>
  );
}
