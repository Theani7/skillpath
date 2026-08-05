import { TrendingUp } from 'lucide-react';

type Props = {
  feedbackMsgs: string[];
};

const FeedbackList = ({ feedbackMsgs }: Props) => {
  return (
    <div className="card" style={{ padding: '24px', marginBottom: '20px' }}>
      <h3 style={{
        display: 'flex', alignItems: 'center', gap: '8px',
        fontSize: '16px', fontWeight: 'var(--font-bold)',
        color: 'var(--color-text)', marginBottom: '16px',
      }}>
        <span style={{
          width: '32px', height: '32px', borderRadius: 'var(--radius-md)',
          background: 'var(--indigo-50)', color: 'var(--color-primary)',
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <TrendingUp size={16} />
        </span>
        Actionable Feedback
      </h3>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {feedbackMsgs.map((msg, i) => (
          <li key={i} style={{
            display: 'flex', alignItems: 'flex-start', gap: '10px',
            padding: '12px 14px', borderRadius: 'var(--radius-md)',
            background: 'var(--color-bg)',
            fontSize: '13px', color: 'var(--color-text)', lineHeight: 1.5,
          }}>
            <span style={{
              width: '6px', height: '6px', borderRadius: '50%',
              background: 'var(--color-primary)', marginTop: '7px', flexShrink: 0,
            }} />
            {msg}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FeedbackList;
