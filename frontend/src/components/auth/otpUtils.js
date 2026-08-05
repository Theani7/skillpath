import { useState, useEffect, useCallback } from 'react';

export const OTP_LENGTH = 6;

export const getStrength = (pw) => {
  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  if (/[a-z]/.test(pw)) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^a-zA-Z0-9]/.test(pw)) score++;
  return Math.min(score, 5);
};

export const strengthLabel = ['', 'Weak', 'Weak', 'Fair', 'Good', 'Strong'];
export const strengthColor = ['', 'var(--color-error)', 'var(--color-error)', 'var(--color-warning)', 'var(--color-primary)', 'var(--color-success)'];

export const useCountdown = (seconds) => {
  const [countdown, setCountdown] = useState(seconds);
  const start = useCallback((s = seconds) => setCountdown(s), [seconds]);
  useEffect(() => {
    if (countdown <= 0) return undefined;
    const t = setInterval(() => setCountdown((c) => (c > 1 ? c - 1 : 0)), 1000);
    return () => clearInterval(t);
  }, [countdown]);
  return [countdown, start];
};
