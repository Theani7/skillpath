import { TrendingUp } from 'lucide-react';
import TrendDashboard from '../TrendDashboard';
import type { MarketTrends } from '../../types';

type Props = {
  trends: MarketTrends | null;
  targetRole: string;
};

const MarketTrendsCard = ({ trends, targetRole }: Props) => {
  return (
    <div className="card" style={{ padding: '28px', marginBottom: '20px' }}>
      <h3 style={{
        display: 'flex', alignItems: 'center', gap: '8px',
        fontSize: '16px', fontWeight: 'var(--font-bold)',
        color: 'var(--color-text)', marginBottom: '20px',
      }}>
        <span style={{
          width: '32px', height: '32px', borderRadius: 'var(--radius-md)',
          background: 'var(--emerald-50)', color: 'var(--color-success)',
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <TrendingUp size={16} />
        </span>
        Market Trends for {targetRole}
      </h3>
      {trends ? <TrendDashboard trends={trends} /> : (
        <p style={{ textAlign: 'center', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
          Loading market trends...
        </p>
      )}
    </div>
  );
};

export default MarketTrendsCard;
