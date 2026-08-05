import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';

const ConfirmModal = (props) => {
  const { open, onClose, onConfirm, title, message, confirmText, danger = false, busy = false, children } = props;
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          onClick={onClose}
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
            role="dialog"
            aria-modal="true"
            aria-labelledby="confirm-modal-title"
            style={{
              background: 'var(--color-surface)', borderRadius: 'var(--radius-2xl)',
              boxShadow: '0 20px 50px rgba(15, 23, 42, 0.2)',
              maxWidth: '420px', width: '100%', padding: '28px', textAlign: 'center',
            }}
          >
            <div style={{
              width: '56px', height: '56px', borderRadius: '50%',
              background: danger ? 'var(--color-error-light)' : 'var(--indigo-50)',
              color: danger ? 'var(--color-error)' : 'var(--color-primary)',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px',
            }}>
              <AlertTriangle size={26} />
            </div>
            <h3 id="confirm-modal-title" style={{ fontSize: '18px', fontWeight: 'var(--font-bold)', color: 'var(--color-text)', margin: '0 0 8px' }}>
              {title}
            </h3>
            <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', lineHeight: 1.6, margin: '0 0 24px' }}>
              {message}
            </p>
            {children}
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                type="button" onClick={onClose} disabled={busy}
                style={{
                  flex: 1, height: '42px', padding: '0 20px', borderRadius: 'var(--radius-lg)',
                  background: 'transparent', border: '1px solid var(--color-border)',
                  color: 'var(--color-text-muted)', fontWeight: 'var(--font-semibold)', fontSize: '14px',
                  cursor: busy ? 'not-allowed' : 'pointer',
                }}
              >
                Cancel
              </button>
              <button
                type="button" onClick={onConfirm} disabled={busy}
                style={{
                  flex: 1, height: '42px', padding: '0 20px', borderRadius: 'var(--radius-lg)',
                  background: danger ? 'var(--color-error)' : 'var(--color-primary)',
                  color: 'white', fontWeight: 'var(--font-semibold)', fontSize: '14px',
                  border: 'none', cursor: busy ? 'not-allowed' : 'pointer',
                  opacity: busy ? 0.7 : 1,
                }}
              >
                {busy ? 'Working…' : confirmText}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ConfirmModal;
