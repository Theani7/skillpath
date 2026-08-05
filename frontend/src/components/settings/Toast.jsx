import { motion, AnimatePresence } from 'framer-motion';
import { Check } from 'lucide-react';

const Toast = (toast) => (
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 20, x: '-50%' }} animate={{ opacity: 1, y: 0, x: '-50%' }} exit={{ opacity: 0, y: 20, x: '-50%' }}
            style={{
              position: 'fixed', bottom: '24px', left: '50%',
              background: toast.type === 'error' ? 'var(--color-error)' : 'var(--color-success)',
              color: 'white', padding: '10px 18px', borderRadius: 'var(--radius-full)',
              fontSize: '13px', fontWeight: 'var(--font-semibold)',
              boxShadow: '0 10px 30px rgba(0,0,0,0.15)',
              display: 'inline-flex', alignItems: 'center', gap: '6px',
              zIndex: 100,
            }}
          >
            <Check size={14} />
            {toast.message}
          </motion.div>
        )}
      </AnimatePresence>
);

export default Toast;
