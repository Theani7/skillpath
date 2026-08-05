type Props = {
  targetRole: string;
};

const AnalyzingState = ({ targetRole }: Props) => {
  return (
    <>
      <div style={{
        width: '56px', height: '56px', borderRadius: '50%',
        background: 'var(--indigo-50)', color: 'var(--color-primary)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        margin: '0 auto 16px',
      }}>
        <span style={{
          width: '24px', height: '24px',
          border: '3px solid var(--indigo-200)',
          borderTopColor: 'var(--color-primary)',
          borderRadius: '50%',
          display: 'inline-block',
          animation: 'spin 0.8s linear infinite',
        }} />
      </div>
      <h3 style={{
        fontSize: 'var(--text-base)', fontWeight: 'var(--font-semibold)',
        color: 'var(--color-text)', marginBottom: '4px',
      }}>
        Analyzing your resume
      </h3>
      <p style={{
        fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)',
        margin: 0,
      }}>
        Parsing content, scoring skills, and matching against <strong>{targetRole}</strong>...
      </p>
    </>
  );
};

export default AnalyzingState;
