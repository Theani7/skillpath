import { motion } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity } from 'lucide-react';
import { CardHeader } from './ui';

const ScoreChart = ({ chartData }) => (

          <motion.div
            initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.2 }}
            className="card"
            style={{ padding: '24px', marginBottom: '24px' }}
          >
            <CardHeader
              icon={Activity}
              title="Score Progression"
              subtitle="Your resume quality over time."
            />
            <div style={{ width: '100%', height: '220px' }}>
              <ResponsiveContainer>
                <AreaChart data={chartData} margin={{ top: 5, right: 12, bottom: 5, left: -10 }}>
                  <defs>
                    <linearGradient id="profileScoreGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="var(--color-primary)" stopOpacity={0.25} />
                      <stop offset="100%" stopColor="var(--color-primary)" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                  <XAxis
                    dataKey="date"
                    stroke="var(--color-text-muted)"
                    tick={{ fill: 'var(--color-text-muted)', fontSize: 11 }}
                    axisLine={false} tickLine={false}
                  />
                  <YAxis
                    stroke="var(--color-text-muted)"
                    domain={[0, 100]}
                    tick={{ fill: 'var(--color-text-muted)', fontSize: 11 }}
                    axisLine={false} tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      background: 'var(--color-surface)',
                      border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-md)',
                      boxShadow: 'var(--shadow-md)',
                      fontSize: '12px',
                    }}
                    labelStyle={{ color: 'var(--color-text)', fontWeight: 'var(--font-bold)' }}
                  />
                  <Area
                    type="monotone" dataKey="score"
                    stroke="var(--color-primary)" fill="url(#profileScoreGrad)"
                    strokeWidth={2.5}
                    activeDot={{ r: 5, fill: 'var(--color-primary)', stroke: 'white', strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>);

export default ScoreChart;
