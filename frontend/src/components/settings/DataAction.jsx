const DataAction = (props) => {
  const { icon: Icon, iconColor, title, description, action } = props;
  const colors = {
    indigo: { bg: 'var(--indigo-50)', fg: 'var(--color-primary)' },
    amber: { bg: '#FEF3C7', fg: '#D97706' },
    error: { bg: 'var(--color-error-light)', fg: 'var(--color-error)' },
    emerald: { bg: 'var(--emerald-50)', fg: 'var(--color-success)' },
  }[iconColor] || { bg: 'var(--color-bg)', fg: 'var(--color-text-muted)' };
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap',
      padding: '14px 16px', borderRadius: 'var(--radius-lg)',
      background: 'var(--color-bg)', border: '1px solid var(--color-border)',
    }}>
      <div style={{
        width: '36px', height: '36px', borderRadius: 'var(--radius-md)',
        background: colors.bg, color: colors.fg,
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
      }}>
        <Icon size={15} />
      </div>
      <div style={{ flex: 1, minWidth: '200px' }}>
        <h4 style={{ fontSize: '13px', fontWeight: 'var(--font-bold)', color: 'var(--color-text)', margin: 0 }}>
          {title}
        </h4>
        <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: '2px 0 0', lineHeight: 1.4 }}>
          {description}
        </p>
      </div>
      {action}
    </div>
  );
};

export default DataAction;
