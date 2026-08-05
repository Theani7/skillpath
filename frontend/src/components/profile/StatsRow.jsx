import { motion } from 'framer-motion';
import { Award, TrendingUp, Activity, FileText } from 'lucide-react';

const StatsRow = ({ hasHistory, latestScore, bestScore, avgScore, totalAnalyses, getScoreColor }) => (

        <motion.div
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.05 }}
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
            gap: '12px', marginBottom: '24px',
          }}
        >
          {[
            { label: 'Latest Score', value: hasHistory ? `${latestScore}%` : '—', color: getScoreColor(latestScore), icon: Award },
            { label: 'Best Score', value: hasHistory ? `${bestScore}%` : '—', color: getScoreColor(bestScore), icon: TrendingUp },
            { label: 'Average', value: hasHistory ? `${avgScore}%` : '—', color: 'var(--color-primary)', icon: Activity },
            { label: 'Analyses', value: totalAnalyses, color: 'var(--color-text)', icon: FileText },
          ].map((s) => (
            <div key={s.label} className="card" style={{ padding: '20px' }}>
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px',
              }}>
                <span style={{
                  fontSize: '11px', fontWeight: 'var(--font-bold)',
                  textTransform: 'uppercase', letterSpacing: '0.06em',
                  color: 'var(--color-text-muted)',
                }}>
                  {s.label}
                </span>
                <div style={{
                  width: '28px', height: '28px', borderRadius: 'var(--radius-md)',
                  background: 'var(--color-bg)', color: s.color,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <s.icon size={14} />
                </div>
              </div>
              <div style={{
                fontSize: '26px', fontWeight: 'var(--font-extrabold)',
                color: s.color, letterSpacing: 'var(--tracking-tight)', lineHeight: 1,
              }}>
                {s.value}
              </div>
            </div>
          ))}
        </motion.div>);

export default StatsRow;
