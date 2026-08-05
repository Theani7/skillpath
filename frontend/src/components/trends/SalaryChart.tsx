import { BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { DollarSign } from 'lucide-react';
import ChartCard from './ChartCard';
import CustomTooltip from './CustomTooltip';

type SkillPoint = { skill: string; salary: number; demand?: number };

type Props = {
  skillsData: SkillPoint[];
  topSkill: SkillPoint | null;
};

const SalaryChart = ({ skillsData, topSkill }: Props) => (
  <ChartCard
    icon={<DollarSign size={18} />}
    iconColor="emerald"
    title="Highest Paying Skills"
  >
    <div style={{ width: '100%', height: '220px' }}>
      <ResponsiveContainer>
        <BarChart data={skillsData} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
          <XAxis
            dataKey="skill"
            stroke="var(--color-text-muted)"
            tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            stroke="var(--color-text-muted)"
            tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `$${v / 1000}k`}
          />
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ fill: 'var(--color-bg)' }}
          />
          <Bar dataKey="salary" radius={[4, 4, 0, 0]} barSize={28}>
            {skillsData.map((entry, index) => (
              <Cell key={index} fill={index === 0 ? '#ff6b35' : '#0a1628'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
    <div style={{ display: 'flex', justifyContent: 'center', marginTop: '8px' }}>
      <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
        {topSkill?.skill} commands the highest salary
      </span>
    </div>
  </ChartCard>
);

export default SalaryChart;
