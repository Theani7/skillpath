import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';
import ChartCard from './ChartCard';
import CustomTooltip from './CustomTooltip';

const DemandChart = ({ growthData, growthRate }) => {
  return (
          <ChartCard
            icon={<TrendingUp size={18} />}
            iconColor="indigo"
            title="Job Demand Projection"
          >
            <div style={{ width: '100%', height: '220px' }}>
              <ResponsiveContainer>
                <AreaChart data={growthData} margin={{ top: 5, right: 10, bottom: 5, left: -10 }}>
                  <defs>
                    <linearGradient id="trendDemandGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#0a1628" stopOpacity={0.25} />
                      <stop offset="100%" stopColor="#0a1628" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                  <XAxis
                    dataKey="year"
                    stroke="var(--color-text-muted)"
                    tick={{ fill: 'var(--color-text-muted)', fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    stroke="var(--color-text-muted)"
                    tick={{ fill: 'var(--color-text-muted)', fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'var(--indigo-200)', strokeWidth: 1 }} />
                  <Area
                    type="monotone"
                    dataKey="demand"
                    stroke="#0a1628"
                    fillOpacity={1}
                    fill="url(#trendDemandGrad)"
                    strokeWidth={2.5}
                    activeDot={{ r: 5, fill: '#ff6b35', stroke: 'white', strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', padding: '0 4px' }}>
              <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                {growthData[0]?.year}: {growthData[0]?.demand} index
              </span>
              <span style={{ fontSize: '11px', color: 'var(--color-success)', fontWeight: 600 }}>
                +{growthRate}% projected
              </span>
            </div>
          </ChartCard>
  );
};

export default DemandChart;
