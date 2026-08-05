import { Link } from 'react-router-dom';
import { Zap } from 'lucide-react';

type Props = {
  openAuthModal: (mode: 'login' | 'register') => void;
};

const Footer = ({ openAuthModal }: Props) => (
  <footer style={{
    borderTop: '1px solid var(--color-border)',
    background: 'var(--color-surface)',
    padding: '40px 0 28px',
  }}>
    <div className="container">
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '32px', marginBottom: '32px',
      }}>
        <div>
          <Link to="/" style={{
            display: 'inline-flex', alignItems: 'center', gap: '10px',
            textDecoration: 'none', color: 'var(--color-text)', marginBottom: '12px',
          }}>
            <div style={{
              width: '32px', height: '32px', borderRadius: '8px',
              background: 'var(--navy-950)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Zap size={16} color="var(--color-secondary)" />
            </div>
            <span style={{ fontWeight: 700, fontSize: '16px', letterSpacing: '-0.02em', fontFamily: 'var(--font-display)' }}>
              Skill<span className="mc-gradient">Path</span>
            </span>
          </Link>
          <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', lineHeight: 1.6, margin: 0, maxWidth: '260px' }}>
            An AI career intelligence tool for job seekers who would rather know than guess.
          </p>
        </div>

        <div>
          <h4 style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '14px', fontFamily: 'var(--font-display)' }}>Product</h4>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <li><a href="#features" style={{ fontSize: '14px', color: 'var(--color-text-muted)', textDecoration: 'none' }}>Features</a></li>
            <li><a href="#how-it-works" style={{ fontSize: '14px', color: 'var(--color-text-muted)', textDecoration: 'none' }}>How it works</a></li>
          </ul>
        </div>

        <div>
          <h4 style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '14px', fontFamily: 'var(--font-display)' }}>Account</h4>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <li><button onClick={() => openAuthModal('login')} style={{ fontSize: '14px', color: 'var(--color-text-muted)', textDecoration: 'none', background: 'none', border: 'none', cursor: 'pointer', padding: 0, font: 'inherit' }}>Sign in</button></li>
            <li><button onClick={() => openAuthModal('register')} style={{ fontSize: '14px', color: 'var(--color-text-muted)', textDecoration: 'none', background: 'none', border: 'none', cursor: 'pointer', padding: 0, font: 'inherit' }}>Create account</button></li>
          </ul>
        </div>
      </div>

      <div className="mc-divider" style={{ marginBottom: '24px' }} />

      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexWrap: 'wrap', gap: '12px',
      }}>
        <p style={{ fontSize: '12px', color: 'var(--color-text-light)', margin: 0 }}>
          &copy; {new Date().getFullYear()} SkillPath
        </p>
      </div>
    </div>
  </footer>
);

export default Footer;
