const badge = (color) => ({
  display: 'inline-flex',
  alignItems: 'center',
  gap: '4px',
  padding: '4px 10px',
  borderRadius: 'var(--radius-full)',
  fontSize: '11px',
  fontWeight: 'var(--font-semibold)',
  textTransform: 'uppercase',
  letterSpacing: '0.04em',
  background: color.bg,
  color: color.fg,
});

export default badge;
