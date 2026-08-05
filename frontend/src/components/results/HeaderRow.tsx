import { ArrowLeft, Target } from 'lucide-react';

type Props = {
  onReset: () => void;
  targetRole: string;
};

const HeaderRow = ({ onReset, targetRole }: Props) => {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      marginBottom: '32px',
    }}>
      <button
        onClick={onReset}
        style={{
          display: 'inline-flex', alignItems: 'center', gap: '6px',
          background: 'transparent', border: 'none', cursor: 'pointer',
          color: 'var(--color-text-muted)', fontSize: '14px', fontWeight: 500,
          padding: '8px 12px', borderRadius: 'var(--radius-md)',
          transition: 'background 150ms ease, color 150ms ease',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'var(--color-bg)';
          e.currentTarget.style.color = 'var(--color-text)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'transparent';
          e.currentTarget.style.color = 'var(--color-text-muted)';
        }}
      >
        <ArrowLeft size={16} /> New Analysis
      </button>
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px',
        padding: '6px 12px', borderRadius: 'var(--radius-full)',
        fontSize: '12px', fontWeight: 'var(--font-semibold)',
        color: 'var(--color-primary)', background: 'var(--indigo-50)',
        border: '1px solid var(--indigo-100)',
      }}>
        <Target size={12} />
        Target: {targetRole || 'General'}
      </div>
    </div>
  );
};

export default HeaderRow;
