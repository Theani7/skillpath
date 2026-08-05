import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';

type Props = {
  title: string;
  body: string;
  confirmLabel: string;
  danger: boolean;
  onCancel: () => void;
  onConfirm: () => void;
};

const ConfirmDialog = ({ title, body, confirmLabel, danger, onCancel, onConfirm }: Props) => {
  const ref = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    ref.current?.focus();
  }, []);
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-title"
      onClick={onCancel}
      style={{
        position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.45)',
        backdropFilter: 'blur(4px)', WebkitBackdropFilter: 'blur(4px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 100, padding: '16px',
      }}
    >
      <motion.div
        initial={{ y: 20, scale: 0.95 }}
        animate={{ y: 0, scale: 1 }}
        exit={{ y: 20, scale: 0.95 }}
        onClick={(e) => e.stopPropagation()}
        className="card"
        style={{ padding: '24px', maxWidth: '420px', width: '100%' }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
          <h3 id="confirm-title" style={{ fontSize: 'var(--text-lg)', fontWeight: 'var(--font-bold)', color: 'var(--color-text)', margin: 0 }}>
            {title}
          </h3>
          <button
            type="button"
            onClick={onCancel}
            aria-label="Close"
            style={{
              width: '44px', height: '44px',
              borderRadius: 'var(--radius-md)', border: 'none', background: 'transparent',
              color: 'var(--color-text-muted)', cursor: 'pointer',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            <X size={16} />
          </button>
        </div>
        <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', margin: '0 0 20px', lineHeight: 1.5 }}>{body}</p>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
          <button
            ref={ref}
            type="button"
            onClick={onCancel}
            className="btn"
            style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', color: 'var(--color-text)' }}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="btn"
            style={{
              background: danger ? 'var(--color-error)' : 'var(--color-primary)',
              color: 'white', border: 'none',
            }}
          >
            {confirmLabel}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};
export { ConfirmDialog };
