import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion, type Variants } from 'framer-motion';
import {
  AlertTriangle, ExternalLink, Shield, Clock, ArrowLeft,
} from 'lucide-react';
import api from '../services/api';
import type { AnalysisResponse, ResumeData, RoadmapPhase } from '../types';

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: [0.22, 1, 0.36, 1] as const } },
};

type Props = {
  openAuthModal: (mode: 'login' | 'register') => void;
};

const SharedReport = ({ openAuthModal }: Props) => {
  const { token } = useParams<{ token: string }>();
  const [data, setData] = useState<{ analysis: AnalysisResponse } | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchShared = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await api.get(`/api/reports/share/${token}`);
        setData(res.data);
      } catch (err: unknown) {
        const status = (err as { response?: { status?: number } })?.response?.status;
        if (status === 404) {
          setError('This share link does not exist or has been removed.');
        } else if (status === 410) {
          setError('This share link has expired.');
        } else {
          setError('Could not load this shared report.');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchShared();
  }, [token]);

  const analysis = data?.analysis;
  const analysisData: ResumeData | undefined = analysis?.data;
  const targetRole = analysis?.target_role;
  const matchScore = analysis?.match_score;
  const resumeScore = analysis?.resume_score ?? 0;
  const missingSkills: string[] = Array.isArray(analysis?.missing_skill_names) ? analysis.missing_skill_names : [];
  const matchedSkills: string[] = analysisData?.skills || [];
  const feedback: string[] = Array.isArray(analysis?.feedback) ? analysis.feedback : [];
  const roadmap: RoadmapPhase[] | undefined = analysis?.roadmap;

  const scoreColor = resumeScore >= 80
    ? 'var(--color-success)' : resumeScore >= 50
      ? 'var(--color-warning)' : 'var(--color-error)';

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)' }}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          style={{ textAlign: 'center' }}
        >
          <div className="analysis-spinner" style={{ width: 32, height: 32, margin: '0 auto 16px' }} />
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>Loading shared report...</p>
        </motion.div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--color-bg)' }}>
        <motion.div
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          style={{ textAlign: 'center', maxWidth: 420, padding: '48px 32px' }}
        >
          <div style={{
            width: 64, height: 64, borderRadius: 16,
            background: 'var(--color-error)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 24px',
          }}>
            <AlertTriangle size={28} color="white" />
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: 12, color: 'var(--color-text)' }}>
            Report unavailable
          </h2>
          <p style={{ color: 'var(--color-text-muted)', marginBottom: 32, lineHeight: 1.6 }}>
            {error}
          </p>
          <button
            onClick={() => openAuthModal('login')}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              padding: '10px 24px', borderRadius: 10,
              background: 'var(--color-primary)', color: 'white',
              fontWeight: 600, fontSize: '0.9rem',
              textDecoration: 'none', border: 'none', cursor: 'pointer',
            }}
          >
            <ArrowLeft size={16} /> Sign in
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <header style={{
        position: 'sticky', top: 0, zIndex: 50,
        background: 'var(--color-surface)', borderBottom: '1px solid var(--color-border)',
        padding: '0 24px',
      }}>
        <div style={{
          maxWidth: 900, margin: '0 auto', height: 56,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <button
            onClick={() => openAuthModal('login')}
            style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-text-muted)', textDecoration: 'none', fontSize: '0.85rem', background: 'none', border: 'none', cursor: 'pointer' }}
          >
            <ArrowLeft size={14} /> Back to login
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
            <Shield size={13} /> Shared report
          </div>
        </div>
      </header>

      <main style={{ maxWidth: 900, margin: '0 auto', padding: '40px 24px 80px' }}>
        <motion.div variants={fadeUp} initial="hidden" animate="visible" style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--color-text)', marginBottom: 4 }}>
            Career Analysis
          </h1>
          {targetRole && (
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
              Target role: <strong style={{ color: 'var(--color-primary)' }}>{targetRole}</strong>
            </p>
          )}
        </motion.div>

        <motion.div variants={fadeUp} initial="hidden" animate="visible" style={{
          background: 'var(--color-surface)', borderRadius: 16,
          border: '1px solid var(--color-border)',
          padding: '32px', marginBottom: 32,
          display: 'flex', alignItems: 'center', gap: 32, flexWrap: 'wrap',
        }}>
          <div style={{ position: 'relative', width: 120, height: 120, flexShrink: 0 }}>
            <svg viewBox="0 0 120 120" style={{ width: 120, height: 120, transform: 'rotate(-90deg)' }}>
              <circle cx="60" cy="60" r="52" fill="none" stroke="var(--color-border)" strokeWidth="8" />
              <circle
                cx="60" cy="60" r="52"
                fill="none" stroke={scoreColor} strokeWidth="8"
                strokeDasharray={`${(resumeScore / 100) * 326.7} 326.7`}
                strokeLinecap="round"
              />
            </svg>
            <div style={{
              position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center',
            }}>
              <span style={{ fontSize: '1.6rem', fontWeight: 800, color: scoreColor }}>{Math.round(resumeScore)}</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>/ 100</span>
            </div>
          </div>
          <div style={{ flex: 1, minWidth: 200 }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--color-text)', marginBottom: 8 }}>
              {targetRole ? `Fit for ${targetRole}` : 'Resume quality'}
            </h3>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', lineHeight: 1.6 }}>
              {feedback[0] || 'Analysis complete.'}
            </p>
          </div>
          {matchScore != null && (
            <div style={{
              background: 'var(--navy-100)', borderRadius: 10,
              padding: '12px 20px', textAlign: 'center',
            }}>
              <div style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--color-primary)' }}>
                {Math.round(matchScore)}%
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>Role match</div>
            </div>
          )}
        </motion.div>

        {matchedSkills.length > 0 && (
          <motion.div variants={fadeUp} initial="hidden" animate="visible" style={{
            background: 'var(--color-surface)', borderRadius: 16,
            border: '1px solid var(--color-border)', padding: '24px', marginBottom: 32,
          }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--color-text)', marginBottom: 16 }}>
              Matched skills
            </h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {matchedSkills.map((s) => (
                <span key={s} style={{
                  padding: '4px 12px', borderRadius: 8,
                  background: 'var(--green-100)', color: 'var(--color-success)',
                  fontSize: '0.8rem', fontWeight: 600,
                }}>{s}</span>
              ))}
            </div>
          </motion.div>
        )}

        {missingSkills.length > 0 && (
          <motion.div variants={fadeUp} initial="hidden" animate="visible" style={{
            background: 'var(--color-surface)', borderRadius: 16,
            border: '1px solid var(--color-border)', padding: '24px', marginBottom: 32,
          }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--color-text)', marginBottom: 16 }}>
              Skills to develop
            </h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {missingSkills.map((s) => (
                <span key={s} style={{
                  padding: '4px 12px', borderRadius: 8,
                  background: 'var(--color-warning-light)', color: 'var(--color-warning)',
                  fontSize: '0.8rem', fontWeight: 600,
                }}>{s}</span>
              ))}
            </div>
          </motion.div>
        )}

        {roadmap && roadmap.length > 0 && (
          <motion.div variants={fadeUp} initial="hidden" animate="visible" style={{
            background: 'var(--color-surface)', borderRadius: 16,
            border: '1px solid var(--color-border)', padding: '24px', marginBottom: 32,
          }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--color-text)', marginBottom: 16 }}>
              Learning roadmap
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {roadmap.slice(0, 3).map((step, i) => (
                <div key={i} style={{
                  padding: '16px', borderRadius: 10,
                  background: 'var(--color-bg)', border: '1px solid var(--color-border)',
                }}>
                  <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--color-primary)', marginBottom: 4 }}>
                    Step {step.step || i + 1}
                  </div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-text)', marginBottom: 4 }}>
                    {step.title}
                  </div>
                  {step.skills && step.skills.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
                      {step.skills.map((s) => (
                        <span key={s} style={{
                          padding: '2px 8px', borderRadius: 6,
                          background: 'var(--navy-100)', color: 'var(--color-primary)',
                          fontSize: '0.75rem', fontWeight: 600,
                        }}>{s}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        )}

        <motion.div variants={fadeUp} initial="hidden" animate="visible" style={{ textAlign: 'center', marginTop: 48 }}>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', marginBottom: 16 }}>
            Want to see your own career analysis?
          </p>
          <button
            onClick={() => openAuthModal('register')}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              padding: '10px 28px', borderRadius: 10,
              background: 'var(--color-primary)',
              color: 'white', fontWeight: 700, fontSize: '0.9rem',
              textDecoration: 'none', border: 'none', cursor: 'pointer',
            }}
          >
            Create your account <ExternalLink size={14} />
          </button>
        </motion.div>
      </main>
    </div>
  );
};

export default SharedReport;
