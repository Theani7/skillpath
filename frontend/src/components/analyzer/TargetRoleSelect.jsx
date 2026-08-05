import { Briefcase } from 'lucide-react';

const TargetRoleSelect = ({ targetRoles, targetRole, onSelect }) => {
  return (
                    <div style={{ marginBottom: '24px' }}>
                      <label className="label" style={{
                        display: 'flex', alignItems: 'center', gap: '6px',
                      }}>
                        <Briefcase size={14} />
                        Target role
                      </label>
                      <select
                        value={targetRole}
                        onChange={(e) => onSelect(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '10px 14px',
                          border: '1px solid var(--color-border)',
                          borderRadius: 'var(--radius-lg)',
                          fontSize: 'var(--text-sm)',
                          color: 'var(--color-text)',
                          background: 'var(--color-surface)',
                          outline: 'none',
                          transition: 'border-color 150ms ease',
                          height: '44px',
                          cursor: 'pointer',
                          boxSizing: 'border-box',
                          appearance: 'none',
                          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")`,
                          backgroundRepeat: 'no-repeat',
                          backgroundPosition: 'right 12px center',
                          paddingRight: '40px',
                        }}
                        onFocus={(e) => e.target.style.borderColor = 'var(--color-primary)'}
                        onBlur={(e) => e.target.style.borderColor = 'var(--color-border)'}
                      >
                        {targetRoles.map((role) => (
                          <option key={role} value={role}>{role}</option>
                        ))}
                      </select>
                    </div>
  );
};

export default TargetRoleSelect;
