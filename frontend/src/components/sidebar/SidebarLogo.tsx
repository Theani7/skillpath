import { Link } from 'react-router-dom';
import { Zap, ChevronLeft } from 'lucide-react';

type Props = {
  collapsed: boolean;
  onCollapse: () => void;
};

const SidebarLogo = ({ collapsed, onCollapse }: Props) => (
  <div
    style={{
      height: '64px',
      padding: '0 16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: collapsed ? 'center' : 'space-between',
      borderBottom: '1px solid var(--color-border)',
    }}
  >
    <Link to="/app" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center' }}>
      {collapsed ? (
        <div
          style={{
            width: '32px', height: '32px', borderRadius: '10px',
            background: 'var(--color-secondary)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <Zap size={18} color="white" />
        </div>
      ) : (
        <span style={{
          fontWeight: '800', fontSize: '18px',
          letterSpacing: '-0.02em', color: 'var(--color-text)',
        }}>
          Skill<span style={{ color: 'var(--color-secondary)' }}>Path</span>
        </span>
      )}
    </Link>
    {!collapsed && (
      <button
        onClick={onCollapse}
        style={{
          width: '28px', height: '28px', borderRadius: '8px',
          border: 'none', background: 'transparent',
          color: 'var(--color-text-light)', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}
      >
        <ChevronLeft size={16} />
      </button>
    )}
  </div>
);

export default SidebarLogo;
