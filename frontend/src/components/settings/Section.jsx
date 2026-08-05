import { motion } from 'framer-motion';

const Section = (props) => {
  const { icon: Icon, title, description, children, action, accent = 'indigo' } = props;
  const colors = {
    indigo: { bg: 'var(--indigo-50)', fg: 'var(--color-primary)' },
    emerald: { bg: 'var(--emerald-50)', fg: 'var(--color-success)' },
    amber: { bg: '#FEF3C7', fg: '#D97706' },
    error: { bg: 'var(--color-error-light)', fg: 'var(--color-error)' },
  }[accent];
  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
      className="card"
      style={{ padding: '24px' }}
    >
      <header style={{
        display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
        gap: '12px', marginBottom: '20px', flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px', height: '40px', borderRadius: 'var(--radius-md)',
            background: colors.bg, color: colors.fg,
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
          }}>
            <Icon size={18} />
          </div>
          <div>
            <h2 style={{ fontSize: '16px', fontWeight: 'var(--font-bold)', color: 'var(--color-text)', margin: 0 }}>
              {title}
            </h2>
            {description && (
              <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', margin: '2px 0 0' }}>
                {description}
              </p>
            )}
          </div>
        </div>
        {action}
      </header>
      {children}
    </motion.section>
  );
};

export default Section;
