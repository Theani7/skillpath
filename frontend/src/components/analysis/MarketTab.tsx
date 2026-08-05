import { TrendingUp } from 'lucide-react';
import TrendDashboard from '../TrendDashboard';
import type { MarketTrends } from '../../types';

type Props = {
  trends: MarketTrends | null;
  targetRole: string;
};

const MarketTab = ({ trends, targetRole }: Props) => {
  if (!trends || (!trends.growth && !trends.top_skills && !trends.remote_vs_onsite && !trends.regional_distribution)) {
    return (
      <div className="card analysis-empty">
        <TrendingUp size={24} color="var(--color-text-light)" />
        <h3>No market data</h3>
        <p>Market trends for {targetRole || 'this role'} are not available right now.</p>
      </div>
    );
  }
  return (
    <div className="card analysis-market-card">
      <div className="analysis-card-head">
        <div className="analysis-card-icon" style={{ background: 'var(--emerald-50)', color: 'var(--color-success)' }}>
          <TrendingUp size={18} />
        </div>
        <div>
          <h3>Market trends{targetRole ? ` for ${targetRole}` : ''}</h3>
          <p className="analysis-card-sub">Demand, pay, and work-environment data.</p>
        </div>
      </div>
      <TrendDashboard trends={trends} />
    </div>
  );
};

export { MarketTab };
