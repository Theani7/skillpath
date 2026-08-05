import { ArrowLeft, ArrowRight, Check, CheckCircle, Eye, EyeOff, KeyRound, Lock, LogIn, Mail, User } from 'lucide-react';
import { OtpBoxes, DevOtpHint } from './otp';
import { OTP_LENGTH, strengthLabel, strengthColor } from './otpUtils';

const LoginForm = ({
  loginStep, setLoginStep,
  loginUsername, setLoginUsername,
  loginPassword, setLoginPassword,
  showLoginPassword, setShowLoginPassword,
  loginError, loginLoading,
  registrationSuccess, forgotSuccess,
  unverifiedAccount,
  resendVerifMsg, resendVerifOtp, resendVerifLoading,
  handleLoginSubmit, handleResendVerification, handleTabSwitch,
  forgotEmail, setForgotEmail,
  forgotError, forgotLoading,
  forgotOtp, setForgotOtp,
  forgotNewPassword, setForgotNewPassword,
  forgotConfirmPassword, setForgotConfirmPassword,
  forgotShowPasswords, setForgotShowPasswords,
  forgotDevOtp, forgotResendCountdown,
  forgotStrength, forgotStrengthsMatch,
  handleForgotRequest, handleForgotReset, handleResendForgot,
}) => (
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
);

export default LoginForm;
