import { motion } from 'framer-motion';
import { Rocket, Zap, Lock, Clock, CheckCircle } from 'lucide-react';
import { fadeUp, stagger } from './variants';
import { matchSkills, gapSkills } from './landingData';

type Props = {
  openAuthModal: (mode: 'login' | 'register') => void;
};

const Hero = ({ openAuthModal }: Props) => (
  <section style={{ padding: '80px 0 96px', position: 'relative', overflow: 'hidden' }}>
    <div className="mc-grid-bg" />
    <div style={{
      position: 'absolute', top: '-200px', right: '-150px',
      width: '500px', height: '500px', borderRadius: '50%',
      background: 'radial-gradient(circle, rgba(255, 107, 53, 0.12), transparent 70%)',
      filter: 'blur(40px)', pointerEvents: 'none',
    }} />
    <div style={{
      position: 'absolute', bottom: '-200px', left: '-150px',
      width: '500px', height: '500px', borderRadius: '50%',
      background: 'radial-gradient(circle, rgba(10, 22, 40, 0.08), transparent 70%)',
      filter: 'blur(40px)', pointerEvents: 'none',
    }} />

    <div className="container" style={{ position: 'relative' }}>
      <div className="mc-hero-grid">
        <motion.div initial="hidden" animate="visible" variants={stagger}>
          <motion.h1
            variants={fadeUp}
            style={{
              fontSize: 'clamp(42px, 6vw, 76px)',
              fontWeight: 700,
              letterSpacing: '-0.04em',
              lineHeight: 1,
              color: 'var(--color-text)',
              marginBottom: '24px',
            }}
          >
            Know exactly{' '}
            <span className="mc-gradient">what stands</span>
            <br />
            between you and the role.
          </motion.h1>

          <motion.p
            variants={fadeUp}
            style={{
              fontSize: 'clamp(16px, 1.4vw, 18px)',
              color: 'var(--color-text-muted)',
              lineHeight: 1.7,
              maxWidth: '500px',
              marginBottom: '32px',
            }}
          >
            SkillPath reads your resume, compares it to a target role, and
            hands you a clear, personalized plan to close the gap.
          </motion.p>

          <motion.div
            variants={fadeUp}
            style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '32px' }}
          >
            <button onClick={() => openAuthModal('register')} className="mc-btn">
              <Rocket size={18} />
              Launch Your Analysis
            </button>
            <button onClick={() => openAuthModal('login')} className="mc-btn mc-btn-secondary">
              Sign In
            </button>
          </motion.div>

          <motion.div
            variants={fadeUp}
            style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}
          >
            <span className="mc-pill">
              <Zap size={14} color="var(--color-secondary)" />
              Powered by Gemini
            </span>
            <span className="mc-pill">
              <Lock size={14} />
              Private by default
            </span>
            <span className="mc-pill">
              <Clock size={14} />
              ~30 seconds
            </span>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40, rotate: -1 }}
          animate={{ opacity: 1, y: 0, rotate: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] as const }}
          style={{ position: 'relative' }}
        >
          <div className="mc-mock" style={{ transform: 'rotate(-1deg)' }}>
            <div className="mc-header">
              <div className="mc-header-dots">
                <span /><span /><span />
              </div>
              <span className="mc-header-title">skillpath.ai / analyzer</span>
              <span className="mc-header-status">LIVE</span>
            </div>
            <div style={{ padding: '28px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
                <div>
                  <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                    Target Role
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--color-text)', marginTop: '4px' }}>
                    Senior Frontend Engineer
                  </div>
                </div>
                <span className="mc-status mc-status-active" style={{ fontSize: '9px', padding: '4px 10px' }}>
                  <CheckCircle size={10} /> Analyzed
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '24px' }}>
                <div style={{ position: 'relative', width: '100px', height: '100px', flexShrink: 0 }}>
                  <svg width="100" height="100" viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
                    <circle cx="50" cy="50" r="42" fill="none" stroke="var(--color-border)" strokeWidth="8" />
                    <motion.circle
                      cx="50" cy="50" r="42" fill="none"
                      stroke="var(--color-secondary)" strokeWidth="8"
                      strokeLinecap="round"
                      strokeDasharray="264"
                      initial={{ strokeDashoffset: 264 }}
                      animate={{ strokeDashoffset: 264 - (264 * 0.82) }}
                      transition={{ duration: 1.5, delay: 0.5, ease: [0.22, 1, 0.36, 1] as const }}
                    />
                  </svg>
                  <div style={{
                    position: 'absolute', inset: 0,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <span style={{ fontSize: '28px', fontWeight: 700, color: 'var(--color-text)' }}>82</span>
                  </div>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '6px' }}>
                    Match Score
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--color-text-muted)', lineHeight: 1.6 }}>
                    Strong fit. Two skills are pulling the score down.
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)' }}>Matched Skills</span>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-success)' }}>6/8</span>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                    {matchSkills.map(s => (
                      <span key={s} style={{
                        display: 'inline-flex', alignItems: 'center', gap: '3px',
                        padding: '3px 8px', borderRadius: 'var(--radius-full)',
                        fontSize: '10px', fontWeight: 600,
                        background: 'var(--green-50)', color: 'var(--color-success)',
                      }}>{s}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)' }}>Skill Gaps</span>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-error)' }}>2/8</span>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                    {gapSkills.map(s => (
                      <span key={s} style={{
                        display: 'inline-flex', alignItems: 'center', gap: '3px',
                        padding: '3px 8px', borderRadius: 'var(--radius-full)',
                        fontSize: '10px', fontWeight: 600,
                        background: 'var(--color-error-light)', color: 'var(--color-error)',
                      }}>{s}</span>
                    ))}
                  </div>
                </div>
              </div>

              <div style={{
                background: 'var(--navy-950)', borderRadius: 'var(--radius-lg)', padding: '14px 16px',
                display: 'flex', alignItems: 'flex-start', gap: '10px',
              }}>
                <Rocket size={16} color="var(--color-secondary)" style={{ marginTop: '2px', flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-secondary)', marginBottom: '2px' }}>
                    Next Launch
                  </div>
                  <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.8)', lineHeight: 1.5 }}>
                    Learn Kubernetes - closes your biggest gap.
                  </div>
                </div>
              </div>
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="mc-float"
            style={{ right: '-20px', top: '35%', transform: 'rotate(3deg)' }}
          >
            <div style={{
              width: '40px', height: '40px', borderRadius: '10px',
              background: 'var(--green-50)', color: 'var(--color-success)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <CheckCircle size={20} />
            </div>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-text)' }}>+12 score</div>
              <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>after learning K8s</div>
            </div>
          </motion.div>

          <div className="mc-doodle" style={{ bottom: '20px', left: '-40px' }}>
            ← so cool!
          </div>
        </motion.div>
      </div>
    </div>
  </section>
);

export default Hero;
