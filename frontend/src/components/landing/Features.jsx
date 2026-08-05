import { motion } from 'framer-motion';
import { fadeUp, stagger, launch, VIEW } from './variants';
import { features } from './landingData';

const Features = () => (
      <section id="features" className="section">
        <div className="container">
          <motion.div
            initial="hidden" whileInView="visible" viewport={VIEW} variants={stagger}
            style={{ textAlign: 'center', marginBottom: '48px', maxWidth: '640px', margin: '0 auto 48px' }}
          >
            <motion.div variants={fadeUp} style={{ marginBottom: '16px' }}>
              <span className="mc-status mc-status-active">System Status</span>
            </motion.div>
            <motion.h2 variants={fadeUp} style={{
              fontSize: 'clamp(28px, 3.5vw, 44px)', fontWeight: 700,
              letterSpacing: '-0.03em', color: 'var(--color-text)', marginBottom: '12px',
            }}>
              Mission Control Dashboard,
              <br />
              <span className="mc-gradient">for your career.</span>
            </motion.h2>
            <motion.p variants={fadeUp} style={{
              fontSize: '16px', color: 'var(--color-text-muted)', lineHeight: 1.7, margin: 0,
            }}>
              Every tool you need to analyze, plan, and track your job search - 
              all in one place. No subscription, no paywall.
            </motion.p>
          </motion.div>

          <motion.div
            className="mc-bento"
            initial="hidden" whileInView="visible" viewport={VIEW} variants={stagger}
          >
            {features.map((f, i) => {
              const Icon = f.icon;
              return (
                <motion.div
                  key={f.title}
                  variants={launch}
                  custom={i}
                  className="mc-card mc-feature"
                >
                  <span className="mc-feature-status">{f.status}</span>
                  <div className="mc-feature-icon">
                    <Icon size={24} />
                  </div>
                  <h3 style={{
                    fontSize: '18px', fontWeight: 700, color: 'var(--color-text)',
                    marginBottom: '8px', letterSpacing: '-0.01em',
                  }}>
                    {f.title}
                  </h3>
                  <p style={{
                    fontSize: '14px', color: 'var(--color-text-muted)',
                    lineHeight: 1.6, margin: 0,
                  }}>
                    {f.body}
                  </p>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>
);

export default Features;
