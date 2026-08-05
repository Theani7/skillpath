import {
  Activity, Users, MessageSquareText, BookOpen, TrendingUp, Server, RefreshCw, BarChart3,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { Row } from './DataTable';
import { StatCard } from './StatCard';

const DashboardTab = ({ resumes, registeredUsers, feedback, courses, analytics, qualityMetrics, uploadsOverTime, skillPathGaps, roleDistribution, scrapeStatus, onTriggerScrape }) => (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '20px' }}>
              <StatCard icon={Activity} label="Resume Uploads" value={resumes.length} />
              <StatCard icon={Users} label="Registered Users" value={registeredUsers.length} accent="var(--color-secondary)" />
              <StatCard icon={MessageSquareText} label="Feedback Items" value={feedback.length} accent="var(--color-warning)" />
              <StatCard icon={BookOpen} label="Courses" value={courses.length} accent="var(--color-success)" />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              <div className="card" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 'var(--font-bold)', color: 'var(--color-text)', margin: '0 0 12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <TrendingUp size={16} color="var(--color-primary)" /> Market Insights
                </h3>
                <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: '0 0 6px' }}>Most sought-after role</p>
                <p style={{ fontSize: 'var(--text-base)', fontWeight: 'var(--font-semibold)', color: 'var(--color-text)', margin: 0 }}>
                  {analytics.most_sought_role || 'Insufficient data'}
                </p>
                <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: '16px 0 6px' }}>Most common missing skill</p>
                <p style={{ fontSize: 'var(--text-base)', fontWeight: 'var(--font-semibold)', color: 'var(--color-text)', margin: 0 }}>
                  {analytics.most_common_missing_skill || 'Insufficient data'}
                </p>
              </div>

              <div className="card" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 'var(--font-bold)', color: 'var(--color-text)', margin: '0 0 12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Server size={16} color="var(--color-primary)" /> Service Health
                </h3>
                {qualityMetrics ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <Row label="Total requests" value={qualityMetrics.total_requests} />
                    <Row label="Server errors" value={qualityMetrics.server_errors} />
                    <Row label="Avg latency" value={`${qualityMetrics.avg_latency_ms} ms`} />
                    <Row label="Error rate" value={`${qualityMetrics.parse_failure_rate_pct}%`} />
                  </div>
                ) : (
                  <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: 0 }}>No metrics available.</p>
                )}
                <button
                  type="button"
                  onClick={onTriggerScrape}
                  className="btn"
                  style={{
                    marginTop: '16px', width: '100%',
                    background: 'var(--color-surface)', border: '1px solid var(--color-border)',
                    color: 'var(--color-text)',
                  }}
                >
                  <RefreshCw size={14} style={{ marginRight: '6px' }} /> Simulate market shift
                </button>
                {scrapeStatus && (
                  <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '10px', textAlign: 'center' }}>{scrapeStatus}</p>
                )}
              </div>
            </div>

            {/* Charts Section */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px', marginTop: '20px' }}>
              {/* Uploads Over Time */}
              <div className="card" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--color-text)', margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Activity size={14} color="var(--color-primary)" /> Resume Uploads Over Time
                </h3>
                {uploadsOverTime.length > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={uploadsOverTime}>
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(v) => v?.slice(5) || v} />
                      <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                      <Tooltip />
                      <Line type="monotone" dataKey="count" stroke="var(--color-primary)" strokeWidth={2} dot={{ r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: 0 }}>No data yet.</p>
                )}
              </div>

              {/* Skill Gaps */}
              <div className="card" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--color-text)', margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BarChart3 size={14} color="var(--color-secondary)" /> Top Missing Skills
                </h3>
                {skillPathGaps.length > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={skillPathGaps} layout="vertical">
                      <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
                      <YAxis type="category" dataKey="skill" tick={{ fontSize: 11 }} width={100} />
                      <Tooltip />
                      <Bar dataKey="count" fill="var(--color-secondary)" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: 0 }}>No data yet.</p>
                )}
              </div>

              {/* Role Distribution */}
              <div className="card" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--color-text)', margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <TrendingUp size={14} color="var(--color-success)" /> Target Role Distribution
                </h3>
                {roleDistribution.length > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie data={roleDistribution} dataKey="count" nameKey="target_role" cx="50%" cy="50%" outerRadius={80} label={({ target_role, percent }) => `${target_role?.slice(0, 15) || ''} ${(percent * 100).toFixed(0)}%`} labelLine={false} style={{ fontSize: '11px' }}>
                        {roleDistribution.map((_, index) => (
                          <Cell key={index} fill={['#ff6b35', '#0a1628', '#22c55e', '#eab308', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6'][index % 8]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: 0 }}>No data yet.</p>
                )}
              </div>
            </div>
          </div>
);

export { DashboardTab };
