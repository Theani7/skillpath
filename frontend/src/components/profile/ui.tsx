import { useState } from 'react';
import type { LucideIcon } from 'lucide-react';

const fieldStyle = (focus: boolean): React.CSSProperties => ({
  width: '100%', height: '42px', padding: '0 12px',
  border: `1px solid ${focus ? 'var(--color-primary)' : 'var(--color-border)'}`,
  borderRadius: 'var(--radius-md)',
  fontSize: '14px', color: 'var(--color-text)', background: 'var(--color-surface)',
  outline: 'none', transition: 'border-color 150ms ease', fontFamily: 'inherit',
  boxSizing: 'border-box',
});

const textareaStyle = (focus: boolean): React.CSSProperties => ({
  ...fieldStyle(focus),
  height: 'auto', minHeight: '84px', padding: '10px 12px', resize: 'vertical', lineHeight: 1.5,
});

const labelStyle: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: '6px',
  fontSize: '12px', fontWeight: 'var(--font-semibold)',
  color: 'var(--color-text-muted)', marginBottom: '6px',
};

type EditableFieldProps = {
  label: string;
  value: string | number;
  onChange: (v: string) => void;
  icon?: LucideIcon;
  type?: string;
  placeholder?: string;
  as?: 'input' | 'textarea';
  focusStyles?: React.CSSProperties;
  pattern?: string;
  maxLength?: number;
  error?: string;
};

export const EditableField = ({ label, value, onChange, icon: Icon, type = 'text', placeholder, as = 'input', focusStyles, pattern, maxLength, error }: EditableFieldProps) => {
  const [focus, setFocus] = useState(false);
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const v = e.target.value;
    if (maxLength && v.length > maxLength) return;
    if (pattern && v && !new RegExp(pattern).test(v)) return;
    onChange(v);
  };
  const borderColor = error ? 'var(--color-error)' : focus ? 'var(--color-primary)' : 'var(--color-border)';
  return (
    <div>
      <label style={labelStyle}>{Icon && <Icon size={12} />} {label}</label>
      {as === 'textarea' ? (
        <textarea
          value={value || ''}
          onChange={handleChange}
          onFocus={() => setFocus(true)}
          onBlur={() => setFocus(false)}
          placeholder={placeholder}
          rows={3}
          style={{ ...textareaStyle(focus), ...focusStyles, borderColor }}
        />
      ) : (
        <input
          type={type}
          value={value || ''}
          onChange={handleChange}
          onFocus={() => setFocus(true)}
          onBlur={() => setFocus(false)}
          placeholder={placeholder}
          style={{ ...fieldStyle(focus), ...focusStyles, borderColor }}
        />
      )}
      {error && (
        <div style={{ fontSize: '11px', color: 'var(--color-error)', marginTop: '4px' }}>{error}</div>
      )}
    </div>
  );
};

type CardHeaderProps = {
  icon: LucideIcon;
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
};

export const CardHeader = ({ icon: Icon, title, subtitle, action }: CardHeaderProps) => (
  <div style={{
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    gap: '12px', marginBottom: '20px',
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      <div style={{
        width: '36px', height: '36px', borderRadius: 'var(--radius-md)',
        background: 'var(--indigo-50)', color: 'var(--color-primary)',
        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <Icon size={16} />
      </div>
      <div>
        <h3 style={{ fontSize: '15px', fontWeight: 'var(--font-bold)', color: 'var(--color-text)', margin: 0 }}>
          {title}
        </h3>
        {subtitle && (
          <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', margin: '2px 0 0' }}>
            {subtitle}
          </p>
        )}
      </div>
    </div>
    {action}
  </div>
);

type ButtonProps = {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  disabled?: boolean;
};

export const PrimaryButton = ({ children, onClick, type = 'button', disabled = false }: ButtonProps) => (
  <button
    type={type} onClick={onClick} disabled={disabled}
    style={{
      display: 'inline-flex', alignItems: 'center', gap: '6px',
      height: '36px', padding: '0 16px', borderRadius: 'var(--radius-md)',
      background: disabled ? 'var(--color-border)' : 'var(--color-primary)',
      color: disabled ? 'var(--color-text-muted)' : 'white',
      fontWeight: 'var(--font-semibold)', fontSize: '13px',
      border: 'none', cursor: disabled ? 'not-allowed' : 'pointer',
      boxShadow: disabled ? 'none' : '0 2px 8px rgba(255, 107, 53, 0.2)',
      transition: 'opacity 150ms ease',
    }}
  >
    {children}
  </button>
);

export const SecondaryButton = ({ children, onClick, type = 'button' }: ButtonProps) => (
  <button
    type={type} onClick={onClick}
    style={{
      display: 'inline-flex', alignItems: 'center', gap: '6px',
      height: '36px', padding: '0 16px', borderRadius: 'var(--radius-md)',
      background: 'transparent', border: '1px solid var(--color-border)',
      color: 'var(--color-text-muted)', fontWeight: 'var(--font-semibold)', fontSize: '13px',
      cursor: 'pointer', transition: 'all 150ms ease',
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.background = 'var(--color-bg)';
      e.currentTarget.style.color = 'var(--color-text)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.background = 'transparent';
      e.currentTarget.style.color = 'var(--color-text-muted)';
    }}
  >
    {children}
  </button>
);

type DetailRowProps = {
  icon: LucideIcon;
  label: string;
  value: string;
  link?: boolean;
  multiline?: boolean;
};

export const DetailRow = ({ icon: Icon, label, value, link = false, multiline = false }: DetailRowProps) => (
  <div style={{
    display: 'flex', alignItems: multiline ? 'flex-start' : 'center', gap: '12px',
    padding: '10px 12px', borderRadius: 'var(--radius-md)',
    background: 'var(--color-bg)',
  }}>
    <div style={{
      width: '32px', height: '32px', borderRadius: 'var(--radius-md)',
      background: 'var(--color-surface)', color: 'var(--color-primary)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      flexShrink: 0, border: '1px solid var(--color-border)',
    }}>
      <Icon size={14} />
    </div>
    <div style={{ flex: 1, minWidth: 0 }}>
      <div style={{
        fontSize: '11px', fontWeight: 'var(--font-semibold)',
        color: 'var(--color-text-muted)', textTransform: 'uppercase',
        letterSpacing: '0.04em', marginBottom: '2px',
      }}>
        {label}
      </div>
      {link && value ? (
        <a
          href={value} target="_blank" rel="noopener noreferrer"
          style={{
            fontSize: '13px', fontWeight: 'var(--font-semibold)',
            color: 'var(--color-primary)', textDecoration: 'none',
            overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'block',
          }}
        >
          {value}
        </a>
      ) : (
        <div style={{
          fontSize: '13px', fontWeight: 'var(--font-semibold)',
          color: value && value !== '—' ? 'var(--color-text)' : 'var(--color-text-light)',
          wordBreak: 'break-word',
          ...(multiline ? { whiteSpace: 'pre-wrap', lineHeight: 1.5 } : {}),
        }}>
          {value || '—'}
        </div>
      )}
    </div>
  </div>
);
