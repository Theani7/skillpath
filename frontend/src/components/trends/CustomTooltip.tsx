type Props = {
  active?: boolean;
  payload?: Array<{ value?: number; dataKey?: string }>;
  label?: string;
};

const CustomTooltip = ({ active, payload, label }: Props) => {
  if (!active || !payload?.length) return null;
  const value = payload[0].value;
  const formatted = payload[0].dataKey === 'demand'
    ? `Demand Index: ${value}`
    : `$${Number(value).toLocaleString()}`;
  return (
    <div style={{
      background: 'var(--color-surface)',
      border: '1px solid var(--color-border)',
      borderRadius: 'var(--radius-md)',
      padding: '8px 12px',
      boxShadow: 'var(--shadow-md)',
    }}>
      <p style={{ margin: 0, fontSize: '12px', fontWeight: 600, color: 'var(--color-text)' }}>
        {label}
      </p>
      <p style={{ margin: '2px 0 0', fontSize: '11px', fontWeight: 600, color: 'var(--color-primary)' }}>
        {formatted}
      </p>
    </div>
  );
};

export default CustomTooltip;
