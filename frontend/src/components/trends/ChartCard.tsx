import { ICON_BG } from './chartColors';
import type { LucideIcon } from 'lucide-react';

type Props = {
  icon: React.ReactNode;
  iconColor?: keyof typeof ICON_BG;
  title: string;
  children: React.ReactNode;
  span?: number;
};

const ChartCard = ({ icon, iconColor = 'indigo', title, children, span = 1 }: Props) => {
  const colors = ICON_BG[iconColor] || ICON_BG.indigo;
  return (
    <div style={{
      padding: '20px', borderRadius: 'var(--radius-lg)',
      background: 'var(--color-surface)',
      border: '1px solid var(--color-border)',
      gridColumn: span > 1 ? `span ${span}` : undefined,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <div style={{
          width: '36px', height: '36px', borderRadius: 'var(--radius-md)',
          background: colors.bg, color: colors.fg,
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
        }}>
          {icon}
        </div>
        <h3 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--color-text)', margin: 0 }}>
          {title}
        </h3>
      </div>
      {children}
    </div>
  );
};

export default ChartCard;
