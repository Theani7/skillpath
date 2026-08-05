import { motion } from 'framer-motion';
import { CheckCircle, AlertTriangle } from 'lucide-react';

const Toast = ({ toast }) => (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            role="status"
            aria-live="polite"
            style={{
              position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)',
              background: toast.type === 'success' ? 'var(--color-success)' : 'var(--color-error)',
              color: 'white', padding: '12px 20px', borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-lg)', fontSize: '14px', fontWeight: 'var(--font-semibold)',
              zIndex: 50, display: 'flex', alignItems: 'center', gap: '8px',
            }}
          >
            {toast.type === 'success' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
            {toast.message}
          </motion.div>
);

export { Toast };
