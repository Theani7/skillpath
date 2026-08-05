export const fieldStyle = (focus: boolean): React.CSSProperties => ({
  width: '100%', height: '44px', padding: '0 14px',
  border: `1px solid ${focus ? 'var(--color-primary)' : 'var(--color-border)'}`,
  borderRadius: 'var(--radius-lg)',
  fontSize: '14px', color: 'var(--color-text)', background: 'var(--color-surface)',
  outline: 'none', transition: 'border-color 150ms ease', fontFamily: 'inherit',
  boxSizing: 'border-box',
});

export const truncate = (text = '', n = 80) => {
  if (!text) return '';
  return text.length > n ? `${text.slice(0, n)}...` : text;
};
