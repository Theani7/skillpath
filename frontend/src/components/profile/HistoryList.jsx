import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { FileText, Sparkles, ArrowRight, UploadCloud, Clock } from 'lucide-react';
import { CardHeader, PrimaryButton } from './ui';

const HistoryList = ({ history, getScoreColor, onSelect }) => (

        <motion.div
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.25 }}
          className="card"
          style={{ padding: '24px' }}
        >
          <CardHeader
            icon={Clock}
            title="Recent Analyses"
            subtitle="Click any row to view the full report."
          />

          {history.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 16px' }}>
              <div style={{
                width: '64px', height: '64px', borderRadius: '50%',
                background: 'var(--indigo-50)', color: 'var(--color-primary)',
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                marginBottom: '14px',
              }}>
                <Sparkles size={28} />
              </div>
              <h3 style={{ fontSize: '18px', fontWeight: 'var(--font-bold)', color: 'var(--color-text)', margin: '0 0 6px' }}>
                No analyses yet
              </h3>
              <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', margin: '0 0 20px' }}>
                Upload your first resume to get AI-powered insights.
              </p>
              <Link to="/app" style={{ textDecoration: 'none' }}>
                <PrimaryButton>
                  <UploadCloud size={14} /> Analyze Resume
                </PrimaryButton>
              </Link>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {[...history].reverse().slice(0, 6).map((item, i) => {
                const score = Math.round(item.resume_score || 0);
                const date = new Date(item.timestamp);
                return (
                  <motion.button
                    key={item.id || i}
                    type="button"
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.03 }}
                    onClick={() => item.analysis_data && onSelect(item.analysis_data)}
                    disabled={!item.analysis_data}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '16px',
                      padding: '14px 16px', borderRadius: 'var(--radius-lg)',
                      background: 'var(--color-bg)', border: '1px solid var(--color-border)',
                      cursor: item.analysis_data ? 'pointer' : 'default',
                      transition: 'all 150ms ease', width: '100%', textAlign: 'left',
                      fontFamily: 'inherit',
                    }}
                    onMouseEnter={(e) => {
                      if (!item.analysis_data) return;
                      e.currentTarget.style.borderColor = 'var(--indigo-200)';
                      e.currentTarget.style.background = 'var(--indigo-50)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = 'var(--color-border)';
                      e.currentTarget.style.background = 'var(--color-bg)';
                    }}
                  >
                    <div style={{
                      width: '42px', height: '42px', borderRadius: 'var(--radius-md)',
                      background: 'var(--color-surface)', border: '1px solid var(--color-border)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      flexShrink: 0,
                    }}>
                      <FileText size={18} color="var(--color-primary)" />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{
                        fontSize: '14px', fontWeight: 'var(--font-bold)',
                        color: 'var(--color-text)', marginBottom: '2px',
                        whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                      }}>
                        {item.target_role || item.predicted_field || 'Resume Analysis'}
                      </div>
                      <div style={{
                        fontSize: '12px', color: 'var(--color-text-muted)',
                        display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap',
                      }}>
                        <span>{date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                        {item.missing_skills?.length > 0 && (
                          <>
                            <span>&middot;</span>
                            <span>{item.missing_skills.length} skill gaps</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div style={{
                      fontSize: '20px', fontWeight: 'var(--font-extrabold)',
                      color: getScoreColor(score), flexShrink: 0, minWidth: '52px', textAlign: 'right',
                    }}>
                      {score}
                      <span style={{ fontSize: '12px', color: 'var(--color-text-muted)', fontWeight: 'var(--font-medium)' }}>%</span>
                    </div>
                    {item.analysis_data && (
                      <ArrowRight size={15} color="var(--color-text-muted)" style={{ flexShrink: 0 }} />
                    )}
                  </motion.button>
                );
              })}
            </div>
          )}
        </motion.div>);

export default HistoryList;
