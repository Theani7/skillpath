type Props = {
  targetRole: string;
};

const TitleBlock = ({ targetRole }: Props) => {
  return (
    <div style={{ textAlign: 'center', marginBottom: '32px' }}>
      <h1 style={{
        fontSize: 'clamp(28px, 4vw, 36px)',
        fontWeight: 'var(--font-extrabold)',
        letterSpacing: 'var(--tracking-tight)',
        color: 'var(--color-text)',
        marginBottom: '8px',
      }}>
        Your Career Analysis
      </h1>
      <p style={{
        fontSize: '15px',
        color: 'var(--color-text-muted)',
        margin: 0,
      }}>
        Here's how your resume stacks up for{' '}
        <strong style={{ color: 'var(--color-text)' }}>{targetRole || 'your target role'}</strong>
      </p>
    </div>
  );
};

export default TitleBlock;
