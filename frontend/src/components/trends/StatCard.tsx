type ColorPair = { bg: string; fg: string };

type Props = {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtext?: string;
  color: ColorPair;
};

const StatCard = ({ icon, label, value, subtext, color }: Props) => (
  <div style={{
    display: 'flex', alignItems: 'center', gap: '12px',
    padding: '14px 16px', borderRadius: 'var(--radius-md)',
    background: 'var(--color-bg)', border: '1px solid var(--color-border)',
  }}>
    <div style={{
      width: '40px', height: '40px', borderRadius: 'var(--radius-md)',
      background: color.bg, color: color.fg,
      display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
    }}>
      {icon}
    </div>
    <div>
      <p style={{ margin: 0, fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
        {label}
      </p>
      <p style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: 'var(--color-text)' }}>
        {value}
      </p>
      {subtext && (
        <p style={{ margin: 0, fontSize: '11px', color: 'var(--color-text-muted)' }}>
          {subtext}
        </p>
      )}
    </div>
  </div>
);

export default StatCard;
