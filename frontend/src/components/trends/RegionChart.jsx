import { BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { MapPin } from 'lucide-react';
import ChartCard from './ChartCard';
import CustomTooltip from './CustomTooltip';

const RegionChart = ({ regionData }) => {
  return (
          <ChartCard
            icon={<MapPin size={18} />}
            iconColor="amber"
            title="Top Market Hubs"
          >
            <div style={{ width: '100%', height: '220px' }}>
              <ResponsiveContainer>
                <BarChart
                  data={regionData}
                  layout="vertical"
                  margin={{ top: 5, right: 20, bottom: 5, left: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" horizontal={false} />
                  <XAxis
                    type="number"
                    stroke="var(--color-text-muted)"
                    tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(v) => `$${v / 1000}k`}
                  />
                  <YAxis
                    dataKey="region"
                    type="category"
                    stroke="var(--color-text-muted)"
                    tick={{ fill: 'var(--color-text)', fontSize: 11, fontWeight: 500 }}
                    axisLine={false}
                    tickLine={false}
                    width={90}
                  />
                  <Tooltip
                    content={<CustomTooltip />}
                    cursor={{ fill: 'var(--color-bg)' }}
                  />
                  <Bar dataKey="salary" radius={[0, 4, 4, 0]} barSize={18}>
                    {regionData.map((entry, index) => (
                      <Cell key={index} fill={index === 0 ? '#ff6b35' : '#0a1628'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '8px' }}>
              <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                Metropolitan areas pay {regionData.length > 1 ? Math.round(((regionData[1]?.salary - regionData[0]?.salary) / regionData[0]?.salary) * 100) : 0}% above average
              </span>
            </div>
          </ChartCard>
  );
};

export default RegionChart;
