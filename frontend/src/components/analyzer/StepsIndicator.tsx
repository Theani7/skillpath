const StepsIndicator = () => {
  return (
    <div style={{
      display: 'flex', justifyContent: 'center', gap: '8px', marginBottom: '24px',
    }}>
      {['Upload', 'Analyze', 'Get Roadmap'].map((step, i) => (
        <div key={step} style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          fontSize: 'var(--text-xs)', fontWeight: 'var(--font-semibold)',
          color: i === 0 ? 'var(--color-text)' : 'var(--color-text-light)',
        }}>
          <span style={{
            width: '20px', height: '20px', borderRadius: '50%',
            background: i === 0 ? 'var(--color-primary)' : 'var(--color-border)',
            color: 'white',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '11px', fontWeight: 700,
          }}>
            {i + 1}
          </span>
          <span>{step}</span>
          {i < 2 && (
            <span style={{
              width: '24px', height: '1px',
              background: 'var(--color-border)',
              marginLeft: '6px',
            }} />
          )}
        </div>
      ))}
    </div>
  );
};

export default StepsIndicator;
