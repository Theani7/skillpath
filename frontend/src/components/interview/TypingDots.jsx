function TypingDots() {
  return (
    <span style={{ display: 'inline-flex', gap: '4px', padding: '4px 2px' }}>
      {[0, 0.15, 0.3].map((d, i) => (
        <span key={i} style={{
          width: '6px', height: '6px', borderRadius: '50%',
          background: 'var(--color-text-light)', animation: `pulse 1s infinite ${d}s`,
        }} />
      ))}
    </span>
  );
}

export default TypingDots;
