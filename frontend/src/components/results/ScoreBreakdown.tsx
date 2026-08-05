import { Award } from 'lucide-react';
import badge from './badge';
import type { ScoreBreakdown as ScoreBreakdownType } from '../../types';

type Props = {
  scoreBreakdown: ScoreBreakdownType;
};

const ScoreBreakdownCard = ({ scoreBreakdown }: Props) => {
  return (
    <div className="card" style={{ padding: '28px', marginBottom: '20px' }}>
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
          <Award size={16} />
        </span>
        Technical Score Breakdown
      </h3>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
        gap: '12px',
      }}>
        {(Object.entries(scoreBreakdown) as [string, { score?: number; status: string }][]).map(([key, val]) => {
          const present = val.status === 'present';
          return (
            <div key={key} style={{
              textAlign: 'center', padding: '16px 12px',
              background: 'var(--color-bg)', borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--color-border)',
            }}>
              <div style={{
                fontSize: '24px', fontWeight: 'var(--font-extrabold)',
                color: 'var(--color-primary)', marginBottom: '4px',
              }}>
                {val.score ?? 0}
              </div>
              <div style={{
                fontSize: '10px', fontWeight: 'var(--font-semibold)',
                textTransform: 'uppercase', letterSpacing: '0.04em',
                color: 'var(--color-text-muted)', marginBottom: '10px',
              }}>
                {key.replace(/_/g, ' ')}
              </div>
              <span style={badge(present
                ? { bg: 'var(--emerald-50)', fg: 'var(--color-success)' }
                : { bg: 'var(--color-error-light)', fg: 'var(--color-error)' }
              )}>
                {present ? 'Optimal' : 'Missing'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ScoreBreakdownCard;
