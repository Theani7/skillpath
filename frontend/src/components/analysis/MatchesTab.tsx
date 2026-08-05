import { motion } from 'framer-motion';
import { Briefcase, Check } from 'lucide-react';
import { pill } from './analysisUtils';
import type { JobMatch } from '../../types';

type Props = {
  matches: JobMatch[];
  targetRole: string;
};

const MatchesTab = ({ matches, targetRole }: Props) => {
  if (!Array.isArray(matches) || matches.length === 0) {
    return (
      <div className="card analysis-empty">
        <Briefcase size={24} color="var(--color-text-light)" />
        <h3>No matches yet</h3>
        <p>Job matches will appear here once your resume is analyzed.</p>
      </div>
    );
  }

  return (
    <div className="card analysis-resources-card">
      <div className="analysis-card-head">
        <div className="analysis-card-icon" style={{ background: 'var(--indigo-50)', color: 'var(--color-primary)' }}>
          <Briefcase size={18} />
        </div>
        <div>
          <h3>Job matches</h3>
          <p className="analysis-card-sub">
            {targetRole ? `Roles matching your profile for ${targetRole}` : 'Roles matching your profile'}
          </p>
        </div>
        <span style={pill('var(--indigo-50)', 'var(--color-primary)')}>
          {matches.length} match{matches.length === 1 ? '' : 'es'}
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', padding: '0 20px 20px' }}>
        {matches.map((match, i) => (
          <motion.div
            key={match.job_id || i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            style={{
              padding: '16px', borderRadius: '12px',
              border: '1px solid var(--color-border)',
              background: 'var(--color-bg)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px', marginBottom: '10px' }}>
              <div>
                <h4 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--color-text)', margin: '0 0 4px' }}>
                  {match.title}
                </h4>
                <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: 0 }}>
                  {match.company} • {match.location}
                </p>
              </div>
              <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <div style={{
                  display: 'inline-flex', alignItems: 'center', gap: '4px',
                  padding: '4px 8px', borderRadius: '6px',
                  background: match.fit_score >= 80 ? 'var(--emerald-50)' : match.fit_score >= 60 ? '#FEF3C7' : 'var(--color-error-light)',
                  color: match.fit_score >= 80 ? 'var(--color-success)' : match.fit_score >= 60 ? '#D97706' : 'var(--color-error)',
                  fontSize: '12px', fontWeight: 700,
                }}>
                  {match.fit_score}% fit
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '10px' }}>
              <span style={pill('var(--color-bg)', 'var(--color-text-muted)')}>
                {match.workplace_type}
              </span>
              {match.salary_estimate > 0 && (
                <span style={pill('var(--emerald-50)', 'var(--color-success)')}>
                  ${(match.salary_estimate / 1000).toFixed(0)}k
                </span>
              )}
            </div>

            {match.why_matched && match.why_matched.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {match.why_matched.map((reason, j) => (
                  <div key={j} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--color-text-muted)' }}>
                    <Check size={10} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
                    {reason}
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export { MatchesTab };
