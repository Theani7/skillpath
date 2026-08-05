import { motion } from 'framer-motion';
import { fadeUp, stagger, VIEW } from './variants';

const StatsBand = () => (
  <section style={{ padding: '48px 0' }}>
    <div className="container">
      <motion.div
        className="mc-stats"
        initial="hidden" whileInView="visible" viewport={VIEW} variants={stagger}
      >
        {[
          { value: '2,847', label: 'Resumes Analyzed' },
          { value: '82%', label: 'Avg Match Score' },
          { value: '<30s', label: 'Analysis Time' },
          { value: '100%', label: 'Free Forever' },
        ].map((s) => (
          <motion.div key={s.label} variants={fadeUp} className="mc-stat">
            <div className="mc-stat-value">{s.value}</div>
            <div className="mc-stat-label">{s.label}</div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  </section>
);

export default StatsBand;
