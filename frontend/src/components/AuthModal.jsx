import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, User, Lock, Mail, UserPlus, LogIn, ArrowRight, ArrowLeft, Check, Eye, EyeOff, CheckCircle, ShieldCheck, KeyRound } from 'lucide-react';
import { API_URL } from '../services/env';
import { useAuth } from '../context/AuthContext';
import './AuthModal.css';

const OTP_LENGTH = 6;

const getStrength = (pw) => {
  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  if (/[a-z]/.test(pw)) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^a-zA-Z0-9]/.test(pw)) score++;
  return Math.min(score, 5);
};

const strengthLabel = ['', 'Weak', 'Weak', 'Fair', 'Good', 'Strong'];
const strengthColor = ['', 'var(--color-error)', 'var(--color-error)', 'var(--color-warning)', 'var(--color-primary)', 'var(--color-success)'];

const OtpBoxes = ({ value, onChange, disabled }) => {
  const refs = useRef([]);

  const handleChange = (i, e) => {
    const digit = e.target.value.replace(/\D/g, '').slice(-1);
    const next = [...value];
    next[i] = digit;
    onChange(next);
    if (digit && i < OTP_LENGTH - 1) refs.current[i + 1]?.focus();
  };

  const handleKeyDown = (i, e) => {
    if (e.key === 'Backspace' && !value[i] && i > 0) refs.current[i - 1]?.focus();
    if (e.key === 'ArrowLeft' && i > 0) refs.current[i - 1]?.focus();
    if (e.key === 'ArrowRight' && i < OTP_LENGTH - 1) refs.current[i + 1]?.focus();
  };

  const handlePaste = (e) => {
    const digits = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, OTP_LENGTH);
    if (!digits) return;
    e.preventDefault();
    onChange(Array.from({ length: OTP_LENGTH }, (_, i) => digits[i] || ''));
    refs.current[Math.min(digits.length, OTP_LENGTH - 1)]?.focus();
  };

  return (
    <div className="auth-otp-row" onPaste={handlePaste}>
      {Array.from({ length: OTP_LENGTH }, (_, i) => (
        <input
          key={i}
          ref={(el) => { refs.current[i] = el; }}
          type="text"
          inputMode="numeric"
          autoComplete={i === 0 ? 'one-time-code' : 'off'}
          maxLength={1}
          value={value[i]}
          disabled={disabled}
          onChange={(e) => handleChange(i, e)}
          onKeyDown={(e) => handleKeyDown(i, e)}
          className="auth-otp-input"
          aria-label={`Digit ${i + 1}`}
        />
      ))}
    </div>
  );
};

const DevOtpHint = ({ otp, label }) => {
  if (!otp) return null;
  return (
    <div className="auth-modal-dev-hint" role="alert">
      <ShieldCheck size={14} />
      <span>
        {label}: <strong>{otp}</strong> <em>(dev only – SMTP not configured)</em>
      </span>
    </div>
  );
};

const useCountdown = (seconds) => {
  const [countdown, setCountdown] = useState(seconds);
  const start = useCallback((s = seconds) => setCountdown(s), [seconds]);
  useEffect(() => {
    if (countdown <= 0) return undefined;
    const t = setInterval(() => setCountdown((c) => (c > 1 ? c - 1 : 0)), 1000);
    return () => clearInterval(t);
  }, [countdown]);
  return [countdown, start];
};

