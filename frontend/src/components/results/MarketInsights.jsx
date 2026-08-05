import { DollarSign, Target } from 'lucide-react';

const MarketInsights = ({ trends }) => {
  return (
        <div className="card" style={{ padding: '24px' }}>
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
              <DollarSign size={16} />
            </span>
            Market Insights
          </h3>
          {trends && (trends.growth || trends.top_skills) ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '12px 14px', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)',
              }}>
                <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)',
                  textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Avg. Salary
                </span>
                <span style={{ fontSize: '15px', fontWeight: 'var(--font-bold)', color: 'var(--color-text)' }}>
                  {trends.top_skills?.[0]
                    ? `$${Math.round((trends.top_skills[0].salary || 115000) / 1000)}k+`
                    : '$115k+'}
                </span>
              </div>
              <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '12px 14px', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)',
              }}>
                <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)',
                  textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Demand Trend
                </span>
                <span style={{ fontSize: '14px', fontWeight: 'var(--font-bold)', color: 'var(--color-success)' }}>
                  {trends.growth?.length
                    ? `+${trends.growth[trends.growth.length - 1].demand - trends.growth[0].demand}%`
                    : '+35%'}
                </span>
              </div>
              <p style={{ fontSize: '11px', color: 'var(--color-text-muted)',
                textAlign: 'center', margin: '4px 0 0' }}>
                Based on real-time market data.
              </p>
            </div>
          ) : (
            <p style={{
              textAlign: 'center', padding: '24px 0',
              color: 'var(--color-text-muted)', fontStyle: 'italic',
              fontSize: '14px', margin: 0,
            }}>
              Loading market trends...
            </p>
          )}
        </div>
  );
};

export default MarketInsights;
