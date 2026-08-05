import { motion } from 'framer-motion';
import { Zap, Lock, Sparkles } from 'lucide-react';
import { fadeUp, stagger, VIEW } from './variants';
import type { LucideIcon } from 'lucide-react';

type WhyItem = {
  icon: LucideIcon;
  t: string;
  b: string;
};

const items: WhyItem[] = [
  { icon: Zap, t: 'Fast where it matters', b: 'Most analyses finish in under 30 seconds. Local parsing handles the common case so the AI is reserved for the hard parts.' },
  { icon: Lock, t: 'Your data stays yours', b: 'Resumes are stored against your account only. Nothing is sold, nothing is shared with third parties, and one click deletes everything.' },
  { icon: Sparkles, t: 'Personal, not generic', b: 'Every recommendation is built from your actual skills and the role you pick - no boilerplate content.' },
];

const WhySkillPath = () => (
  <section id="why-skillpath" className="section">
    <div className="container">
      <motion.div
        initial="hidden" whileInView="visible" viewport={VIEW} variants={stagger}
        style={{ textAlign: 'center', marginBottom: '48px', maxWidth: '600px', margin: '0 auto 48px' }}
      >
        <motion.div variants={fadeUp} style={{ marginBottom: '16px' }}>
          <span className="mc-status mc-status-active">Mission Brief</span>
        </motion.div>
        <motion.h2 variants={fadeUp} style={{
          fontSize: 'clamp(28px, 3.5vw, 44px)', fontWeight: 700,
          letterSpacing: '-0.03em', color: 'var(--color-text)', marginBottom: '12px',
        }}>
          Built like a tool,
          <br />
          <span className="mc-gradient">not a marketing site.</span>
        </motion.h2>
      </motion.div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '20px',
      }}>
        {items.map((d, i) => {
          const Icon = d.icon;
          return (
            <motion.div
              key={d.t}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={VIEW}
              transition={{ delay: i * 0.1 }}
              className="mc-card mc-feature"
            >
              <div className="mc-feature-icon" style={{ background: 'var(--color-secondary)', color: 'white' }}>
                <Icon size={22} />
              </div>
              <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-text)', marginBottom: '8px' }}>{d.t}</h3>
              <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', lineHeight: 1.6, margin: 0 }}>{d.b}</p>
            </motion.div>
          );
        })}
      </div>
    </div>
  </section>
);

export default WhySkillPath;
