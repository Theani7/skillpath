import { ArrowLeft, ArrowRight, Check, CheckCircle, Eye, EyeOff, Lock, Mail, ShieldCheck, User, UserPlus, X } from 'lucide-react';
import { OtpBoxes } from './otp';
import { OTP_LENGTH, strengthLabel, strengthColor } from './otpUtils';

type Props = {
  regStep: 'form' | 'otp';
  setRegStep: (s: 'form' | 'otp') => void;
  firstName: string;
  setFirstName: (v: string) => void;
  lastName: string;
  setLastName: (v: string) => void;
  regUsername: string;
  setRegUsername: (v: string) => void;
  usernameStatus: 'idle' | 'checking' | 'available' | 'taken';
  email: string;
  setEmail: (v: string) => void;
  password: string;
  setPassword: (v: string) => void;
  confirmPassword: string;
  setConfirmPassword: (v: string) => void;
  showPasswords: boolean;
  setShowPasswords: React.Dispatch<React.SetStateAction<boolean>>;
  regError: string;
  regLoading: boolean;
  strength: number;
  passwordsMatch: boolean;
  passwordsMismatch: boolean;
  canRegister: boolean;
  otpDigits: string[];
  setOtpDigits: (v: string[]) => void;
  verifyError: string;
  verifyLoading: boolean;
  resendCountdown: number;
  handleRegisterSubmit: (e: React.FormEvent) => void;
  handleVerifyEmail: (e: React.FormEvent) => void;
  handleResendRegister: () => void;
  handleTabSwitch: (tab: 'login' | 'register') => void;
};

const RegisterForm = ({
  regStep, setRegStep,
  firstName, setFirstName,
  lastName, setLastName,
  regUsername, setRegUsername,
  usernameStatus,
  email, setEmail,
  password, setPassword,
  confirmPassword, setConfirmPassword,
  showPasswords, setShowPasswords,
  regError, regLoading,
  strength, passwordsMatch, passwordsMismatch, canRegister,
  otpDigits, setOtpDigits,
  verifyError, verifyLoading, resendCountdown,
  handleRegisterSubmit, handleVerifyEmail, handleResendRegister, handleTabSwitch,
}: Props) => (
  regStep === 'form' ? (
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
            onClick={() => setShowPasswords((s: boolean) => !s)}
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

      <div className="auth-divider">or</div>

      <button
        type="button"
        className="auth-google-btn"
        onClick={() => window.location.href = '/api/auth/google'}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
        </svg>
        Continue with Google
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
  )
);

export default RegisterForm;
