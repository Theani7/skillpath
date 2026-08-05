import { motion } from 'framer-motion';
import { Rocket } from 'lucide-react';
import { fadeUp, VIEW } from './variants';

const CtaSection = (openAuthModal) => (
      <section className="section">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 32 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={VIEW}
            className="mc-cta"
            style={{ textAlign: 'center' }}
          >
            <div style={{ maxWidth: '560px', margin: '0 auto' }}>
              <motion.div variants={fadeUp} style={{ marginBottom: '16px' }}>
                <span className="mc-status" style={{ background: 'rgba(255,107,53,0.15)', color: 'var(--color-secondary)', border: '1px solid rgba(255,107,53,0.3)' }}>
                  Ready for Launch
                </span>
              </motion.div>
              <h2 style={{
                fontSize: 'clamp(28px, 3.5vw, 40px)', fontWeight: 700,
                letterSpacing: '-0.03em', color: 'white', marginBottom: '16px',
              }}>
                Your career deserves a <span style={{ color: 'var(--color-secondary)' }}>mission plan</span>, not guesswork.
              </h2>
              <p style={{
                fontSize: '16px', color: 'rgba(255,255,255,0.7)', lineHeight: 1.7,
                marginBottom: '32px',
              }}>
                Join thousands of job seekers who know exactly what they need to learn next.
              </p>
              <button onClick={() => openAuthModal('register')} className="mc-btn" style={{ fontSize: '16px', padding: '18px 36px' }}>
                <Rocket size={20} />
                Start Your Mission
              </button>
            </div>
          </motion.div>
        </div>
      </section>
);

export default CtaSection;
