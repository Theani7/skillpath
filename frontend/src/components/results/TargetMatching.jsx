import { motion } from 'framer-motion';
import { Target } from 'lucide-react';

const TargetMatching = ({ matchScore, targetRole }) => {
  return (
        <div className="card" style={{ padding: '24px' }}>
          <h3 style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            fontSize: '16px', fontWeight: 'var(--font-bold)',
            color: 'var(--color-text)', marginBottom: '20px',
          }}>
            <span style={{
              width: '32px', height: '32px', borderRadius: 'var(--radius-md)',
              background: 'var(--indigo-50)', color: 'var(--color-primary)',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Target size={16} />
            </span>
            Target Matching
          </h3>
          <div style={{ marginBottom: '12px' }}>
            <div style={{
              display: 'flex', justifyContent: 'space-between',
              marginBottom: '8px',
            }}>
              <span style={{ fontSize: '14px', fontWeight: 500, color: 'var(--color-text)' }}>
                Role Alignment
              </span>
              <span style={{ fontSize: '14px', fontWeight: 'var(--font-bold)', color: 'var(--color-text)' }}>
                {matchScore ?? 0}%
              </span>
            </div>
            <div style={{
              height: '8px', width: '100%', borderRadius: 'var(--radius-full)',
              background: 'var(--color-border)', overflow: 'hidden',
            }}>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${matchScore ?? 0}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
                style={{
                  height: '100%',
                  background: 'var(--color-primary)',
                  borderRadius: 'var(--radius-full)',
                }}
              />
            </div>
          </div>
          <p style={{
            fontSize: '12px', color: 'var(--color-text-muted)',
            fontStyle: 'italic', margin: 0, lineHeight: 1.5,
          }}>
            "{targetRole}" requires specific competencies mapped against your profile.
          </p>
        </div>
  );
};

export default TargetMatching;
