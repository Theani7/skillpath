import { Check, CheckCircle } from 'lucide-react';

type Props = {
  matchedSkills: string[];
};

const MatchedSkills = ({ matchedSkills }: Props) => {
  return (
    <div className="card" style={{ padding: '24px' }}>
      <h3 style={{
        display: 'flex', alignItems: 'center', gap: '8px',
        fontSize: '15px', fontWeight: 'var(--font-bold)',
        color: 'var(--color-success)', marginBottom: '16px',
      }}>
        <CheckCircle size={16} />
        Matched Skills ({matchedSkills.length})
      </h3>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
        {matchedSkills.length > 0 ? (
          matchedSkills.slice(0, 30).map((skill, i) => (
            <span key={i} style={{
              display: 'inline-flex', alignItems: 'center', gap: '4px',
              padding: '5px 10px', borderRadius: 'var(--radius-md)',
              background: 'var(--emerald-50)', color: 'var(--color-success)',
              fontSize: '12px', fontWeight: 'var(--font-semibold)',
              border: '1px solid #A7F3D0',
            }}>
              <Check size={11} /> {skill}
            </span>
          ))
        ) : (
          <span style={{ color: 'var(--color-text-muted)', fontStyle: 'italic', fontSize: '14px' }}>
            No skills identified yet.
          </span>
        )}
      </div>
    </div>
  );
};

export default MatchedSkills;
