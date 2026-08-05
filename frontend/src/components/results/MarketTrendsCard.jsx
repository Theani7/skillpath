import { TrendingUp } from 'lucide-react';
import TrendDashboard from '../TrendDashboard';

const MarketTrendsCard = ({ trends, targetRole }) => {
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
          <TrendDashboard trends={trends} targetRole={targetRole} />
        </div>
  );
};

export default MarketTrendsCard;