const AuthModal = ({ isOpen, onClose, initialTab = 'login' }) => {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  // Login state
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [loginStep, setLoginStep] = useState('login'); // 'login' | 'forgot' | 'forgot-otp'
  const [unverifiedAccount, setUnverifiedAccount] = useState(false);
  const [resendVerifMsg, setResendVerifMsg] = useState('');
  const [resendVerifOtp, setResendVerifOtp] = useState('');
  const [resendVerifLoading, setResendVerifLoading] = useState(false);

  // Register state
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPasswords, setShowPasswords] = useState(false);
  const [regError, setRegError] = useState('');
  const [regLoading, setRegLoading] = useState(false);
  const [usernameStatus, setUsernameStatus] = useState('idle');
  const [regStep, setRegStep] = useState('form'); // 'form' | 'otp'
  const [devOtp, setDevOtp] = useState('');
  const [otpDigits, setOtpDigits] = useState(Array(OTP_LENGTH).fill(''));
  const [verifyError, setVerifyError] = useState('');
  const [verifyLoading, setVerifyLoading] = useState(false);
  const [resendCountdown, startResendCountdown] = useCountdown(30);

  // Forgot password state
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotError, setForgotError] = useState('');
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotOtp, setForgotOtp] = useState(Array(OTP_LENGTH).fill(''));
  const [forgotNewPassword, setForgotNewPassword] = useState('');
  const [forgotConfirmPassword, setForgotConfirmPassword] = useState('');
  const [forgotShowPasswords, setForgotShowPasswords] = useState(false);
  const [forgotDevOtp, setForgotDevOtp] = useState('');
  const [forgotSuccess, setForgotSuccess] = useState(false);
  const [forgotResendCountdown, startForgotResendCountdown] = useCountdown(30);

  // Reset form when tab changes or modal opens
  useEffect(() => {
    if (isOpen) {
      setActiveTab(initialTab);
      setLoginUsername('');
      setLoginPassword('');
      setLoginError('');
      setFirstName('');
      setLastName('');
      setRegUsername('');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setRegError('');
      setUsernameStatus('idle');
      setRegistrationSuccess(false);
      setRegStep('form');
      setDevOtp('');
      setOtpDigits(Array(OTP_LENGTH).fill(''));
      setVerifyError('');
      setLoginStep('login');
      setUnverifiedAccount(false);
      setResendVerifMsg('');
      setResendVerifOtp('');
      setForgotEmail('');
      setForgotError('');
      setForgotOtp(Array(OTP_LENGTH).fill(''));
      setForgotNewPassword('');
      setForgotConfirmPassword('');
      setForgotDevOtp('');
      setForgotSuccess(false);
    }
  }, [isOpen, initialTab]);

  // Username availability check
  useEffect(() => {
    if (regUsername.length < 3) {
      setUsernameStatus('idle');
      return undefined;
    }
    const timer = setTimeout(async () => {
      setUsernameStatus('checking');
      try {
        const res = await fetch(`${API_URL}/api/auth/check-username/${encodeURIComponent(regUsername)}`);
        const data = await res.json();
        setUsernameStatus(data.available ? 'available' : 'taken');
      } catch (_err) {
        setUsernameStatus('idle');
      }
    }, 400);
    return () => clearTimeout(timer);
  }, [regUsername]);

  // Escape key handler
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Body scroll lock
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoginError('');
    setUnverifiedAccount(false);
    setResendVerifMsg('');
    setResendVerifOtp('');
    setLoginLoading(true);

    const formData = new URLSearchParams();
    formData.append('username', loginUsername);
    formData.append('password', loginPassword);

    try {
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      });
      const data = await res.json();
      if (res.ok) {
        await login();
        onClose();
        navigate('/app');
      } else {
        setLoginError(data.error || data.detail?.[0]?.msg || data.detail || 'Invalid username or password.');
        if (res.status === 403) setUnverifiedAccount(true);
      }
    } catch (_err) {
      setLoginError('Unable to reach the server. Check your connection and try again.');
    } finally {
      setLoginLoading(false);
    }
  };

  const handleResendVerification = async () => {
    if (resendVerifLoading) return;
    setResendVerifLoading(true);
    setResendVerifMsg('');
    try {
      const res = await fetch(`${API_URL}/api/auth/resend-verification`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: loginUsername }),
      });
      const data = await res.json();
      if (res.ok) {
        setResendVerifMsg(data.message || 'A new code has been sent.');
        if (data.debug_otp) setResendVerifOtp(data.debug_otp);
        setLoginError('');
      } else {
        setLoginError(data.error || data.detail?.[0]?.msg || data.detail || 'Unable to resend the code. Try again shortly.');
      }
    } catch (_err) {
      setLoginError('Unable to reach the server. Check your connection and try again.');
    } finally {
      setResendVerifLoading(false);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    if (usernameStatus === 'taken') return;
    if (password !== confirmPassword) {
      setRegError('Passwords do not match.');
      return;
    }
    setRegError('');
    setRegLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: regUsername,
          email,
          password,
          full_name: `${firstName} ${lastName}`.trim(),
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setDevOtp(data.debug_otp || '');
        setOtpDigits(Array(OTP_LENGTH).fill(''));
        setVerifyError('');
        setRegStep('otp');
        startResendCountdown();
      } else {
        let msg = data.error || data.detail;
        if (Array.isArray(msg)) {
          msg = msg.map(e => e.msg || e).join('. ');
        } else if (!msg) {
          msg = 'Registration failed. Please check your details and try again.';
        }
        setRegError(msg);
      }
    } catch (_err) {
      setRegError('Unable to reach the server. Check your connection and try again.');
    } finally {
      setRegLoading(false);
    }
  };

  const handleVerifyEmail = async (e) => {
    e.preventDefault();
    const code = otpDigits.join('');
    if (code.length !== OTP_LENGTH) {
      setVerifyError('Please enter the 6-digit code.');
      return;
    }
    setVerifyError('');
    setVerifyLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/auth/verify-email`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp: code }),
      });
      const data = await res.json();
      if (res.ok) {
        setRegistrationSuccess(true);
        setLoginUsername(regUsername);
        setLoginPassword('');
        setRegStep('form');
        setActiveTab('login');
      } else {
        setVerifyError(data.error || data.detail?.[0]?.msg || data.detail || 'Invalid code. Please check and try again.');
      }
    } catch (_err) {
      setVerifyError('Unable to reach the server. Check your connection and try again.');
    } finally {
      setVerifyLoading(false);
    }
  };

  const handleResendRegister = async () => {
    if (resendCountdown > 0) return;
    setVerifyError('');
    try {
      const res = await fetch(`${API_URL}/api/auth/resend-otp`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, purpose: 'register' }),
      });
      const data = await res.json();
      if (res.ok) {
        if (data.debug_otp) setDevOtp(data.debug_otp);
        setOtpDigits(Array(OTP_LENGTH).fill(''));
        startResendCountdown();
      } else {
        setVerifyError(data.error || data.detail?.[0]?.msg || data.detail || 'Unable to resend the code. Try again shortly.');
      }
    } catch (_err) {
      setVerifyError('Unable to reach the server. Check your connection and try again.');
    }
  };

  const handleForgotRequest = async (e) => {
    e.preventDefault();
    setForgotError('');
    setForgotLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/auth/request-password-reset`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: forgotEmail }),
      });
      const data = await res.json();
      if (res.ok) {
        setForgotDevOtp(data.debug_otp || '');
        setForgotOtp(Array(OTP_LENGTH).fill(''));
        setLoginStep('forgot-otp');
        startForgotResendCountdown();
      } else {
        setForgotError(data.error || data.detail?.[0]?.msg || data.detail || 'Unable to send the reset code. Try again.');
      }
    } catch (_err) {
      setForgotError('Unable to reach the server. Check your connection and try again.');
    } finally {
      setForgotLoading(false);
    }
  };

  const handleForgotReset = async (e) => {
    e.preventDefault();
    if (forgotNewPassword.length < 8) {
      setForgotError('New password must be at least 8 characters.');
      return;
    }
    if (forgotNewPassword !== forgotConfirmPassword) {
      setForgotError('Passwords do not match.');
      return;
    }
    const code = forgotOtp.join('');
    if (code.length !== OTP_LENGTH) {
      setForgotError('Please enter the 6-digit code from your email.');
      return;
    }
    setForgotError('');
    setForgotLoading(true);
    try {
      const verifyRes = await fetch(`${API_URL}/api/auth/verify-reset-otp`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: forgotEmail, otp: code }),
      });
      const verifyData = await verifyRes.json();
      if (!verifyRes.ok) {
        setForgotError(verifyData.error || verifyData.detail?.[0]?.msg || verifyData.detail || 'Invalid or expired code.');
        return;
      }
      const resetRes = await fetch(`${API_URL}/api/auth/reset-password`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: verifyData.reset_token, new_password: forgotNewPassword }),
      });
      const resetData = await resetRes.json();
      if (!resetRes.ok) {
        setForgotError(resetData.error || resetData.detail?.[0]?.msg || resetData.detail || 'Unable to reset the password. Try again.');
        return;
      }
      setForgotSuccess(true);
      setLoginStep('login');
      setLoginUsername('');
      setLoginPassword('');
    } catch (_err) {
      setForgotError('Unable to reach the server. Check your connection and try again.');
    } finally {
      setForgotLoading(false);
    }
  };

  const handleResendForgot = async () => {
    if (forgotResendCountdown > 0) return;
    setForgotError('');
    try {
      const res = await fetch(`${API_URL}/api/auth/request-password-reset`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: forgotEmail }),
      });
      const data = await res.json();
      if (res.ok) {
        if (data.debug_otp) setForgotDevOtp(data.debug_otp);
        setForgotOtp(Array(OTP_LENGTH).fill(''));
        startForgotResendCountdown();
      } else {
        setForgotError(data.error || data.detail?.[0]?.msg || data.detail || 'Unable to resend the code. Try again shortly.');
      }
    } catch (_err) {
      setForgotError('Unable to reach the server. Check your connection and try again.');
    }
  };

  const handleTabSwitch = (tab) => {
    if (tab === activeTab || isTransitioning) return;
    setIsTransitioning(true);
    setTimeout(() => {
      setActiveTab(tab);
      setTimeout(() => setIsTransitioning(false), 50);
    }, 150);
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const strength = getStrength(password);
  const passwordsMatch = password.length > 0 && confirmPassword.length > 0 && password === confirmPassword;
  const passwordsMismatch = confirmPassword.length > 0 && password !== confirmPassword;
  const forgotStrengthsMatch = forgotNewPassword.length > 0 && forgotConfirmPassword.length > 0 && forgotNewPassword === forgotConfirmPassword;
  const forgotStrength = getStrength(forgotNewPassword);

  const canRegister =
    regUsername.length >= 3 &&
    usernameStatus === 'available' &&
    password.length >= 8 &&
    passwordsMatch &&
    firstName && email &&
    !regLoading;

  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay" onClick={handleOverlayClick}>
      <div className="auth-modal" role="dialog" aria-modal="true" aria-label={activeTab === 'login' ? 'Sign in' : 'Create account'}>
        <button className="auth-modal-close" onClick={onClose} aria-label="Close">
          <X size={18} />
        </button>
        
        <div className="auth-modal-body">
          <div style={{ textAlign: 'center', marginBottom: '8px' }}>
            <span style={{
              fontWeight: 'var(--font-extrabold)', fontSize: '24px',
              letterSpacing: 'var(--tracking-tight)',
              color: 'var(--color-text)',
            }}>
              Skill<span className="mc-gradient">Path</span>
            </span>
          </div>
          
          <div className="auth-modal-tabs">
            <button
              className={`auth-modal-tab ${activeTab === 'login' ? 'active' : ''}`}
              onClick={() => handleTabSwitch('login')}
            >
              Sign In
            </button>
            <button
              className={`auth-modal-tab ${activeTab === 'register' ? 'active' : ''}`}
              onClick={() => handleTabSwitch('register')}
            >
              Create account
            </button>
          </div>

          <div className={`auth-modal-content ${isTransitioning ? 'fade-out' : 'fade-in'}`}>
            {activeTab === 'login' ? (
              loginStep === 'login' ? (
              <form onSubmit={handleLoginSubmit} className="auth-modal-form" noValidate>
                {registrationSuccess && (
                  <div className="auth-modal-success" role="alert">
                    <CheckCircle size={16} />
                    <span>Email verified! Your account is ready. Please sign in.</span>
                  </div>
                )}
                {forgotSuccess && (
                  <div className="auth-modal-success" role="alert">
                    <CheckCircle size={16} />
                    <span>Password reset successful! Sign in with your new password.</span>
                  </div>
                )}
                {loginError && (
                  <div className="auth-modal-error" role="alert">
                    <span className="auth-modal-error-icon" aria-hidden="true">!</span>
                    <span>{loginError}</span>
                  </div>
                )}
                {resendVerifMsg && (
                  <div className="auth-modal-success" role="alert">
                    <CheckCircle size={16} />
                    <span>{resendVerifMsg}</span>
                  </div>
                )}
                <DevOtpHint otp={resendVerifOtp} label="Dev verification code" />
                {unverifiedAccount && (
                  <div className="auth-resend-verification">
                    <button
                      type="button"
                      className="auth-link"
                      onClick={handleResendVerification}
                      disabled={resendVerifLoading}
                    >
                      {resendVerifLoading ? 'Sending...' : 'Resend verification code'}
                    </button>
                  </div>
                )}

                <div className="auth-field">
                  <label className="auth-field-label" htmlFor="modal-login-username">Username</label>
                  <div className="auth-input-wrap">
                    <input
                      id="modal-login-username"
                      type="text"
                      value={loginUsername}
                      onChange={(e) => setLoginUsername(e.target.value)}
                      required
                      autoComplete="username"
                      placeholder="your-username"
                      className="auth-input has-icon"
                    />
                    <User size={16} style={{
                      position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                      color: 'var(--color-text-light)', pointerEvents: 'none',
                    }} />
                  </div>
                </div>

                <div className="auth-field">
                  <label className="auth-field-label" htmlFor="modal-login-password">Password</label>
                  <div className="auth-input-wrap">
                    <input
                      id="modal-login-password"
                      type={showLoginPassword ? 'text' : 'password'}
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      required
                      autoComplete="current-password"
                      placeholder="••••••••"
                      className="auth-input has-icon"
                    />
                    <Lock size={16} style={{
                      position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                      color: 'var(--color-text-light)', pointerEvents: 'none',
                    }} />
                    <button
                      type="button"
                      onClick={() => setShowLoginPassword(!showLoginPassword)}
                      style={{
                        position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)',
                        background: 'none', border: 'none', cursor: 'pointer', padding: '4px',
                        color: 'var(--color-text-light)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      }}
                      tabIndex={-1}
                    >
                      {showLoginPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <button type="submit" className="auth-modal-submit" disabled={loginLoading || !loginUsername || !loginPassword}>
                  {loginLoading ? (
                    <>
                      <span className="spinner-btn" aria-hidden="true" />
                      Signing you in...
                    </>
                  ) : (
                    <>
                      <LogIn size={16} />
                      Sign in
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>

                <div style={{ textAlign: 'right', marginTop: '-10px' }}>
                  <button type="button" className="auth-link" onClick={() => setLoginStep('forgot')}>
                    Forgot password?
                  </button>
                </div>

                <div className="auth-modal-footer">
                  New here?{' '}
                  <span className="auth-modal-footer-link" onClick={() => handleTabSwitch('register')}>
                    Create an account
                  </span>
                </div>
              </form>
              ) : loginStep === 'forgot' ? (
                <form onSubmit={handleForgotRequest} className="auth-modal-form">
                  <button type="button" className="auth-back-link" onClick={() => setLoginStep('login')}>
                    <ArrowLeft size={14} /> Back to sign in
                  </button>
                  {forgotError && (
                    <div className="auth-modal-error" role="alert">
                      <span className="auth-modal-error-icon" aria-hidden="true">!</span>
                      <span>{forgotError}</span>
                    </div>
                  )}
                  <p className="auth-modal-subtitle">
                    Enter your account email and we&apos;ll send you a 6-digit code to reset your password.
                  </p>
                  <div className="auth-field">
                    <label className="auth-field-label" htmlFor="modal-forgot-email">Email</label>
                    <div className="auth-input-wrap">
                      <input
                        id="modal-forgot-email"
                        type="email"
                        value={forgotEmail}
                        onChange={(e) => setForgotEmail(e.target.value)}
                        required
                        autoComplete="email"
                        placeholder="you@example.com"
                        className="auth-input has-icon"
                      />
                      <Mail size={16} style={{
                        position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                        color: 'var(--color-text-light)', pointerEvents: 'none',
                      }} />
                    </div>
                  </div>
                  <button type="submit" className="auth-modal-submit" disabled={forgotLoading || !forgotEmail}>
                    {forgotLoading ? (
                      <>
                        <span className="spinner-btn" aria-hidden="true" />
                        Sending code...
                      </>
                    ) : (
                      <>
                        <KeyRound size={16} />
                        Send reset code
                      </>
                    )}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleForgotReset} className="auth-modal-form">
                  <button type="button" className="auth-back-link" onClick={() => setLoginStep('forgot')}>
                    <ArrowLeft size={14} /> Change email
                  </button>
                  {forgotError && (
                    <div className="auth-modal-error" role="alert">
                      <span className="auth-modal-error-icon" aria-hidden="true">!</span>
                      <span>{forgotError}</span>
                    </div>
                  )}
                  <DevOtpHint otp={forgotDevOtp} label="Dev reset code" />
                  <p className="auth-modal-subtitle">
                    We sent a 6-digit code to <strong>{forgotEmail}</strong>. Enter it and choose a new password.
                  </p>
                  <div className="auth-field">
                    <label className="auth-field-label" htmlFor="modal-forgot-otp">Verification code</label>
                    <OtpBoxes value={forgotOtp} onChange={setForgotOtp} disabled={forgotLoading} />
                    <div className="auth-resend-row">
                      <button
                        type="button"
                        className="auth-link"
                        onClick={handleResendForgot}
                        disabled={forgotResendCountdown > 0}
                      >
                        Resend code
                        {forgotResendCountdown > 0 && ` in ${forgotResendCountdown}s`}
                      </button>
                    </div>
                  </div>
                  <div className="auth-field">
                    <label className="auth-field-label" htmlFor="modal-forgot-new-password">New password</label>
                    <div className="auth-input-wrap">
                      <input
                        id="modal-forgot-new-password"
                        type={forgotShowPasswords ? 'text' : 'password'}
                        value={forgotNewPassword}
                        onChange={(e) => setForgotNewPassword(e.target.value)}
                        required
                        minLength={8}
                        autoComplete="new-password"
                        placeholder="At least 8 characters"
                        className="auth-input has-icon"
                      />
                      <Lock size={16} style={{
                        position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                        color: 'var(--color-text-light)', pointerEvents: 'none',
                      }} />
                      <button
                        type="button"
                        onClick={() => setForgotShowPasswords((s) => !s)}
                        style={{
                          position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)',
                          background: 'none', border: 'none', cursor: 'pointer', padding: '4px',
                          color: 'var(--color-text-light)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                        }}
                        tabIndex={-1}
                      >
                        {forgotShowPasswords ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                    {forgotNewPassword.length > 0 && (
                      <div style={{ marginTop: '6px' }}>
                        <div className="auth-password-strength">
                          <div
                            className="auth-password-strength-bar"
                            style={{
                              width: `${(forgotStrength / 5) * 100}%`,
                              background: strengthColor[forgotStrength],
                            }}
                          />
                        </div>
                        <p className="auth-hint" style={{ color: strengthColor[forgotStrength] || 'var(--color-text-light)', marginTop: '6px' }}>
                          {strengthLabel[forgotStrength]}
                        </p>
                      </div>
                    )}
                  </div>
                  <div className="auth-field">
                    <label className="auth-field-label" htmlFor="modal-forgot-confirm">
                      Confirm new password
                      {forgotStrengthsMatch && (
                        <span className="auth-hint auth-hint-success" style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                          <Check size={11} /> Matches
                        </span>
                      )}
                    </label>
                    <div className="auth-input-wrap">
                      <input
                        id="modal-forgot-confirm"
                        type={forgotShowPasswords ? 'text' : 'password'}
                        value={forgotConfirmPassword}
                        onChange={(e) => setForgotConfirmPassword(e.target.value)}
                        required
                        minLength={8}
                        autoComplete="new-password"
                        placeholder="Re-enter your password"
                        className="auth-input has-icon"
                      />
                      <Lock size={16} style={{
                        position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                        color: 'var(--color-text-light)', pointerEvents: 'none',
                      }} />
                      {forgotStrengthsMatch && (
                        <div className="auth-input-status">
                          <Check size={16} color="var(--color-success)" />
                        </div>
                      )}
                    </div>
                  </div>
                  <button
                    type="submit"
                    className="auth-modal-submit"
                    disabled={forgotLoading || forgotNewPassword.length < 8 || !forgotStrengthsMatch || forgotOtp.join('').length !== OTP_LENGTH}
                  >
                    {forgotLoading ? (
                      <>
                        <span className="spinner-btn" aria-hidden="true" />
                        Resetting password...
                      </>
                    ) : (
                      <>
                        <KeyRound size={16} />
                        Reset password
                      </>
                    )}
                  </button>
                </form>
              )
            ) : regStep === 'form' ? (
            <form onSubmit={handleRegisterSubmit} className="auth-modal-form">
              {regError && (
                <div className="auth-modal-error" role="alert">
                  <span className="auth-modal-error-icon" aria-hidden="true">!</span>
                  <span>{regError}</span>
                </div>
              )}

              <div className="auth-row-2">
                <div className="auth-field">
                  <label className="auth-field-label" htmlFor="modal-reg-first">First name</label>
                  <div className="auth-input-wrap">
                    <input
                      id="modal-reg-first"
                      type="text"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      required
                      autoComplete="given-name"
                      placeholder="First"
                      className="auth-input has-icon"
                    />
                    <User size={16} style={{
                      position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                      color: 'var(--color-text-light)', pointerEvents: 'none',
                    }} />
                  </div>
                </div>

                <div className="auth-field">
                  <label className="auth-field-label" htmlFor="modal-reg-last">Last name <span style={{ color: 'var(--color-text-muted)', fontWeight: 400 }}>(optional)</span></label>
                  <div className="auth-input-wrap">
                    <input
                      id="modal-reg-last"
                      type="text"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                      autoComplete="family-name"
                      placeholder="Last"
                      className="auth-input has-icon"
                    />
                    <User size={16} style={{
                      position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                      color: 'var(--color-text-light)', pointerEvents: 'none',
                    }} />
                  </div>
                </div>
              </div>

              <div className="auth-field">
                <label className="auth-field-label" htmlFor="modal-reg-username">
                  Username
                  {usernameStatus === 'available' && (
                    <span className="auth-hint auth-hint-success" style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <Check size={11} /> Available
                    </span>
                  )}
                  {usernameStatus === 'taken' && (
                    <span className="auth-hint auth-hint-error" style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <X size={11} /> Taken
                    </span>
                  )}
                </label>
                <div className="auth-input-wrap">
                  <input
                    id="modal-reg-username"
                    type="text"
                    value={regUsername}
                    onChange={(e) => setRegUsername(e.target.value)}
                    required
                    minLength={3}
                    autoComplete="username"
                    placeholder="choose-a-handle"
                    className="auth-input has-icon"
                    style={{
                      paddingRight: usernameStatus === 'idle' ? '14px' : '40px',
                    }}
                  />
                  <span style={{
                    position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                    color: 'var(--color-text-light)', pointerEvents: 'none', fontWeight: 600, fontSize: '14px',
                  }}>@</span>
                  <div className="auth-input-status">
                    {usernameStatus === 'checking' && <span className="spinner" />}
                    {usernameStatus === 'available' && <Check size={16} color="var(--color-success)" />}
                    {usernameStatus === 'taken' && <X size={16} color="var(--color-error)" />}
                  </div>
                </div>
                {usernameStatus === 'idle' && regUsername.length > 0 && regUsername.length < 3 && (
                  <p className="auth-hint auth-hint-muted">Minimum 3 characters.</p>
                )}
              </div>

              <div className="auth-field">
                <label className="auth-field-label" htmlFor="modal-reg-email">Email</label>
                <div className="auth-input-wrap">
                  <input
                    id="modal-reg-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoComplete="email"
                    placeholder="you@example.com"
                    className="auth-input has-icon"
                  />
                  <Mail size={16} style={{
                    position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                    color: 'var(--color-text-light)', pointerEvents: 'none',
                  }} />
                </div>
              </div>

              <div className="auth-field">
                <label className="auth-field-label" htmlFor="modal-reg-password">
                  Password
                  <button
                    type="button"
                    onClick={() => setShowPasswords((s) => !s)}
                    className="auth-link"
                    style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                    tabIndex={-1}
                  >
                    {showPasswords ? <EyeOff size={12} /> : <Eye size={12} />}
                    {showPasswords ? 'Hide' : 'Show'}
                  </button>
                </label>
                <div className="auth-input-wrap">
                  <input
                    id="modal-reg-password"
                    type={showPasswords ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={8}
                    autoComplete="new-password"
                    placeholder="At least 8 characters"
                    className="auth-input has-icon"
                  />
                  <Lock size={16} style={{
                    position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                    color: 'var(--color-text-light)', pointerEvents: 'none',
                  }} />
                </div>

                {password.length > 0 && (
                  <div style={{ marginTop: '6px' }}>
                    <div className="auth-password-strength">
                      <div
                        className="auth-password-strength-bar"
                        style={{
                          width: `${(strength / 5) * 100}%`,
                          background: strengthColor[strength],
                        }}
                      />
                    </div>
                    <p className="auth-hint" style={{ color: strengthColor[strength] || 'var(--color-text-light)', marginTop: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      {strength >= 4 ? <CheckCircle size={12} /> : null}
                      {strengthLabel[strength]}
                      {strength < 5 && strength > 0 && (
                        <span className="auth-hint-muted">- try mixing uppercase, numbers, and symbols.</span>
                      )}
                    </p>
                  </div>
                )}
              </div>

              <div className="auth-field">
                <label className="auth-field-label" htmlFor="modal-reg-confirm">
                  Confirm password
                  {passwordsMatch && (
                    <span className="auth-hint auth-hint-success" style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <Check size={11} /> Matches
                    </span>
                  )}
                  {passwordsMismatch && (
                    <span className="auth-hint auth-hint-error" style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <X size={11} /> Doesn&apos;t match
                    </span>
                  )}
                </label>
                <div className="auth-input-wrap">
                  <input
                    id="modal-reg-confirm"
                    type={showPasswords ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    minLength={8}
                    autoComplete="new-password"
                    placeholder="Re-enter your password"
                    className="auth-input has-icon"
                    style={{
                      paddingRight: (passwordsMatch || passwordsMismatch) ? '40px' : '14px',
                    }}
                  />
                  <Lock size={16} style={{
                    position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                    color: 'var(--color-text-light)', pointerEvents: 'none',
                  }} />
                  <div className="auth-input-status">
                    {passwordsMatch && <Check size={16} color="var(--color-success)" />}
                    {passwordsMismatch && <X size={16} color="var(--color-error)" />}
                  </div>
                </div>
                {passwordsMismatch && (
                  <p className="auth-hint auth-hint-error">Passwords do not match - please re-enter.</p>
                )}
              </div>

              <button type="submit" className="auth-modal-submit" disabled={!canRegister}>
                {regLoading ? (
                  <>
                    <span className="spinner-btn" aria-hidden="true" />
                    Creating your account...
                  </>
                ) : (
                  <>
                    <UserPlus size={16} />
                    Create account
                    <ArrowRight size={16} />
                  </>
                )}
              </button>

              <div className="auth-modal-footer">
                Already have an account?{' '}
                <span className="auth-modal-footer-link" onClick={() => handleTabSwitch('login')}>
                  Sign in
                </span>
              </div>
            </form>
            ) : (
            <form onSubmit={handleVerifyEmail} className="auth-modal-form">
              {verifyError && (
                <div className="auth-modal-error" role="alert">
                  <span className="auth-modal-error-icon" aria-hidden="true">!</span>
                  <span>{verifyError}</span>
                </div>
              )}
              <DevOtpHint otp={devOtp} label="Dev verification code" />
              <div className="auth-verify-hero">
                <div className="auth-verify-icon">
                  <ShieldCheck size={26} />
                </div>
                <h3 className="auth-verify-title">Verify your email</h3>
                <p className="auth-modal-subtitle">
                  We sent a 6-digit code to <strong>{email}</strong>. Enter it below to activate your account.
                </p>
              </div>
              <div className="auth-field">
                <label className="auth-field-label" htmlFor="modal-reg-otp">Verification code</label>
                <OtpBoxes value={otpDigits} onChange={setOtpDigits} disabled={verifyLoading} />
                <div className="auth-resend-row">
                  <button
                    type="button"
                    className="auth-link"
                    onClick={handleResendRegister}
                    disabled={resendCountdown > 0}
                  >
                    Resend code
                    {resendCountdown > 0 && ` in ${resendCountdown}s`}
                  </button>
                </div>
              </div>
              <button
                type="submit"
                className="auth-modal-submit"
                disabled={verifyLoading || otpDigits.join('').length !== OTP_LENGTH}
              >
                {verifyLoading ? (
                  <>
                    <span className="spinner-btn" aria-hidden="true" />
                    Verifying...
                  </>
                ) : (
                  <>
                    <ShieldCheck size={16} />
                    Verify & activate account
                  </>
                )}
              </button>
              <button type="button" className="auth-back-link auth-back-centered" onClick={() => setRegStep('form')}>
                <ArrowLeft size={14} /> Back to registration
              </button>
            </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
