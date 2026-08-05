import { Lock, Eye, EyeOff } from 'lucide-react';
import { Section } from './';

const SecurityCard = (passwordForm, setPasswordForm, passwordErrors, passwordLoading, showCurrentPassword, setShowCurrentPassword, showNewPassword, setShowNewPassword, handlePasswordChange) => (
          <Section
            icon={Lock}
            title="Security"
            description="Change your password."
            accent="indigo"
          >
            <form onSubmit={handlePasswordChange}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', maxWidth: '400px' }}>
                <div>
                  <label style={{ fontSize: '13px', fontWeight: 'var(--font-semibold)', color: 'var(--color-text)', display: 'block', marginBottom: '6px' }}>
                    Current Password
                  </label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type={showCurrentPassword ? 'text' : 'password'}
                      value={passwordForm.currentPassword}
                      onChange={(e) => setPasswordForm({ ...passwordForm, currentPassword: e.target.value })}
                      style={{
                        width: '100%', height: '40px', padding: '0 40px 0 12px',
                        borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)',
                        background: 'var(--color-surface)', color: 'var(--color-text)', fontSize: '14px',
                        outline: 'none',
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      style={{
                        position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)',
                        background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)',
                        padding: '4px',
                      }}
                    >
                      {showCurrentPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  {passwordErrors.currentPassword && (
                    <p style={{ fontSize: '12px', color: 'var(--color-error)', margin: '4px 0 0' }}>{passwordErrors.currentPassword}</p>
                  )}
                </div>

                <div>
                  <label style={{ fontSize: '13px', fontWeight: 'var(--font-semibold)', color: 'var(--color-text)', display: 'block', marginBottom: '6px' }}>
                    New Password
                  </label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type={showNewPassword ? 'text' : 'password'}
                      value={passwordForm.newPassword}
                      onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                      style={{
                        width: '100%', height: '40px', padding: '0 40px 0 12px',
                        borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)',
                        background: 'var(--color-surface)', color: 'var(--color-text)', fontSize: '14px',
                        outline: 'none',
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      style={{
                        position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)',
                        background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)',
                        padding: '4px',
                      }}
                    >
                      {showNewPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  {passwordErrors.newPassword && (
                    <p style={{ fontSize: '12px', color: 'var(--color-error)', margin: '4px 0 0' }}>{passwordErrors.newPassword}</p>
                  )}
                </div>

                <div>
                  <label style={{ fontSize: '13px', fontWeight: 'var(--font-semibold)', color: 'var(--color-text)', display: 'block', marginBottom: '6px' }}>
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    value={passwordForm.confirmPassword}
                    onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                    style={{
                      width: '100%', height: '40px', padding: '0 12px',
                      borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)',
                      background: 'var(--color-surface)', color: 'var(--color-text)', fontSize: '14px',
                      outline: 'none',
                    }}
                  />
                  {passwordErrors.confirmPassword && (
                    <p style={{ fontSize: '12px', color: 'var(--color-error)', margin: '4px 0 0' }}>{passwordErrors.confirmPassword}</p>
                  )}
                </div>

                <p style={{ fontSize: '12px', color: 'var(--color-text-light)', margin: 0 }}>
                  Password must be at least 8 characters and different from your current password.
                </p>

                <button
                  type="submit"
                  disabled={passwordLoading}
                  style={{
                    alignSelf: 'flex-start', height: '38px', padding: '0 20px',
                    borderRadius: 'var(--radius-md)', background: 'var(--color-primary)',
                    color: 'white', fontSize: '13px', fontWeight: 'var(--font-semibold)',
                    border: 'none', cursor: passwordLoading ? 'not-allowed' : 'pointer',
                    opacity: passwordLoading ? 0.7 : 1,
                  }}
                >
                  {passwordLoading ? 'Changing...' : 'Change Password'}
                </button>
              </div>
            </form>
          </Section>
);

export default SecurityCard;
