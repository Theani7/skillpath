import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Sparkles } from 'lucide-react';
import api from '../services/api';
import { PracticeMode, AiInterviewMode } from '../components/interview';

export default function MockInterview() {
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState('');
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [autoDetected, setAutoDetected] = useState(false);
  const [mode, setMode] = useState('practice');

  useEffect(() => {
    const init = async () => {
      try {
        const rolesRes = await api.get('/api/mock-interview');
        setRoles(rolesRes.data.roles);
        try {
          const analysisRes = await api.get('/api/user/latest-analysis');
          const targetRole = analysisRes.data?.target_role;
          if (targetRole && rolesRes.data.roles.includes(targetRole)) {
            setSelectedRole(targetRole); setAutoDetected(true);
          } else if (rolesRes.data.roles.length > 0) {
            setSelectedRole(rolesRes.data.roles[0]);
          }
        } catch {
          if (rolesRes.data.roles.length > 0) setSelectedRole(rolesRes.data.roles[0]);
        }
      } catch { /* ignore */ }
    };
    init();
  }, []);

  useEffect(() => {
    if (!selectedRole || mode !== 'practice') return;
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/api/mock-interview/${encodeURIComponent(selectedRole)}`);
        if (!cancelled) setQuestions(res.data.questions);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, [selectedRole, mode]);

  return (
    <div style={{ minHeight: '100%', background: 'var(--color-bg)', position: 'relative', overflow: 'hidden', paddingTop: '32px', paddingBottom: '48px' }}>
      <div style={{
        position: 'absolute', top: '-160px', right: '-160px', width: '500px', height: '500px',
        borderRadius: '50%', opacity: 0.06, pointerEvents: 'none',
        background: 'radial-gradient(circle, var(--color-primary) 0%, transparent 70%)',
      }} />
      <div style={{
        position: 'absolute', bottom: '-200px', left: '-200px', width: '500px', height: '500px',
        borderRadius: '50%', opacity: 0.05, pointerEvents: 'none',
        background: 'radial-gradient(circle, var(--color-secondary) 0%, transparent 70%)',
      }} />

      <div className="container" style={{ position: 'relative', zIndex: 1 }}>
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ maxWidth: '1000px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '36px' }}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 12px',
              borderRadius: 'var(--radius-full)', fontSize: 'var(--text-xs)', fontWeight: 'var(--font-semibold)',
              color: 'var(--color-secondary)', background: 'rgba(255, 107, 53, 0.08)',
              border: '1px solid rgba(255, 107, 53, 0.15)', marginBottom: '20px',
            }}>
              <BookOpen size={12} /> Interview Prep
            </div>
            <h1 style={{
              fontSize: 'clamp(28px, 4vw, 36px)', fontWeight: 'var(--font-extrabold)',
              letterSpacing: 'var(--tracking-tight)', color: 'var(--color-text)', marginBottom: '12px',
            }}>
              Mock Interview
            </h1>
            <p style={{
              fontSize: 'var(--text-base)', color: 'var(--color-text-muted)', lineHeight: 1.6,
              maxWidth: '500px', margin: '0 auto',
            }}>
              {mode === 'practice'
                ? 'Practice common interview questions for your target role. Expand each question to reveal a model answer.'
                : 'Practice with an AI interviewer that provides real-time feedback on your answers.'}
            </p>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.05 }}
            style={{
              display: 'flex', gap: '4px', marginBottom: '28px',
              padding: '4px', background: 'var(--color-surface)',
              borderRadius: '12px', border: '1px solid var(--color-border)',
              maxWidth: '300px', margin: '0 auto 28px',
            }}
          >
            {[
              { id: 'practice', label: 'Practice', icon: BookOpen },
              { id: 'ai', label: 'AI Interview', icon: Sparkles },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setMode(id)}
                style={{
                  flex: 1, padding: '10px 16px', borderRadius: '10px', border: 'none', fontSize: '13px', fontWeight: 600,
                  cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
                  background: mode === id ? 'var(--color-primary)' : 'transparent',
                  color: mode === id ? 'white' : 'var(--color-text-muted)', transition: 'all 200ms',
                }}
              >
                <Icon size={14} /> {label}
              </button>
            ))}
          </motion.div>

          {mode === 'practice' ? (
            <PracticeMode roles={roles} selectedRole={selectedRole} setSelectedRole={setSelectedRole}
              autoDetected={autoDetected} questions={questions} loading={loading} />
          ) : (
            <AiInterviewMode selectedRole={selectedRole} />
          )}
        </motion.div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%,100% { opacity: 0.4; } 50% { opacity: 1; } }
        @media (max-width: 860px) {
          .mi-room { grid-template-columns: 1fr !important; }
          .mi-rail { width: 100%; }
        }
      `}</style>
    </div>
  );
}
