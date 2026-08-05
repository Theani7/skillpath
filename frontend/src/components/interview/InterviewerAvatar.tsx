import { User } from 'lucide-react';

type Props = {
  size?: number;
};

function InterviewerAvatar({ size = 36 }: Props) {
  return (
    <div style={{
      width: size, height: size, borderRadius: '10px', flexShrink: 0,
      background: 'linear-gradient(135deg, var(--color-primary), var(--color-primary-light))',
      color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
      boxShadow: '0 2px 8px rgba(10,22,40,0.18)',
    }}>
      <User size={size * 0.42} />
    </div>
  );
}

export default InterviewerAvatar;
