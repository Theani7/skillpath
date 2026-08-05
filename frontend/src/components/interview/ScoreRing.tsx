import { motion } from 'framer-motion';

type Props = {
  score: number;
};

function ScoreRing({ score }: Props) {
  const r = 52;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(10, score)) / 10;
  const color = score >= 8 ? 'var(--color-success)' : score >= 5 ? 'var(--color-warning)' : 'var(--color-error)';
  return (
    <div style={{ position: 'relative', width: '140px', height: '140px' }}>
      <svg width="140" height="140" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="70" cy="70" r={r} fill="none" stroke="var(--color-border)" strokeWidth="10" />
        <motion.circle
          cx="70" cy="70" r={r} fill="none" stroke={color} strokeWidth="10" strokeLinecap="round"
          strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: c * (1 - pct) }}
          transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] as const }}
        />
      </svg>
      <div style={{
        position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
      }}>
        <span style={{ fontSize: '34px', fontWeight: 800, color: 'var(--color-text)', lineHeight: 1 }}>{score}</span>
        <span style={{ fontSize: '12px', color: 'var(--color-text-muted)', fontWeight: 600 }}>/ 10</span>
      </div>
    </div>
  );
}

export default ScoreRing;
