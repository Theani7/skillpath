import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Mail, MapPin, Briefcase, UploadCloud, Check, AlertOctagon, X } from 'lucide-react';
import { PrimaryButton } from './ui';
import type { AuthUser, UserProfile } from '../../types';

type Props = {
  user: AuthUser | null;
  profile: UserProfile;
  avatarLetter: string;
  savedProfile: boolean;
  savedPrefs: boolean;
  profileError: string;
  prefsError: string;
  setProfileError: (msg: string) => void;
  setPrefsError: (msg: string) => void;
};

const Header = ({ user, profile, avatarLetter, savedProfile, savedPrefs, profileError, prefsError, setProfileError, setPrefsError }: Props) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
    className="card"
    style={{ padding: '28px 32px', marginBottom: '24px' }}
  >
    <div style={{
      display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '20px',
      justifyContent: 'space-between',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '18px', minWidth: 0 }}>
        <div style={{
          width: '72px', height: '72px', borderRadius: '50%',
          background: 'var(--color-primary)',
          color: 'white', fontSize: '28px', fontWeight: 'var(--font-extrabold)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 6px 20px rgba(255, 107, 53, 0.3)',
          flexShrink: 0,
        }}>
          {avatarLetter}
        </div>
        <div style={{ minWidth: 0 }}>
          <h1 style={{
            fontSize: 'clamp(20px, 3vw, 26px)', fontWeight: 'var(--font-extrabold)',
            letterSpacing: 'var(--tracking-tight)', color: 'var(--color-text)',
            margin: 0, marginBottom: '4px',
          }}>
            {profile.full_name || user?.username || 'Welcome'}
          </h1>
          <div style={{
            display: 'flex', flexWrap: 'wrap', gap: '14px',
            fontSize: '13px', color: 'var(--color-text-muted)',
          }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
              <Mail size={13} /> {user?.email}
            </span>
            {profile.location && (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                <MapPin size={13} /> {profile.location}
              </span>
            )}
            {profile.current_role && (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                <Briefcase size={13} /> {profile.current_job_role}
              </span>
            )}
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', gap: '10px', flexShrink: 0 }}>
        <Link to="/app" style={{ textDecoration: 'none' }}>
          <PrimaryButton>
            <UploadCloud size={14} /> New Analysis
          </PrimaryButton>
        </Link>
      </div>
    </div>

    <AnimatePresence>
      {savedProfile && (
        <motion.div
          initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
          style={{
            marginTop: '16px', padding: '10px 14px',
            background: 'var(--emerald-50)', color: 'var(--color-success)',
            border: '1px solid #A7F3D0', borderRadius: 'var(--radius-md)',
            fontSize: '13px', fontWeight: 'var(--font-semibold)',
            display: 'inline-flex', alignItems: 'center', gap: '6px',
          }}
        >
          <Check size={14} /> Profile saved
        </motion.div>
      )}
      {savedPrefs && (
        <motion.div
          initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
          style={{
            marginTop: '16px', padding: '10px 14px',
            background: 'var(--emerald-50)', color: 'var(--color-success)',
            border: '1px solid #A7F3D0', borderRadius: 'var(--radius-md)',
            fontSize: '13px', fontWeight: 'var(--font-semibold)',
            display: 'inline-flex', alignItems: 'center', gap: '6px',
          }}
        >
          <Check size={14} /> Preferences saved
        </motion.div>
      )}
      {profileError && (
        <motion.div
          initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
          style={{
            marginTop: '16px', padding: '10px 14px',
            background: 'var(--color-error-light)', color: 'var(--color-error)',
            border: '1px solid #FECACA', borderRadius: 'var(--radius-md)',
            fontSize: '13px', fontWeight: 'var(--font-semibold)',
            display: 'inline-flex', alignItems: 'center', gap: '6px',
          }}
        >
          <AlertOctagon size={14} /> {profileError}
          <button
            onClick={() => setProfileError('')}
            style={{
              marginLeft: '6px', background: 'transparent', border: 'none',
              color: 'var(--color-error)', cursor: 'pointer', padding: '0',
              display: 'inline-flex', alignItems: 'center',
            }}
          >
            <X size={12} />
          </button>
        </motion.div>
      )}
      {prefsError && (
        <motion.div
          initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
          style={{
            marginTop: '16px', padding: '10px 14px',
            background: 'var(--color-error-light)', color: 'var(--color-error)',
            border: '1px solid #FECACA', borderRadius: 'var(--radius-md)',
            fontSize: '13px', fontWeight: 'var(--font-semibold)',
            display: 'inline-flex', alignItems: 'center', gap: '6px',
          }}
        >
          <AlertOctagon size={14} /> {prefsError}
          <button
            onClick={() => setPrefsError('')}
            style={{
              marginLeft: '6px', background: 'transparent', border: 'none',
              color: 'var(--color-error)', cursor: 'pointer', padding: '0',
              display: 'inline-flex', alignItems: 'center',
            }}
          >
            <X size={12} />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  </motion.div>
);

export default Header;
er;
