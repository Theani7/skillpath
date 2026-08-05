import { useState, useRef, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Settings as SettingsIcon } from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { ConfirmModal, DataPrivacyCard, SecurityCard, DangerCard, SupportCard, SupportModal, Toast } from '../components/settings';

const Settings = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const toastTimer = useRef(null);

  useEffect(() => () => { if (toastTimer.current) clearTimeout(toastTimer.current); }, []);

  const [showLogout, setShowLogout] = useState(false);
  const [showClearHistory, setShowClearHistory] = useState(false);
  const [showDeleteAccount, setShowDeleteAccount] = useState(false);
  const [showContactSupport, setShowContactSupport] = useState(false);

  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState(null);

  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [passwordErrors, setPasswordErrors] = useState({});
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);

  const [deletePassword, setDeletePassword] = useState('');
  const [deleteError, setDeleteError] = useState('');
  const [deleteLoading, setDeleteLoading] = useState(false);

  const [supportForm, setSupportForm] = useState({ subject: '', message: '' });
  const [supportErrors, setSupportErrors] = useState({});
  const [supportLoading, setSupportLoading] = useState(false);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 2600);
  };

  const handleExportData = async () => {
    try {
      const res = await api.get('/api/user/history');
      const profile = await api.get('/api/user/profile');
      const prefs = await api.get('/api/user/preferences');
      const blob = new Blob(
        [JSON.stringify({
          exported_at: new Date().toISOString(),
          user: { username: user?.username, email: user?.email, role: user?.role },
          profile: profile.data.profile,
          preferences: prefs.data.preferences,
          analyses: res.data.history,
        }, null, 2)],
        { type: 'application/json' }
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `skillpath-export-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('Data exported');
    } catch (err) {
      console.error(err);
      showToast('Failed to export data', 'error');
    }
  };

  const handleClearHistory = async () => {
    setBusy(true);
    try {
      await api.delete('/api/user/history');
      setShowClearHistory(false);
      showToast('Analysis history cleared');
    } catch (err) {
      console.error(err);
      showToast('Failed to clear history', 'error');
    } finally {
      setBusy(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    const errors = {};
    if (!passwordForm.currentPassword) errors.currentPassword = 'Current password is required';
    if (!passwordForm.newPassword) errors.newPassword = 'New password is required';
    else if (passwordForm.newPassword.length < 8) errors.newPassword = 'Password must be at least 8 characters';
    if (passwordForm.newPassword !== passwordForm.confirmPassword) errors.confirmPassword = 'Passwords do not match';
    if (passwordForm.currentPassword && passwordForm.newPassword && passwordForm.currentPassword === passwordForm.newPassword) {
      errors.newPassword = 'New password must be different from current password';
    }

    if (Object.keys(errors).length > 0) {
      setPasswordErrors(errors);
      return;
    }

    setPasswordErrors({});
    setPasswordLoading(true);
    try {
      await api.post('/api/auth/change-password', {
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword,
      });
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
      showToast('Password changed successfully');
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        setPasswordErrors({ currentPassword: detail });
      } else if (Array.isArray(detail)) {
        setPasswordErrors({ currentPassword: detail[0]?.msg || 'Failed to change password' });
      } else {
        setPasswordErrors({ currentPassword: 'Failed to change password' });
      }
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!deletePassword) {
      setDeleteError('Password is required');
      return;
    }
    setDeleteError('');
    setDeleteLoading(true);
    try {
      await api.delete('/api/user/account', { data: { password: deletePassword } });
      await logout();
      navigate('/');
    } catch (err) {
      const detail = err.response?.data?.detail;
      setDeleteError(typeof detail === 'string' ? detail : 'Failed to delete account');
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleContactSupport = async (e) => {
    e.preventDefault();
    const errors = {};
    if (!supportForm.subject || supportForm.subject.length < 5) errors.subject = 'Subject must be at least 5 characters';
    if (!supportForm.message || supportForm.message.length < 10) errors.message = 'Message must be at least 10 characters';
    if (Object.keys(errors).length > 0) { setSupportErrors(errors); return; }

    setSupportErrors({});
    setSupportLoading(true);
    try {
      await api.post('/api/user/contact-support', supportForm);
      setSupportForm({ subject: '', message: '' });
      setShowContactSupport(false);
      showToast('Support request submitted');
    } catch (err) {
      const detail = err.response?.data?.detail;
      setSupportErrors({ message: typeof detail === 'string' ? detail : 'Failed to submit' });
    } finally {
      setSupportLoading(false);
    }
  };


  return (
    <div style={{
      minHeight: '100%',
      background: 'var(--color-bg)',
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: '-180px', right: '-150px', width: '480px', height: '480px',
        borderRadius: '50%', opacity: 0.05, pointerEvents: 'none',
        background: 'radial-gradient(circle, var(--color-primary) 0%, transparent 70%)',
      }} />
      <div style={{
        position: 'absolute', bottom: '-200px', left: '-180px', width: '500px', height: '500px',
        borderRadius: '50%', opacity: 0.04, pointerEvents: 'none',
        background: 'radial-gradient(circle, var(--color-secondary) 0%, transparent 70%)',
      }} />

      <div className="container" style={{ position: 'relative', zIndex: 1, maxWidth: '880px' }}>
        <motion.div
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
          style={{ marginBottom: '28px' }}
        >
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '6px',
            padding: '4px 12px', borderRadius: 'var(--radius-full)',
            fontSize: 'var(--text-xs)', fontWeight: 'var(--font-semibold)',
            color: 'var(--color-primary)', background: 'var(--indigo-50)',
            border: '1px solid var(--indigo-100)', marginBottom: '14px',
          }}>
            <SettingsIcon size={11} /> Account
          </div>
          <h1 style={{
            fontSize: 'clamp(28px, 4vw, 34px)', fontWeight: 'var(--font-extrabold)',
            letterSpacing: 'var(--tracking-tight)', color: 'var(--color-text)', margin: 0, marginBottom: '6px',
          }}>
            Settings
          </h1>
          <p style={{ fontSize: '15px', color: 'var(--color-text-muted)', margin: 0 }}>
            Manage your data and account.
          </p>
          <p style={{ fontSize: '13px', color: 'var(--color-text-light)', margin: '10px 0 0' }}>
            To update your name, contact info, or career preferences, visit{' '}
            <Link to="/profile" style={{ color: 'var(--color-primary)', fontWeight: 'var(--font-semibold)' }}>Profile</Link>.
          </p>
        </motion.div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <DataPrivacyCard handleExportData={handleExportData} onClearHistory={() => setShowClearHistory(true)} />
          <SecurityCard
            passwordForm={passwordForm} setPasswordForm={setPasswordForm}
            passwordErrors={passwordErrors} passwordLoading={passwordLoading}
            showCurrentPassword={showCurrentPassword} setShowCurrentPassword={setShowCurrentPassword}
            showNewPassword={showNewPassword} setShowNewPassword={setShowNewPassword}
            handlePasswordChange={handlePasswordChange}
          />
          <DangerCard onLogout={() => setShowLogout(true)} onDelete={() => setShowDeleteAccount(true)} />
          <SupportCard onOpen={() => setShowContactSupport(true)} />
        </div>
      </div>

      <ConfirmModal
        open={showLogout}
        onClose={() => setShowLogout(false)}
        onConfirm={handleLogout}
        title="Log out?"
        message="You'll need to sign in again to access your account."
        confirmText="Log out"
      />

      <ConfirmModal
        open={showClearHistory}
        onClose={() => setShowClearHistory(false)}
        onConfirm={handleClearHistory}
        title="Clear analysis history?"
        message="This permanently removes every past resume analysis. Your profile and preferences are kept."
        confirmText="Clear history"
        danger
        busy={busy}
      />

      <ConfirmModal
        open={showDeleteAccount}
        onClose={() => { setShowDeleteAccount(false); setDeletePassword(''); setDeleteError(''); }}
        onConfirm={handleDeleteAccount}
        title="Delete account?"
        message="This permanently removes your account and all associated data. Enter your password to confirm."
        confirmText="Delete account"
        danger
        busy={deleteLoading}
      >
        <div style={{ marginTop: '12px', textAlign: 'left' }}>
          <input
            type="password"
            placeholder="Enter your password"
            value={deletePassword}
            onChange={(e) => setDeletePassword(e.target.value)}
            style={{
              width: '100%', height: '40px', padding: '0 12px',
              borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)',
              background: 'var(--color-surface)', color: 'var(--color-text)', fontSize: '14px',
              outline: 'none', boxSizing: 'border-box',
            }}
          />
          {deleteError && (
            <p style={{ fontSize: '12px', color: 'var(--color-error)', margin: '4px 0 0' }}>{deleteError}</p>
          )}
        </div>
      </ConfirmModal>

      <SupportModal
        showContactSupport={showContactSupport}
        onClose={() => setShowContactSupport(false)}
        supportForm={supportForm} setSupportForm={setSupportForm}
        supportErrors={supportErrors} supportLoading={supportLoading}
        handleContactSupport={handleContactSupport}
      />

      <Toast toast={toast} />
    </div>
  );
};

export default Settings;
