import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { X } from 'lucide-react';
import { API_URL } from '../services/env';
import { useAuth } from '../context/AuthContext';
import './AuthModal.css';
import { OTP_LENGTH, getStrength, useCountdown } from './auth/otpUtils';
import LoginForm from './auth/LoginForm';
import RegisterForm from './auth/RegisterForm';

type Props = {
  isOpen: boolean;
  onClose: () => void;
  initialTab?: 'login' | 'register';
};

const AuthModal = ({ isOpen, onClose, initialTab = 'login' }: Props) => {
  const [activeTab, setActiveTab] = useState<'login' | 'register'>(initialTab);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [loginStep, setLoginStep] = useState<'login' | 'forgot' | 'forgot-otp'>('login');
  const [unverifiedAccount, setUnverifiedAccount] = useState(false);
  const [resendVerifMsg, setResendVerifMsg] = useState('');
  const [resendVerifOtp, setResendVerifOtp] = useState('');
  const [resendVerifLoading, setResendVerifLoading] = useState(false);

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPasswords, setShowPasswords] = useState(false);
  const [regError, setRegError] = useState('');
  const [regLoading, setRegLoading] = useState(false);
  const [usernameStatus, setUsernameStatus] = useState<'idle' | 'checking' | 'available' | 'taken'>('idle');
  const [regStep, setRegStep] = useState<'form' | 'otp'>('form');
  const [devOtp, setDevOtp] = useState('');
  const [otpDigits, setOtpDigits] = useState<string[]>(Array(OTP_LENGTH).fill(''));
  const [verifyError, setVerifyError] = useState('');
  const [verifyLoading, setVerifyLoading] = useState(false);
  const [resendCountdown, startResendCountdown] = useCountdown(30);

  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotError, setForgotError] = useState('');
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotOtp, setForgotOtp] = useState<string[]>(Array(OTP_LENGTH).fill(''));
  const [forgotNewPassword, setForgotNewPassword] = useState('');
  const [forgotConfirmPassword, setForgotConfirmPassword] = useState('');
  const [forgotShowPasswords, setForgotShowPasswords] = useState(false);
  const [forgotDevOtp, setForgotDevOtp] = useState('');
  const [forgotSuccess, setForgotSuccess] = useState(false);
  const [forgotResendCountdown, startForgotResendCountdown] = useCountdown(30);

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

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  const handleLoginSubmit = async (e: React.FormEvent) => {
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

  const handleRegisterSubmit = async (e: React.FormEvent) => {
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
          msg = msg.map((e: { msg?: string; type?: string }) => e.msg || e).join('. ');
        } else if (!msg) {
          msg = 'Registration failed. Please check your details and try again.';
        }
        setRegError(msg as string);
      }
    } catch (_err) {
      setRegError('Unable to reach the server. Check your connection and try again.');
    } finally {
      setRegLoading(false);
    }
  };

  const handleVerifyEmail = async (e: React.FormEvent) => {
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

  const handleForgotRequest = async (e: React.FormEvent) => {
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

  const handleForgotReset = async (e: React.FormEvent) => {
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

  const handleTabSwitch = (tab: 'login' | 'register') => {
    if (tab === activeTab || isTransitioning) return;
    setIsTransitioning(true);
    setTimeout(() => {
      setActiveTab(tab);
      setTimeout(() => setIsTransitioning(false), 50);
    }, 150);
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
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
    firstName.length > 0 && email.length > 0 &&
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
              <LoginForm
                loginStep={loginStep} setLoginStep={setLoginStep}
                loginUsername={loginUsername} setLoginUsername={setLoginUsername}
                loginPassword={loginPassword} setLoginPassword={setLoginPassword}
                showLoginPassword={showLoginPassword} setShowLoginPassword={setShowLoginPassword}
                loginError={loginError} loginLoading={loginLoading}
                registrationSuccess={registrationSuccess} forgotSuccess={forgotSuccess}
                unverifiedAccount={unverifiedAccount}
                resendVerifMsg={resendVerifMsg} resendVerifOtp={resendVerifOtp}
                resendVerifLoading={resendVerifLoading}
                handleLoginSubmit={handleLoginSubmit}
                handleResendVerification={handleResendVerification}
                handleTabSwitch={handleTabSwitch}
                forgotEmail={forgotEmail} setForgotEmail={setForgotEmail}
                forgotError={forgotError} forgotLoading={forgotLoading}
                forgotOtp={forgotOtp} setForgotOtp={setForgotOtp}
                forgotNewPassword={forgotNewPassword} setForgotNewPassword={setForgotNewPassword}
                forgotConfirmPassword={forgotConfirmPassword} setForgotConfirmPassword={setForgotConfirmPassword}
                forgotShowPasswords={forgotShowPasswords} setForgotShowPasswords={setForgotShowPasswords}
                forgotDevOtp={forgotDevOtp} forgotResendCountdown={forgotResendCountdown}
                forgotStrength={forgotStrength} forgotStrengthsMatch={forgotStrengthsMatch}
                handleForgotRequest={handleForgotRequest} handleForgotReset={handleForgotReset}
                handleResendForgot={handleResendForgot}
              />
            ) : (
              <RegisterForm
                regStep={regStep} setRegStep={setRegStep}
                firstName={firstName} setFirstName={setFirstName}
                lastName={lastName} setLastName={setLastName}
                regUsername={regUsername} setRegUsername={setRegUsername}
                usernameStatus={usernameStatus}
                email={email} setEmail={setEmail}
                password={password} setPassword={setPassword}
                confirmPassword={confirmPassword} setConfirmPassword={setConfirmPassword}
                showPasswords={showPasswords} setShowPasswords={setShowPasswords}
                regError={regError} regLoading={regLoading}
                strength={strength} passwordsMatch={passwordsMatch}
                passwordsMismatch={passwordsMismatch} canRegister={canRegister}
                devOtp={devOtp} otpDigits={otpDigits} setOtpDigits={setOtpDigits}
                verifyError={verifyError} verifyLoading={verifyLoading}
                resendCountdown={resendCountdown}
                handleRegisterSubmit={handleRegisterSubmit}
                handleVerifyEmail={handleVerifyEmail}
                handleResendRegister={handleResendRegister}
                handleTabSwitch={handleTabSwitch}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
