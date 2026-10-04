import React, { useState } from 'react';
import api from '../services/api';
import { Mail, MapPin, User, Send, CheckCircle, AlertCircle } from 'lucide-react';

export default function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });

  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: null });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMsg('');
    setErrors({});

    try {
      const res = await api.post('/contact', formData);
      setSuccessMsg(res.data.message);
      setFormData({ name: '', email: '', subject: '', message: '' });
    } catch (err) {
      if (err.response && err.response.data && err.response.data.errors) {
        setErrors(err.response.data.errors);
      } else {
        setErrors({ general: 'Failed to send message. Please try again.' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-wrapper">
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', textAlign: 'center' }}>
          Contact <span style={{ color: 'var(--accent-gold)' }}>Deptrix Support</span>
        </h1>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', fontSize: '1.1rem', marginBottom: '3rem' }}>
          Have questions regarding software supply chain scanning or custom security integrations? Get in touch with us.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>
          {/* Author / Official Details */}
          <div className="card">
            <h2 style={{ fontSize: '1.4rem', color: 'var(--accent-gold)', marginBottom: '1.5rem' }}>
              Official Contact Info
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <User size={22} style={{ color: 'var(--accent-gold)', marginTop: '3px' }} />
                <div>
                  <strong style={{ color: 'var(--text-light)', display: 'block' }}>Lead Developer</strong>
                  <span style={{ color: 'var(--text-muted)' }}>Omkar Nalawade</span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <Mail size={22} style={{ color: 'var(--accent-gold)', marginTop: '3px' }} />
                <div>
                  <strong style={{ color: 'var(--text-light)', display: 'block' }}>Email Address</strong>
                  <a href="mailto:nalawadeomkar0508@gmail.com" style={{ color: 'var(--accent-gold)' }}>
                    nalawadeomkar0508@gmail.com
                  </a>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <MapPin size={22} style={{ color: 'var(--accent-gold)', marginTop: '3px' }} />
                <div>
                  <strong style={{ color: 'var(--text-light)', display: 'block' }}>Address / Location</strong>
                  <span style={{ color: 'var(--text-muted)' }}>Pune, Maharashtra, India</span>
                </div>
              </div>
            </div>
          </div>

          {/* Form */}
          <div className="card">
            <h2 style={{ fontSize: '1.4rem', marginBottom: '1.5rem' }}>Send Us a Message</h2>

            {successMsg && (
              <div style={{
                backgroundColor: 'var(--success-green-bg)',
                border: '1px solid var(--success-green)',
                color: 'var(--success-green)',
                padding: '0.85rem 1rem',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '1.25rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.92rem'
              }}>
                <CheckCircle size={18} /> {successMsg}
              </div>
            )}

            {errors.general && (
              <div style={{
                backgroundColor: 'var(--danger-red-bg)',
                border: '1px solid var(--danger-red)',
                color: 'var(--danger-red)',
                padding: '0.85rem 1rem',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '1.25rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.92rem'
              }}>
                <AlertCircle size={18} /> {errors.general}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label" htmlFor="contact-name">Your Name</label>
                <input
                  id="contact-name"
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="form-control"
                  placeholder="Enter full name"
                  required
                />
                {errors.name && <span className="error-text">{errors.name[0]}</span>}
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="contact-email">Your Email</label>
                <input
                  id="contact-email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="form-control"
                  placeholder="name@example.com"
                  required
                />
                {errors.email && <span className="error-text">{errors.email[0]}</span>}
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="contact-subject">Subject</label>
                <input
                  id="contact-subject"
                  type="text"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  className="form-control"
                  placeholder="Subject of inquiry"
                  required
                />
                {errors.subject && <span className="error-text">{errors.subject[0]}</span>}
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="contact-message">Message</label>
                <textarea
                  id="contact-message"
                  name="message"
                  rows="4"
                  value={formData.message}
                  onChange={handleChange}
                  className="form-control"
                  placeholder="Type your message here..."
                  required
                />
                {errors.message && <span className="error-text">{errors.message[0]}</span>}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary"
                style={{ width: '100%', marginTop: '0.5rem' }}
              >
                {loading ? 'Sending...' : <><Send size={16} /> Send Message</>}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
