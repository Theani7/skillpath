import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { Monitor } from 'lucide-react';
import ChartCard from './ChartCard';
import CustomTooltip from './CustomTooltip';
import { CHART_COLORS } from './chartColors';

type WorkEnvPoint = { name: string; value: number };

type Props = {
  remoteData: WorkEnvPoint[];
};

const WorkEnvChart = ({ remoteData }: Props) => (
  <ChartCard
    icon={<Monitor size={18} />}
    iconColor="indigo"
    title="Work Environment"
  >
    <div style={{ width: '100%', height: '200px' }}>
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={remoteData}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            paddingAngle={3}
            dataKey="value"
            stroke="var(--color-surface)"
            strokeWidth={2}
          >
            {remoteData.map((_entry, index) => (
              <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
    <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap', marginTop: '8px' }}>
      {remoteData.map((entry, index) => (
        <div key={entry.name} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{
            width: '10px', height: '10px', borderRadius: '50%',
            background: CHART_COLORS[index % CHART_COLORS.length],
          }} />
          <span style={{ fontSize: '12px', color: 'var(--color-text-muted)', fontWeight: 500 }}>
            {entry.name} ({entry.value}%)
          </span>
        </div>
      ))}
    </div>
  </ChartCard>
);

export default WorkEnvChart;
