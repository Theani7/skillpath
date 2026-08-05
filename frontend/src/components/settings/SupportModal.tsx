import { motion, AnimatePresence } from 'framer-motion';

type SupportForm = {
  subject: string;
  message: string;
};

type SupportErrors = {
  subject?: string;
  message?: string;
};

type Props = {
  showContactSupport: boolean;
  onClose: (v: boolean) => void;
  supportForm: SupportForm;
  setSupportForm: (v: SupportForm) => void;
  supportErrors: SupportErrors;
  supportLoading: boolean;
  handleContactSupport: (e: React.FormEvent) => void;
};

const SupportModal = ({ showContactSupport, onClose, supportForm, setSupportForm, supportErrors, supportLoading, handleContactSupport }: Props) => (
  <AnimatePresence>
    {showContactSupport && (
      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
        onClick={() => onClose(false)}
        style={{
          position: 'fixed', inset: 0,
          background: 'rgba(15, 23, 42, 0.45)',
          backdropFilter: 'blur(4px)', WebkitBackdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          padding: '16px', zIndex: 50,
        }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.96 }}
          onClick={(e) => e.stopPropagation()}
          style={{
            background: 'var(--color-surface)', borderRadius: 'var(--radius-2xl)',
            boxShadow: '0 20px 50px rgba(15, 23, 42, 0.2)',
            maxWidth: '480px', width: '100%', padding: '28px',
          }}
        >
          <h3 style={{ fontSize: '18px', fontWeight: 'var(--font-bold)', color: 'var(--color-text)', margin: '0 0 16px' }}>
            Contact Support
          </h3>
          <form onSubmit={handleContactSupport} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label style={{ fontSize: '13px', fontWeight: 'var(--font-semibold)', color: 'var(--color-text)', display: 'block', marginBottom: '6px' }}>
                Subject
              </label>
              <input
                value={supportForm.subject}
                onChange={(e) => setSupportForm({ ...supportForm, subject: e.target.value })}
                placeholder="How can we help?"
                style={{
                  width: '100%', height: '40px', padding: '0 12px',
                  borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)',
                  background: 'var(--color-surface)', color: 'var(--color-text)', fontSize: '14px',
                  outline: 'none', boxSizing: 'border-box',
                }}
              />
              {supportErrors.subject && (
                <p style={{ fontSize: '12px', color: 'var(--color-error)', margin: '4px 0 0' }}>{supportErrors.subject}</p>
              )}
            </div>
            <div>
              <label style={{ fontSize: '13px', fontWeight: 'var(--font-semibold)', color: 'var(--color-text)', display: 'block', marginBottom: '6px' }}>
                Message
              </label>
              <textarea
                value={supportForm.message}
                onChange={(e) => setSupportForm({ ...supportForm, message: e.target.value })}
                placeholder="Describe your issue or question..."
                rows={4}
                style={{
                  width: '100%', padding: '10px 12px',
                  borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)',
                  background: 'var(--color-surface)', color: 'var(--color-text)', fontSize: '14px',
                  outline: 'none', resize: 'vertical', boxSizing: 'border-box',
                }}
              />
              {supportErrors.message && (
                <p style={{ fontSize: '12px', color: 'var(--color-error)', margin: '4px 0 0' }}>{supportErrors.message}</p>
              )}
            </div>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button
                type="button" onClick={() => onClose(false)}
                style={{
                  height: '38px', padding: '0 18px', borderRadius: 'var(--radius-md)',
                  background: 'transparent', border: '1px solid var(--color-border)',
                  color: 'var(--color-text-muted)', fontSize: '13px', fontWeight: 'var(--font-semibold)',
                  cursor: 'pointer',
                }}
              >
                Cancel
              </button>
              <button
                type="submit" disabled={supportLoading}
                style={{
                  height: '38px', padding: '0 18px', borderRadius: 'var(--radius-md)',
                  background: 'var(--color-primary)', color: 'white',
                  fontSize: '13px', fontWeight: 'var(--font-semibold)',
                  border: 'none', cursor: supportLoading ? 'not-allowed' : 'pointer',
                  opacity: supportLoading ? 0.7 : 1,
                }}
              >
                {supportLoading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
);

export default SupportModal;
