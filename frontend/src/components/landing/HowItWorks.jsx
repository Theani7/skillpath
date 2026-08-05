import { motion } from 'framer-motion';
import { fadeUp, stagger, VIEW } from './variants';
import { steps } from './landingData';

const HowItWorks = () => (
      <section id="how-it-works" className="section" style={{ background: 'var(--navy-950)', color: 'white' }}>
        <div className="container">
          <motion.div
            initial="hidden" whileInView="visible" viewport={VIEW} variants={stagger}
            style={{ textAlign: 'center', marginBottom: '48px', maxWidth: '560px', margin: '0 auto 48px' }}
          >
            <motion.div variants={fadeUp} style={{ marginBottom: '16px' }}>
              <span className="mc-status" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--color-secondary)', border: '1px solid rgba(255,255,255,0.12)' }}>
                Launch Sequence
              </span>
            </motion.div>
            <motion.h2 variants={fadeUp} style={{
              fontSize: 'clamp(28px, 3.5vw, 44px)', fontWeight: 700,
              letterSpacing: '-0.03em', color: 'white', marginBottom: '12px',
            }}>
              Four steps to launch.
            </motion.h2>
            <motion.p variants={fadeUp} style={{
              fontSize: '16px', color: 'rgba(255,255,255,0.6)', lineHeight: 1.7, margin: 0,
            }}>
              From a fresh PDF to a tracked application, with a real plan in between.
            </motion.p>
          </motion.div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '20px',
          }}>
            {steps.map((s, i) => {
              const Icon = s.icon;
              return (
                <motion.div
                  key={s.num}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={VIEW}
                  transition={{ delay: i * 0.12 }}
                  className="mc-step"
                  style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.08)' }}
                >
                  <div className="mc-step-num">{s.num}</div>
                  <div style={{
                    width: '44px', height: '44px', borderRadius: '12px',
                    background: 'var(--color-secondary)',
                    color: 'white',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    marginBottom: '16px',
                  }}>
                    <Icon size={20} />
                  </div>
                  <h3 style={{
                    fontSize: '17px', fontWeight: 700,
                    color: 'white', marginBottom: '8px',
                  }}>
                    {s.title}
                  </h3>
                  <p style={{
                    fontSize: '14px', color: 'rgba(255,255,255,0.6)',
                    lineHeight: 1.6, margin: 0,
                  }}>
                    {s.body}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>
);

export default HowItWorks;
