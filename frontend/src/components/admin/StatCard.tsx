import { ComponentType } from 'react';
import { motion } from 'framer-motion';
import { LucideProps } from 'lucide-react';

type Props = {
  icon: ComponentType<LucideProps>;
  label: string;
  value: string | number;
  accent?: string;
};

const StatCard = ({ icon: Icon, label, value, accent = 'var(--color-primary)' }: Props) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    className="card"
    style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '14px' }}
  >
    <div style={{
      width: '44px', height: '44px', borderRadius: 'var(--radius-lg)',
      background: 'var(--indigo-50)', color: accent,
      display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
    }}>
      <Icon size={20} />
    </div>
    <div style={{ minWidth: 0 }}>
      <p style={{ fontSize: 'var(--text-xs)', fontWeight: 'var(--font-semibold)', color: 'var(--color-text-light)', textTransform: 'uppercase', letterSpacing: '0.06em', margin: 0 }}>
        {label}
      </p>
      <p style={{ fontSize: 'var(--text-xl)', fontWeight: 'var(--font-bold)', color: 'var(--color-text)', margin: '2px 0 0', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {value}
      </p>
    </div>
  </motion.div>
);
export { StatCard };
