import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { User, Settings, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { AuthUser } from '../../types';

type Props = {
  user: AuthUser | null;
  collapsed: boolean;
  onLogoutRequest: () => void;
};

const UserMenu = ({ user, collapsed, onLogoutRequest }: Props) => {
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const userSubtitle = user?.email || (user?.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : '');

  useEffect(() => {
    if (!userMenuOpen) return;
    const handleClick = (e: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [userMenuOpen]);

  return (
    <div
      style={{
        borderTop: '1px solid var(--color-border)',
        padding: '8px',
        position: 'relative',
      }}
      ref={userMenuRef}
    >
      <AnimatePresence>
        {userMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            style={{
              position: 'fixed',
              bottom: '70px',
              left: collapsed ? '72px' : '8px',
              width: '200px',
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: '12px',
              boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
              padding: '6px', zIndex: 100,
            }}
          >
            <div style={{ padding: '10px 12px', borderBottom: '1px solid var(--color-border)', marginBottom: '4px' }}>
              <p style={{ fontSize: '13px', fontWeight: '600', color: 'var(--color-text)', margin: 0 }}>
                {user?.full_name || user?.username}
              </p>
              <p style={{ fontSize: '11px', color: 'var(--color-text-muted)', margin: '2px 0 0', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {userSubtitle}
              </p>
            </div>
            <Link
              to="/profile"
              onClick={() => setUserMenuOpen(false)}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '8px 12px', borderRadius: '8px',
                fontSize: '13px', color: 'var(--color-text)', textDecoration: 'none',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--color-bg)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              <User size={14} /> View profile
            </Link>
            <Link
              to="/settings"
              onClick={() => setUserMenuOpen(false)}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '8px 12px', borderRadius: '8px',
                fontSize: '13px', color: 'var(--color-text)', textDecoration: 'none',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--color-bg)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              <Settings size={14} /> Settings
            </Link>
            <div style={{ height: '1px', background: 'var(--color-border)', margin: '4px 0' }} />
            <button
              onClick={onLogoutRequest}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '8px 12px', borderRadius: '8px',
                fontSize: '13px', color: 'var(--color-error)',
                background: 'transparent', border: 'none', cursor: 'pointer', width: '100%',
                textAlign: 'left',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--color-error-light)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              <LogOut size={14} /> Log out
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <button
        onClick={() => setUserMenuOpen(!userMenuOpen)}
        style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          width: '100%',
          padding: collapsed ? '6px' : '8px',
          justifyContent: collapsed ? 'center' : 'flex-start',
          borderRadius: '8px',
          border: 'none',
          background: 'transparent',
          cursor: 'pointer',
          color: 'var(--color-text)',
          transition: 'background 100ms ease',
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = 'var(--color-bg)'}
        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
      >
        <div style={{
          width: '32px', height: '32px', borderRadius: '50%',
          background: 'var(--color-secondary)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'white', fontSize: '13px', fontWeight: '700', flexShrink: 0,
        }}>
          {(user?.full_name || user?.username || '?').charAt(0).toUpperCase()}
        </div>
        {!collapsed && (
          <div style={{ flex: 1, minWidth: 0, textAlign: 'left' }}>
            <div style={{ fontSize: '13px', fontWeight: '600', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {user?.full_name || user?.username}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {userSubtitle}
            </div>
          </div>
        )}
      </button>
    </div>
  );
};

export default UserMenu;
