import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';

const LogoutModal = ({ show, onClose, onConfirm }) => {
  return (
      <AnimatePresence>
        {show && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed', inset: 0, zIndex: 910,
              background: 'rgba(0,0,0,0.4)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px',
            }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              onClick={(e) => e.stopPropagation()}
              style={{
                background: 'var(--color-surface)', border: '1px solid var(--color-border)',
                borderRadius: '16px', width: '100%', maxWidth: '360px',
                boxShadow: '0 24px 64px rgba(0,0,0,0.2)', padding: '28px',
                display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center',
              }}
            >
              <div style={{
                width: 48, height: 48, borderRadius: 12,
                background: 'var(--color-error-light)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16,
              }}>
                <AlertTriangle size={22} color="var(--color-error)" />
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--color-text)', marginBottom: 6 }}>
                Log out?
              </h3>
              <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', marginBottom: 20, lineHeight: 1.5 }}>
                You'll need to sign in again to access your data.
              </p>
              <div style={{ display: 'flex', gap: 10, width: '100%' }}>
                <button
                  onClick={onClose}
                  style={{
                    flex: 1, padding: '10px 0', borderRadius: 10,
                    border: '1px solid var(--color-border)', background: 'var(--color-surface)',
                    color: 'var(--color-text)', fontWeight: 600, fontSize: '14px', cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={onConfirm}
                  style={{
                    flex: 1, padding: '10px 0', borderRadius: 10,
                    border: 'none', background: 'var(--color-error)',
                    color: 'white', fontWeight: 600, fontSize: '14px', cursor: 'pointer',
                  }}
                >
                  Log out
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
  );
};

export default LogoutModal;
