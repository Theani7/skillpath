import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, MessageSquare, Sparkles, Target } from 'lucide-react';

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.5, delay: i * 0.06, ease: [0.22, 1, 0.36, 1] },
  }),
};

/* ---------------- Practice mode ---------------- */

function PracticeMode({ roles, selectedRole, setSelectedRole, autoDetected, questions, loading }) {
  const [expanded, setExpanded] = useState({});
  const toggle = (id) => setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  const expandedCount = Object.values(expanded).filter(Boolean).length;

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: '16px',
          padding: '20px 24px',
          marginBottom: '24px',
          display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-text-muted)' }}>
          <Target size={16} style={{ color: 'var(--color-secondary)' }} />
          <span style={{ fontSize: '13px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Role
          </span>
        </div>
        <select
          value={selectedRole}
          onChange={e => setSelectedRole(e.target.value)}
          style={{
            flex: 1, minWidth: '200px',
            padding: '10px 14px', borderRadius: '10px',
            border: `1px solid ${autoDetected ? 'var(--color-secondary)' : 'var(--color-border)'}`,
            background: autoDetected ? 'rgba(255, 107, 53, 0.04)' : 'var(--color-bg)',
            color: 'var(--color-text)', fontSize: '14px',
            fontWeight: 500, cursor: 'pointer', outline: 'none',
            transition: 'border-color 200ms',
          }}
        >
          {roles.map(r => <option key={r} value={r}>{r}</option>)}
        </select>
        {autoDetected && (
          <span style={{
            fontSize: '11px', fontWeight: 600, color: 'var(--color-secondary)',
            background: 'rgba(255, 107, 53, 0.08)', padding: '4px 10px',
            borderRadius: '6px', whiteSpace: 'nowrap',
          }}>
            Auto-detected
          </span>
        )}
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        style={{ display: 'flex', gap: '20px', marginBottom: '20px', padding: '0 4px' }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <MessageSquare size={14} style={{ color: 'var(--color-secondary)' }} />
          <span style={{ fontSize: '13px', color: 'var(--color-text-muted)', fontWeight: 500 }}>
            {questions.length} questions
          </span>
        </div>
        {expandedCount > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Sparkles size={14} style={{ color: 'var(--color-success)' }} />
            <span style={{ fontSize: '13px', color: 'var(--color-text-muted)', fontWeight: 500 }}>
              {expandedCount} revealed
            </span>
          </div>
        )}
      </motion.div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--color-text-light)', fontSize: '14px' }}>
          <div style={{
            width: '36px', height: '36px', border: '3px solid var(--color-border)',
            borderTopColor: 'var(--color-secondary)', borderRadius: '50%',
            animation: 'spin 0.8s linear infinite', margin: '0 auto 16px',
          }} />
          Loading questions...
        </div>
      ) : questions.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--color-text-light)', fontSize: '14px' }}>
          No questions available for this role.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {questions.map((q, i) => (
            <motion.div
              key={q.id}
              variants={fadeUp}
              initial="hidden"
              animate="visible"
              custom={i}
              style={{
                background: 'var(--color-surface)',
                border: `1px solid ${expanded[q.id] ? 'var(--color-secondary)' : 'var(--color-border)'}`,
                borderRadius: '14px', overflow: 'hidden',
                transition: 'border-color 200ms, box-shadow 200ms',
                boxShadow: expanded[q.id] ? '0 4px 20px rgba(255, 107, 53, 0.08)' : 'none',
              }}
            >
              <button
                onClick={() => toggle(q.id)}
                style={{
                  width: '100%', display: 'flex', alignItems: 'flex-start', gap: '14px', padding: '20px',
                  background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left',
                }}
              >
                <span style={{
                  flexShrink: 0, width: '32px', height: '32px', borderRadius: '10px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: expanded[q.id] ? 'var(--color-secondary)' : 'var(--color-bg)',
                  color: expanded[q.id] ? 'white' : 'var(--color-text-muted)',
                  fontSize: '13px', fontWeight: 700, transition: 'background 200ms, color 200ms',
                }}>
                  {i + 1}
                </span>
                <span style={{ flex: 1, fontWeight: 500, fontSize: '15px', color: 'var(--color-text)', lineHeight: 1.6, paddingTop: '4px' }}>
                  {q.question}
                </span>
                <span style={{
                  flexShrink: 0, width: '28px', height: '28px', borderRadius: '8px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: expanded[q.id] ? 'rgba(255, 107, 53, 0.1)' : 'var(--color-bg)',
                  color: expanded[q.id] ? 'var(--color-secondary)' : 'var(--color-text-light)',
                  transition: 'all 200ms', marginTop: '4px',
                }}>
                  {expanded[q.id] ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </span>
              </button>

              <AnimatePresence>
                {expanded[q.id] && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
                    style={{ overflow: 'hidden' }}
                  >
                    <div style={{ padding: '0 20px 20px', paddingLeft: 'calc(20px + 32px + 14px)' }}>
                      <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '16px' }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', padding: '4px 10px', borderRadius: '6px', background: 'rgba(255, 107, 53, 0.08)', marginBottom: '12px' }}>
                          <Sparkles size={11} style={{ color: 'var(--color-secondary)' }} />
                          <span style={{ fontWeight: 700, fontSize: '10px', color: 'var(--color-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Model Answer</span>
                        </div>
                        <p style={{ margin: 0, fontSize: '14px', lineHeight: 1.7, color: 'var(--color-text-muted)' }}>{q.answer}</p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      )}
    </>
  );
}

export default PracticeMode;
