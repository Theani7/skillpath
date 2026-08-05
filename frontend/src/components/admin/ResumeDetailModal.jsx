import { motion } from 'framer-motion';
import { X } from 'lucide-react';
import { Row } from './DataTable';

const ResumeDetailModal = ({ detail, onClose }) => (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              zIndex: 50, padding: '20px',
            }}
            onClick={() => onClose()}
          >
            <motion.div
              initial={{ scale: 0.95, y: 10 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 10 }}
              onClick={(e) => e.stopPropagation()}
              style={{
                background: 'var(--color-surface)', borderRadius: 'var(--radius-xl)',
                padding: '28px', maxWidth: '600px', width: '100%', maxHeight: '80vh',
                overflow: 'auto', boxShadow: 'var(--shadow-xl)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--color-text)', margin: 0 }}>Resume Analysis Detail</h2>
                <button onClick={() => onClose()} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', padding: '4px' }}>
                  <X size={20} />
                </button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <Row label="Name" value={detail.Name} />
                <Row label="Email" value={detail.Email_ID} />
                <Row label="File" value={detail.pdf_name} />
                <Row label="Target Role" value={detail.target_role || detail.Predicted_Field} />
                <Row label="Score" value={detail.resume_score} />
                <Row label="Date" value={detail.Timestamp} />
                {detail.Actual_skills && (
                  <div>
                    <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: '0 0 6px' }}>Current Skills</p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {detail.Actual_skills.split(',').map((s, i) => (
                        <span key={i} style={{ padding: '3px 10px', borderRadius: '12px', background: 'var(--color-bg)', fontSize: '12px', color: 'var(--color-text)' }}>{s.trim()}</span>
                      ))}
                    </div>
                  </div>
                )}
                {detail.missing_skills && (
                  <div>
                    <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: '0 0 6px' }}>Missing Skills</p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {detail.missing_skills.split(',').map((s, i) => (
                        <span key={i} style={{ padding: '3px 10px', borderRadius: '12px', background: 'var(--color-error-light)', fontSize: '12px', color: 'var(--color-error)' }}>{s.trim()}</span>
                      ))}
                    </div>
                  </div>
                )}
                {detail.Recommended_skills && (
                  <div>
                    <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: '0 0 6px' }}>Recommended Skills</p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {detail.Recommended_skills.split(',').map((s, i) => (
                        <span key={i} style={{ padding: '3px 10px', borderRadius: '12px', background: 'var(--color-success-light)', fontSize: '12px', color: 'var(--color-success)' }}>{s.trim()}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
);

export { ResumeDetailModal };
