import { TrendingUp, DollarSign, BarChart3, Monitor } from 'lucide-react';
import { ICON_BG } from './trends/chartColors';
import type { MarketTrends } from '../types';
import StatCard from './trends/StatCard';
import DemandChart from './trends/DemandChart';
import SalaryChart from './trends/SalaryChart';
import WorkEnvChart from './trends/WorkEnvChart';
import RegionChart from './trends/RegionChart';

type Props = {
  trends: MarketTrends;
};

const TrendDashboard = ({ trends }: Props) => {
  if (!trends || (!trends.growth && !trends.top_skills)) return null;

  const growthRaw = (trends as Record<string, unknown>).growth;
  const growthData = Array.isArray(growthRaw) ? growthRaw as { year: string; demand: number }[] : [];
  const skillsData = Array.isArray(trends.top_skills) ? trends.top_skills : [];
  const remoteRaw = (trends as Record<string, unknown>).remote_vs_onsite;
  const remoteData = Array.isArray(remoteRaw) ? remoteRaw as { name: string; value: number }[] : [];
  const regionData = Array.isArray(trends.regional_distribution) ? trends.regional_distribution as { region: string; salary: number }[] : [];

  const growthRate = growthData.length >= 2
    ? Math.round(((growthData[growthData.length - 1].demand - growthData[0].demand) / growthData[0].demand) * 100)
    : 0;

  const avgSalary = skillsData.length > 0
    ? Math.round(skillsData.reduce((sum, s) => sum + s.salary, 0) / skillsData.length)
    : 0;

  const topSkill = skillsData.length > 0 ? skillsData.reduce((a, b) => a.salary > b.salary ? a : b) : null;

  const hybridPct = remoteData.find(r => r.name === 'Hybrid')?.value || 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px',
      }}>
        <StatCard
          icon={<TrendingUp size={18} />}
          label="Growth Rate"
          value={`+${growthRate}%`}
          subtext="5-year projection"
          color={ICON_BG.emerald}
        />
        <StatCard
          icon={<DollarSign size={18} />}
          label="Avg Salary"
          value={`$${(avgSalary / 1000).toFixed(0)}k`}
          subtext={`Top: ${topSkill?.skill || 'N/A'}`}
          color={ICON_BG.indigo}
        />
        <StatCard
          icon={<BarChart3 size={18} />}
          label="Top Skills"
          value={skillsData.length}
          subtext={`${topSkill?.skill} leads at $${topSkill ? (topSkill.salary / 1000).toFixed(0) : 0}k`}
          color={ICON_BG.amber}
        />
        <StatCard
          icon={<Monitor size={18} />}
          label="Hybrid Work"
          value={`${hybridPct}%`}
          subtext="Most common setup"
          color={ICON_BG.rose}
        />
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '16px',
      }}>
        {growthData.length > 0 && (
          <DemandChart growthData={growthData} growthRate={growthRate} />
        )}
        {skillsData.length > 0 && (
          <SalaryChart skillsData={skillsData} topSkill={topSkill} />
        )}
        {remoteData.length > 0 && (
          <WorkEnvChart remoteData={remoteData} />
        )}
        {regionData.length > 0 && (
          <RegionChart regionData={regionData} />
        )}
      </div>
    </div>
  );
};

export default TrendDashboard;
