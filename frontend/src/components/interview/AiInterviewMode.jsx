import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Sparkles, ArrowRight, CheckCircle, TrendingUp, Lightbulb, Award, RotateCcw, Quote, Send, User } from 'lucide-react';
import api from '../../services/api';
import { InterviewerAvatar, TypingDots, ScoreRing } from './';

function AIInterviewMode({ selectedRole }) {
  const [sessionId, setSessionId] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [userAnswer, setUserAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [starting, setStarting] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [questionNumber, setQuestionNumber] = useState(0);
  const [finished, setFinished] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, loading, feedback]);

  const startInterview = async () => {
    setStarting(true);
    try {
      const res = await api.post('/api/mock-interview/start', { role: selectedRole });
      setSessionId(res.data.session_id);
      setCurrentQuestion(res.data.question);
      setChatHistory([]);
      setFeedback('');
      setQuestionNumber(1);
      setFinished(false);
      setEvaluation(null);
    } catch (err) {
      console.error('Failed to start interview:', err);
    } finally {
      setStarting(false);
    }
  };

  const submitAnswer = async () => {
    if (!userAnswer.trim() || loading) return;
    setLoading(true);
    const currentQ = currentQuestion;
    const answer = userAnswer.trim();

    setChatHistory(prev => [...prev, { type: 'question', text: currentQ }, { type: 'answer', text: answer }]);
    setUserAnswer('');
    setFeedback('');

    try {
      const res = await api.post('/api/mock-interview/answer', {
        session_id: sessionId, question: currentQ, answer, role: selectedRole, chat_history: chatHistory,
      });
      setFeedback(res.data.feedback);
      setCurrentQuestion(res.data.next_question);
      setQuestionNumber(res.data.question_number);
    } catch (_err) {
      setFeedback('');
    } finally {
      setLoading(false);
    }
  };

  const finishInterview = async () => {
    setLoading(true);
    try {
      const res = await api.post(`/api/mock-interview/finish/${sessionId}`);
      setEvaluation(res.data);
      setFinished(true);
    } catch (err) {
      console.error('Failed to finish interview:', err);
    } finally {
      setLoading(false);
    }
  };

  /* Start screen */
  if (!sessionId) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'relative', overflow: 'hidden',
          background: 'var(--color-surface)', border: '1px solid var(--color-border)',
          borderRadius: '24px', padding: '48px 32px', textAlign: 'center',
          boxShadow: 'var(--shadow-card)',
        }}
      >
        <div style={{
          position: 'absolute', top: '-80px', right: '-80px', width: '240px', height: '240px',
          borderRadius: '50%', opacity: 0.06, pointerEvents: 'none',
          background: 'radial-gradient(circle, var(--color-secondary) 0%, transparent 70%)',
        }} />
        <div style={{
          width: '72px', height: '72px', borderRadius: '18px', margin: '0 auto 22px',
          background: 'linear-gradient(135deg, var(--color-primary), var(--color-primary-light))',
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 8px 24px rgba(10,22,40,0.2)',
        }}>
          <MessageSquare size={30} style={{ color: 'white' }} />
        </div>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 12px',
          borderRadius: 'var(--radius-full)', fontSize: 'var(--text-xs)', fontWeight: 'var(--font-semibold)',
          color: 'var(--color-secondary)', background: 'rgba(255, 107, 53, 0.08)',
          border: '1px solid rgba(255, 107, 53, 0.15)', marginBottom: '16px',
        }}>
          <Sparkles size={12} /> Live AI Interviewer
        </div>
        <h3 style={{
          fontSize: '24px', fontWeight: 800, color: 'var(--color-text)', marginBottom: '10px',
          letterSpacing: 'var(--tracking-tight)',
        }}>
          Ready when you are
        </h3>
        <p style={{
          fontSize: '14px', color: 'var(--color-text-muted)', lineHeight: 1.6,
          maxWidth: '420px', margin: '0 auto 28px',
        }}>
          You'll be interviewed for the <strong style={{ color: 'var(--color-text)' }}>{selectedRole}</strong> role.
          Answer out loud in your head, get coaching after each reply, and a final score at the end.
        </p>
        <button
          onClick={startInterview}
          disabled={starting}
          style={{
            display: 'inline-flex', alignItems: 'center', gap: '8px',
            padding: '14px 28px', borderRadius: '12px',
            background: 'var(--color-secondary)', color: 'white',
            fontSize: '15px', fontWeight: 700, border: 'none',
            cursor: starting ? 'not-allowed' : 'pointer', opacity: starting ? 0.7 : 1,
            boxShadow: 'var(--shadow-button)',
            transition: 'transform 200ms',
          }}
          onMouseDown={e => !starting && (e.currentTarget.style.transform = 'scale(0.97)')}
          onMouseUp={e => (e.currentTarget.style.transform = 'scale(1)')}
          onMouseLeave={e => (e.currentTarget.style.transform = 'scale(1)')}
        >
          {starting ? 'Connecting…' : <>Start Interview <ArrowRight size={16} /></>}
        </button>
      </motion.div>
    );
  }

  /* Evaluation screen */
  if (finished && evaluation) {
    const score = evaluation.score ?? 5;
    const cards = [
      { label: 'Strengths', items: evaluation.strengths || [], icon: TrendingUp, tone: 'success' },
      { label: 'Areas to improve', items: evaluation.weaknesses || [], icon: Lightbulb, tone: 'warning' },
      { label: 'Recommendations', items: evaluation.recommendations || [], icon: Award, tone: 'primary' },
    ];
    const toneColor = {
      success: { bg: 'var(--green-50)', bd: 'var(--green-200)', tx: 'var(--color-success)' },
      warning: { bg: 'var(--orange-50)', bd: 'var(--orange-200)', tx: 'var(--color-warning)' },
      primary: { bg: 'var(--navy-50)', bd: 'var(--navy-200)', tx: 'var(--color-primary)' },
    };
    return (
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{ textAlign: 'center' }}
      >
        <div style={{
          background: 'var(--color-surface)', border: '1px solid var(--color-border)',
          borderRadius: '24px', padding: '36px 28px', maxWidth: '640px', margin: '0 auto 20px',
          boxShadow: 'var(--shadow-card)',
        }}>
          <div style={{
            width: '56px', height: '56px', borderRadius: '16px', margin: '0 auto 18px',
            background: 'var(--green-50)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <CheckCircle size={28} style={{ color: 'var(--color-success)' }} />
          </div>
          <h3 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--color-text)', marginBottom: '4px', letterSpacing: 'var(--tracking-tight)' }}>
            Interview Complete
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', marginBottom: '24px' }}>
            Here's how you did as a {selectedRole}.
          </p>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '28px', flexWrap: 'wrap' }}>
            <ScoreRing score={score} />
            <div style={{ maxWidth: '320px', textAlign: 'left' }}>
              <p style={{ fontSize: '14px', lineHeight: 1.7, color: 'var(--color-text-muted)', margin: 0 }}>
                {evaluation.summary || 'Thank you for practicing. Keep going — every interview makes the next one easier.'}
              </p>
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px', maxWidth: '640px', margin: '0 auto 20px' }}>
          {cards.map(({ label, items, icon: Icon, tone }) => (
            <div key={label} style={{
              background: 'var(--color-surface)', border: '1px solid var(--color-border)',
              borderRadius: '16px', padding: '18px', textAlign: 'left',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <span style={{
                  width: '28px', height: '28px', borderRadius: '8px', display: 'inline-flex',
                  alignItems: 'center', justifyContent: 'center',
                  background: toneColor[tone].bg, color: toneColor[tone].tx,
                }}>
                  <Icon size={15} />
                </span>
                <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-text)' }}>{label}</span>
              </div>
              {items.length ? (
                <ul style={{ margin: 0, paddingLeft: '16px' }}>
                  {items.map((it, i) => (
                    <li key={i} style={{ fontSize: '13px', lineHeight: 1.6, color: 'var(--color-text-muted)', marginBottom: '4px' }}>{it}</li>
                  ))}
                </ul>
              ) : (
                <p style={{ fontSize: '13px', color: 'var(--color-text-light)', margin: 0 }}>—</p>
              )}
            </div>
          ))}
        </div>

        <button
          onClick={startInterview}
          style={{
            display: 'inline-flex', alignItems: 'center', gap: '8px',
            padding: '12px 22px', borderRadius: '12px',
            background: 'var(--color-surface)', border: '1px solid var(--color-border)',
            color: 'var(--color-text)', fontSize: '14px', fontWeight: 600, cursor: 'pointer',
          }}
        >
          <RotateCcw size={14} /> Start New Interview
        </button>
      </motion.div>
    );
  }

  /* Live interview room */
  const progress = Math.min(questionNumber / 6, 1);

  return (
    <div className="mi-room" style={{
      display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 220px', gap: '20px', alignItems: 'start',
    }}>
      {/* Conversation column */}
      <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <div style={{
          flex: 1, overflowY: 'auto', padding: '20px',
          background: 'var(--color-surface)', borderRadius: '18px',
          border: '1px solid var(--color-border)', marginBottom: '16px', minHeight: '420px', maxHeight: '60vh',
          boxShadow: 'var(--shadow-card)',
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
            {chatHistory.map((msg, i) => (
              <div key={i}>
                {msg.type === 'question' ? (
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                    <InterviewerAvatar size={34} />
                    <div style={{ maxWidth: '82%' }}>
                      <div style={{
                        padding: '12px 16px', borderRadius: '4px 14px 14px 14px',
                        background: 'var(--color-bg)', color: 'var(--color-text)',
                        border: '1px solid var(--color-border)', fontSize: '14px', lineHeight: 1.6,
                      }}>{msg.text}</div>
                      <span style={{ fontSize: '11px', color: 'var(--color-text-light)', marginLeft: '4px', fontWeight: 600 }}>Interviewer</span>
                    </div>
                  </div>
                ) : (
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', flexDirection: 'row-reverse' }}>
                    <div style={{
                      width: '34px', height: '34px', borderRadius: '10px', flexShrink: 0,
                      background: 'var(--color-secondary)', color: 'white',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}><User size={18} /></div>
                    <div style={{ maxWidth: '82%' }}>
                      <div style={{
                        padding: '12px 16px', borderRadius: '14px 4px 14px 14px',
                        background: 'linear-gradient(135deg, var(--color-secondary), var(--color-secondary-dark))',
                        color: 'white', fontSize: '14px', lineHeight: 1.6,
                      }}>{msg.text}</div>
                      <span style={{ fontSize: '11px', color: 'var(--color-text-light)', marginRight: '4px', fontWeight: 600, display: 'block', textAlign: 'right' }}>You</span>
                    </div>
                  </div>
                )}
              </div>
            ))}

            {feedback && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                style={{
                  display: 'flex', gap: '12px', alignItems: 'flex-start', marginLeft: '46px',
                }}
              >
                <div style={{
                  flex: 1, padding: '12px 16px', borderRadius: '14px',
                  background: 'rgba(34, 197, 94, 0.06)', border: '1px dashed rgba(34, 197, 94, 0.3)',
                  fontSize: '13px', lineHeight: 1.65, color: 'var(--color-text-muted)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                    <Quote size={13} style={{ color: 'var(--color-success)' }} />
                    <span style={{ fontWeight: 700, fontSize: '11px', color: 'var(--color-success)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Coach's note</span>
                  </div>
                  {feedback}
                </div>
              </motion.div>
            )}

            {loading && (
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <InterviewerAvatar size={34} />
                <div style={{
                  padding: '14px 18px', borderRadius: '4px 14px 14px 14px',
                  background: 'var(--color-bg)', border: '1px solid var(--color-border)',
                }}>
                  <TypingDots />
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        </div>

        {/* Composer */}
        <div style={{
          display: 'flex', gap: '10px', padding: '16px', background: 'var(--color-surface)',
          borderRadius: '18px', border: '1px solid var(--color-border)', boxShadow: 'var(--shadow-card)',
        }}>
          <textarea
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitAnswer(); } }}
            placeholder="Type your answer…"
            rows={2}
            style={{
              flex: 1, padding: '12px', borderRadius: '12px',
              border: '1px solid var(--color-border)', background: 'var(--color-bg)',
              color: 'var(--color-text)', fontSize: '14px', resize: 'none', outline: 'none', fontFamily: 'inherit',
            }}
          />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button
              onClick={submitAnswer}
              disabled={!userAnswer.trim() || loading}
              style={{
                padding: '10px 18px', borderRadius: '12px', background: 'var(--color-secondary)', color: 'white',
                border: 'none', cursor: userAnswer.trim() && !loading ? 'pointer' : 'not-allowed',
                opacity: userAnswer.trim() && !loading ? 1 : 0.5,
                display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: 600,
              }}
            >
              <Send size={14} /> Send
            </button>
            <button
              onClick={finishInterview}
              disabled={loading}
              style={{
                padding: '8px 16px', borderRadius: '12px', background: 'transparent', color: 'var(--color-text-muted)',
                border: '1px solid var(--color-border)', cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '12px', fontWeight: 500,
              }}
            >
              End
            </button>
          </div>
        </div>
      </div>

      {/* Progress rail */}
      <div style={{
        background: 'var(--color-surface)', border: '1px solid var(--color-border)',
        borderRadius: '18px', padding: '20px',
        boxShadow: 'var(--shadow-card)',
      }} className="mi-rail">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <InterviewerAvatar size={32} />
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-text)' }}>Interviewer</div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>{selectedRole}</div>
          </div>
        </div>

        <div style={{
          height: '6px', borderRadius: 'var(--radius-full)', background: 'var(--color-border)', overflow: 'hidden', marginBottom: '8px',
        }}>
          <motion.div
            style={{ height: '100%', background: 'var(--color-secondary)', borderRadius: 'var(--radius-full)' }}
            initial={false}
            animate={{ width: `${progress * 100}%` }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          />
        </div>
        <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', fontWeight: 600, marginBottom: '20px' }}>
          Question {questionNumber} <span style={{ color: 'var(--color-text-light)' }}>· in progress</span>
        </div>

        <div style={{
          fontSize: '11px', color: 'var(--color-text-light)', lineHeight: 1.6,
          borderTop: '1px solid var(--color-border)', paddingTop: '14px',
        }}>
          Answer each question, then read your coach's note before the next one. End anytime for a score.
        </div>
      </div>
    </div>
  );
}

export default AIInterviewMode;
