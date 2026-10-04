import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Footer from './components/Footer';

// Pages
import Home from './pages/Home';
import About from './pages/About';
import Threats from './pages/Threats';
import Contact from './pages/Contact';
import SignUpStep1 from './pages/SignUpStep1';
import SignUpStep2 from './pages/SignUpStep2';
import VerifyOTP from './pages/VerifyOTP';
import Login from './pages/Login';
import ForgotPassword from './pages/ForgotPassword';
import Dashboard from './pages/Dashboard';
import UploadZip from './pages/UploadZip';
import UploadGithub from './pages/UploadGithub';
import UploadManifests from './pages/UploadManifests';
import ScanReport from './pages/ScanReport';
import ScanHistory from './pages/ScanHistory';

function PrivateRoute({ children }) {
  const { user, loading } = useContext(AuthContext);
  if (loading) {
    return <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-gold)' }}>Loading Deptrix Session...</div>;
  }
  return user ? children : <Navigate to="/login" replace />;
}

function MainLayout() {
  const { user } = useContext(AuthContext);

  return (
    <div className="app-container">
      <Navbar />

      <main className="main-content">
        {user ? (
          <div className="app-with-sidebar">
            <Sidebar />
            <div style={{ flex: 1, width: '100%' }}>
              <Routes>
                <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
                <Route path="/upload" element={<PrivateRoute><UploadZip /></PrivateRoute>} />
                <Route path="/upload/zip" element={<PrivateRoute><UploadZip /></PrivateRoute>} />
                <Route path="/upload/github" element={<PrivateRoute><UploadGithub /></PrivateRoute>} />
                <Route path="/upload/manifests" element={<PrivateRoute><UploadManifests /></PrivateRoute>} />
                <Route path="/scans/:scanId" element={<PrivateRoute><ScanReport /></PrivateRoute>} />
                <Route path="/history" element={<PrivateRoute><ScanHistory /></PrivateRoute>} />
                
                {/* Public Info Pages accessible inside app */}
                <Route path="/about" element={<About />} />
                <Route path="/threats" element={<Threats />} />
                <Route path="/contact" element={<Contact />} />
                
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </div>
          </div>
        ) : (
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/threats" element={<Threats />} />
            <Route path="/contact" element={<Contact />} />

            {/* Auth Routes */}
            <Route path="/signup-step1" element={<SignUpStep1 />} />
            <Route path="/signup-step2" element={<SignUpStep2 />} />
            <Route path="/verify-otp" element={<VerifyOTP />} />
            <Route path="/login" element={<Login />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        )}
      </main>

      <Footer />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <MainLayout />
      </Router>
    </AuthProvider>
  );
}
