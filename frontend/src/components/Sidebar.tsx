import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { SECTIONS, ADMIN_SECTION } from './sidebar/navData';
import SidebarLogo from './sidebar/SidebarLogo';
import NavSectionComponent from './sidebar/NavSection';
import AccountLinks from './sidebar/AccountLinks';
import UserMenu from './sidebar/UserMenu';
import LogoutModal from './sidebar/LogoutModal';

const STORAGE_KEY = 'skillpath_sidebar_collapsed';

const Sidebar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const [collapsed, setCollapsed] = useState(() => {
    try { return localStorage.getItem(STORAGE_KEY) === '1'; } catch { return false; }
  });
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, collapsed ? '1' : '0'); } catch { /* storage may be unavailable (private mode) */ }
  }, [collapsed]);

  const sidebarWidth = collapsed ? 64 : 220;

  const isAdmin = user?.role === 'admin';
  const sectionsToRender = isAdmin ? [ADMIN_SECTION] : [...SECTIONS];

  return (
    <>
      <aside
        style={{
          position: 'sticky',
          top: 0,
          height: '100vh',
          width: sidebarWidth,
          minWidth: sidebarWidth,
          background: 'var(--color-surface)',
          borderRight: '1px solid var(--color-border)',
          display: 'flex',
          flexDirection: 'column',
          transition: 'width 200ms ease, min-width 200ms ease',
          overflow: 'hidden',
          zIndex: 40,
        }}
      >
        <SidebarLogo collapsed={collapsed} onCollapse={() => setCollapsed(true)} />

        <nav style={{ flex: 1, padding: '12px 8px', overflowY: 'auto', overflowX: 'hidden' }}>
          {sectionsToRender.map((section) => (
            <NavSectionComponent key={section.label} section={section} collapsed={collapsed} activePath={location.pathname} />
          ))}
          <AccountLinks collapsed={collapsed} activePath={location.pathname} />
        </nav>

        {collapsed && (
          <div style={{ padding: '0 8px 8px' }}>
            <button
              onClick={() => setCollapsed(false)}
              style={{
                width: '100%', height: '36px', borderRadius: '8px',
                border: 'none', background: 'var(--color-bg)',
                color: 'var(--color-text-muted)', cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}
            >
              <ChevronRight size={16} />
            </button>
          </div>
        )}

        <UserMenu user={user} collapsed={collapsed} onLogoutRequest={() => setShowLogoutConfirm(true)} />
      </aside>

      <LogoutModal
        show={showLogoutConfirm}
        onClose={() => setShowLogoutConfirm(false)}
        onConfirm={async () => { await logout(); }}
      />
    </>
  );
};

export default Sidebar;
