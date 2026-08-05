import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

type Props = {
  score?: number;
};

const AnimatedScore = ({ score = 0 }: Props) => {
  const [displayScore, setDisplayScore] = useState(0);
  const numericScore = typeof score === 'number' ? score : parseInt(score as string, 10) || 0;

  useEffect(() => {
    let start = 0;
    const duration = 1500;
    const increment = numericScore / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= numericScore) {
        setDisplayScore(numericScore);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.floor(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [numericScore]);

  const size = 180;
  const strokeWidth = 10;
  const center = size / 2;
  const radius = center - strokeWidth;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (numericScore / 100) * circumference;

  const getColor = () => {
    if (numericScore >= 75) return 'var(--color-success)';
    if (numericScore >= 50) return 'var(--color-warning)';
    return 'var(--color-error)';
  };

  return (
    <div style={{
      position: 'relative', width: size, height: size, margin: '0 auto',
    }}>
      <svg
        width={size}
        height={size}
        style={{ transform: 'rotate(-90deg)' }}
      >
        <defs>
          <linearGradient id={`scoreGrad-${numericScore}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--color-primary)" />
            <stop offset="100%" stopColor="var(--color-secondary)" />
          </linearGradient>
        </defs>
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="var(--color-border)"
          strokeWidth={strokeWidth}
        />
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          fill="transparent"
          stroke={`url(#scoreGrad-${numericScore})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        />
      </svg>
      <div style={{
        position: 'absolute', inset: 0,
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
      }}>
        <motion.span
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          style={{
            fontSize: '3rem',
            fontWeight: 'var(--font-extrabold)',
            color: getColor(),
            lineHeight: 1,
            letterSpacing: 'var(--tracking-tight)',
            fontFamily: 'var(--font-display)',
          }}
        >
          {displayScore}
        </motion.span>
        <span style={{
          fontSize: '12px', fontWeight: 'var(--font-semibold)',
          color: 'var(--color-text-muted)', marginTop: '4px',
        }}>
          / 100
        </span>
      </div>
    </div>
  );
};

export default AnimatedScore;
