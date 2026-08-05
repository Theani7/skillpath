import { useRef } from 'react';
import { ShieldCheck } from 'lucide-react';
import { OTP_LENGTH } from './otpUtils';

type OtpBoxesProps = {
  value: string[];
  onChange: (v: string[]) => void;
  disabled?: boolean;
};

export const OtpBoxes = ({ value, onChange, disabled }: OtpBoxesProps) => {
  const refs = useRef<(HTMLInputElement | null)[]>([]);

  const handleChange = (i: number, e: React.ChangeEvent<HTMLInputElement>) => {
    const digit = e.target.value.replace(/\D/g, '').slice(-1);
    const next = [...value];
    next[i] = digit;
    onChange(next);
    if (digit && i < OTP_LENGTH - 1) refs.current[i + 1]?.focus();
  };

  const handleKeyDown = (i: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !value[i] && i > 0) refs.current[i - 1]?.focus();
    if (e.key === 'ArrowLeft' && i > 0) refs.current[i - 1]?.focus();
    if (e.key === 'ArrowRight' && i < OTP_LENGTH - 1) refs.current[i + 1]?.focus();
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLDivElement>) => {
    const digits = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, OTP_LENGTH);
    if (!digits) return;
    e.preventDefault();
    onChange(Array.from({ length: OTP_LENGTH }, (_, i) => digits[i] || ''));
    refs.current[Math.min(digits.length, OTP_LENGTH - 1)]?.focus();
  };

  return (
    <div className="auth-otp-row" onPaste={handlePaste}>
      {Array.from({ length: OTP_LENGTH }, (_, i) => (
        <input
          key={i}
          ref={(el) => { refs.current[i] = el; }}
          type="text"
          inputMode="numeric"
          autoComplete={i === 0 ? 'one-time-code' : 'off'}
          maxLength={1}
          value={value[i]}
          disabled={disabled}
          onChange={(e) => handleChange(i, e)}
          onKeyDown={(e) => handleKeyDown(i, e)}
          className="auth-otp-input"
          aria-label={`Digit ${i + 1}`}
        />
      ))}
    </div>
  );
};

type DevOtpHintProps = {
  otp: string;
  label: string;
};

export const DevOtpHint = ({ otp, label }: DevOtpHintProps) => {
  if (!otp) return null;
  return (
    <div className="auth-modal-dev-hint" role="alert">
      <ShieldCheck size={14} />
      <span>
        {label}: <strong>{otp}</strong> <em>(dev only – SMTP not configured)</em>
      </span>
    </div>
  );
};
