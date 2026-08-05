import { Link, useLocation } from 'react-router-dom';

const scrollToSection = (id: string) => {
  const element = document.getElementById(id);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

type Props = {
  openAuthModal: (tab: 'login' | 'register') => void;
};

const PublicTopBar = ({ openAuthModal }: Props) => {
  const location = useLocation();
  const isLanding = location.pathname === '/';

  const navLinks = [
    { label: 'Features', id: 'features' },
    { label: 'How it works', id: 'how-it-works' },
    { label: 'Why SkillPath', id: 'why-skillpath' },
  ];

  const handleNavClick = (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    if (isLanding) {
      scrollToSection(id);
    } else {
      window.location.assign(`/#${id}`);
    }
  };

  const handleLogoClick = (e: React.MouseEvent) => {
    if (isLanding) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <header
      style={{
        position: 'sticky', top: 0, zIndex: 30,
        background: 'var(--color-surface)',
        borderBottom: '1px solid var(--color-border)',
        height: '64px',
        display: 'flex',
        alignItems: 'center',
      }}
      className="public-topbar"
    >
      <div style={{
        flex: 1,
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <Link
          to="/"
          onClick={handleLogoClick}
          style={{ textDecoration: 'none' }}
        >
          <span style={{
            fontWeight: 'var(--font-extrabold)', fontSize: '20px',
            letterSpacing: 'var(--tracking-tight)',
            color: 'var(--color-text)',
          }}>
            Skill<span className="mc-gradient">Path</span>
          </span>
        </Link>

        <nav style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
          {navLinks.map((link) => (
            <a
              key={link.id}
              href={`#${link.id}`}
              onClick={(e) => handleNavClick(e, link.id)}
              style={{
                fontSize: '15px',
                fontWeight: '500',
                color: 'var(--color-text-muted)',
                textDecoration: 'none',
                transition: 'color 150ms ease',
              }}
              onMouseEnter={(e) => e.currentTarget.style.color = 'var(--color-text)'}
              onMouseLeave={(e) => e.currentTarget.style.color = 'var(--color-text-muted)'}
            >
              {link.label}
            </a>
          ))}
        </nav>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        paddingRight: '24px',
        marginLeft: 'auto',
      }}>
        <button
          onClick={() => openAuthModal('login')}
          className="btn btn-primary"
          style={{
            padding: '10px 24px',
            fontSize: '14px',
            fontWeight: '500',
            borderRadius: '50px',
          }}
        >
          Log in
        </button>
        <button
          onClick={() => openAuthModal('register')}
          className="btn btn-secondary"
          style={{
            padding: '10px 24px',
            fontSize: '14px',
            fontWeight: '500',
            borderRadius: '50px',
            background: 'var(--slate-100)',
            border: '1px solid var(--slate-200)',
          }}
        >
          Sign up
        </button>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .public-topbar nav { display: none !important; }
        }
        html {
          scroll-behavior: smooth;
        }
      `}</style>
    </header>
  );
};

export default PublicTopBar;
