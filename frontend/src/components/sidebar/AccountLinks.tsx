import { BOTTOM_LINKS } from './navData';
import SidebarLink from './SidebarLink';
import type { NavItem } from './navData';

type Props = {
  collapsed: boolean;
  activePath: string;
};

const AccountLinks = ({ collapsed, activePath }: Props) => (
  <div style={{ marginBottom: '20px' }}>
    {!collapsed && (
      <div style={{
        fontSize: '11px', fontWeight: '600',
        textTransform: 'uppercase', letterSpacing: '0.06em',
        color: 'var(--color-text-light)',
        padding: '0 8px', marginBottom: '6px',
      }}>
        Account
      </div>
    )}
    {BOTTOM_LINKS.map((link: NavItem) => (
      <SidebarLink key={link.path} link={link} collapsed={collapsed} active={activePath === link.path} />
    ))}
  </div>
);

export default AccountLinks;
