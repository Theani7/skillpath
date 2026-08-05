import { motion } from 'framer-motion';

const PageLoader = () => (
  <div
    role="status"
    aria-label="Loading"
    style={{
      minHeight: '60vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', gap: '14px',
      padding: '40px 16px',
    }}
  >
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      style={{
        width: '36px', height: '36px',
        borderRadius: '50%',
        border: '3px solid var(--navy-100)',
        borderTopColor: 'var(--color-primary)',
      }}
    />
    <p style={{
      fontSize: '13px', fontWeight: 'var(--font-semibold)',
      color: 'var(--color-text-muted)',
      textTransform: 'uppercase', letterSpacing: '0.08em',
      margin: 0,
    }}>
      Loading...
    </p>
  </div>
);

export default PageLoader;
