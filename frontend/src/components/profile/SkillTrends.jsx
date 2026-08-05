import { motion } from 'framer-motion';
import { TrendingUp } from 'lucide-react';
import { CardHeader } from './ui';

const SkillTrends = ({ skillTrends }) => (

          <motion.div
            initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.22 }}
            className="card"
            style={{ padding: '24px', marginBottom: '24px' }}
          >
            <CardHeader
              icon={TrendingUp}
              title="Skill Trends"
              subtitle={`Based on ${skillTrends.analyses_count} analysis${skillTrends.analyses_count === 1 ? '' : 'es'}`}
            />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {skillTrends.trends.map((trend, i) => {
                const colors = {
                  improved: { bg: 'var(--emerald-50)', fg: 'var(--color-success)', label: 'Resolved Gaps' },
                  gained: { bg: 'var(--indigo-50)', fg: 'var(--color-primary)', label: 'New Skills' },
                  lost: { bg: '#FEF3C7', fg: '#D97706', label: 'Lost Skills' },
                  new_gaps: { bg: 'var(--color-error-light)', fg: 'var(--color-error)', label: 'New Gaps' },
                };
                const c = colors[trend.type] || colors.improved;
                if (trend.count === 0) return null;
                return (
                  <div key={i} style={{
                    padding: '14px 16px', borderRadius: 'var(--radius-md)',
                    background: c.bg, border: `1px solid ${c.fg}20`,
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 600, color: c.fg }}>{c.label}</span>
                      <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>({trend.count})</span>
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {trend.skills.slice(0, 10).map((skill) => (
                        <span key={skill} style={{
                          padding: '3px 8px', borderRadius: 'var(--radius-md)',
                          background: 'white', border: '1px solid var(--color-border)',
                          fontSize: '12px', color: 'var(--color-text)',
                        }}>
                          {skill}
                        </span>
                      ))}
                      {trend.skills.length > 10 && (
                        <span style={{ fontSize: '12px', color: 'var(--color-text-muted)', alignSelf: 'center' }}>
                          +{trend.skills.length - 10} more
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>);

export default SkillTrends;
