import { XCircle } from 'lucide-react';

type Props = {
  missingSkills: string[];
};

const MissingSkills = ({ missingSkills }: Props) => {
  return (
    <div className="card" style={{ padding: '24px' }}>
      <h3 style={{
        display: 'flex', alignItems: 'center', gap: '8px',
        fontSize: '15px', fontWeight: 'var(--font-bold)',
        color: 'var(--color-error)', marginBottom: '16px',
      }}>
        <XCircle size={16} />
        Missing Competencies ({missingSkills.length})
      </h3>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
        {missingSkills.length > 0 ? (
          missingSkills.slice(0, 20).map((skill, i) => (
            <span key={i} style={{
              display: 'inline-flex', alignItems: 'center', gap: '4px',
              padding: '5px 10px', borderRadius: 'var(--radius-md)',
              background: 'var(--color-error-light)', color: 'var(--color-error)',
              fontSize: '12px', fontWeight: 'var(--font-semibold)',
              border: '1px solid #FECACA',
            }}>
              {skill}
            </span>
          ))
        ) : (
          <span style={{ color: 'var(--color-text-muted)', fontStyle: 'italic', fontSize: '14px' }}>
            All clear! No major gaps identified.
          </span>
        )}
      </div>
    </div>
  );
};

export default MissingSkills;
