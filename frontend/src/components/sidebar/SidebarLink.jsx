import { Link } from 'react-router-dom';

const SidebarLink = ({ link, collapsed, active }) => {
  return (
                  <Link
                    to={link.path}
                    title={collapsed ? link.label : undefined}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '10px',
                      height: '36px',
                      padding: collapsed ? '0' : '0 10px',
                      justifyContent: collapsed ? 'center' : 'flex-start',
                      borderRadius: '8px',
                      fontSize: '13px', fontWeight: active ? '600' : '500',
                      textDecoration: 'none',
                      color: active ? 'var(--color-secondary)' : 'var(--color-text-muted)',
                      background: active ? 'rgba(255, 107, 53, 0.1)' : 'transparent',
                      marginBottom: '2px',
                      transition: 'background 100ms ease, color 100ms ease',
                    }}
                    onMouseEnter={(e) => {
                      if (!active) e.currentTarget.style.background = 'var(--color-bg)';
                    }}
                    onMouseLeave={(e) => {
                      if (!active) e.currentTarget.style.background = 'transparent';
                    }}
                  >
                    <Icon size={18} />
                    {!collapsed && <span>{link.label}</span>}
                  </Link>
  );
};

export default SidebarLink;
