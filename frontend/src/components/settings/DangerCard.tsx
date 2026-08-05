import { ShieldAlert, LogOut, Trash2, ExternalLink } from 'lucide-react';
import { Section, DataAction } from './';

type Props = {
  onLogout: (v: boolean) => void;
  onDelete: (v: boolean) => void;
};

const DangerCard = ({ onLogout, onDelete }: Props) => (
  <Section
    icon={ShieldAlert}
    title="Danger Zone"
    description="Irreversible actions. Proceed with care."
    accent="error"
  >
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <DataAction
        icon={LogOut}
        iconColor="error"
        title="Log out"
        description="Sign out of this device. You can log back in anytime."
        action={
          <button
            onClick={() => onLogout(true)}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: '5px',
              height: '34px', padding: '0 14px', borderRadius: 'var(--radius-md)',
              background: 'transparent', border: '1px solid var(--color-border)',
              color: 'var(--color-error)', fontSize: '12px', fontWeight: 'var(--font-semibold)',
              cursor: 'pointer', flexShrink: 0,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--color-error-light)';
              e.currentTarget.style.borderColor = '#FECACA';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.borderColor = 'var(--color-border)';
            }}
          >
            <LogOut size={13} /> Log out
          </button>
        }
      />
      <DataAction
        icon={Trash2}
        iconColor="error"
        title="Delete account"
        description="Permanently remove your account, profile, preferences, and all data."
        action={
          <button
            onClick={() => onDelete(true)}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: '5px',
              height: '34px', padding: '0 14px', borderRadius: 'var(--radius-md)',
              background: 'var(--color-error)', color: 'white',
              fontSize: '12px', fontWeight: 'var(--font-semibold)',
              border: 'none', cursor: 'pointer', flexShrink: 0,
            }}
          >
            Delete account
          </button>
        }
      />
      <p style={{
        fontSize: '11px', color: 'var(--color-text-light)', margin: '4px 0 0',
        display: 'flex', alignItems: 'center', gap: '4px',
      }}>
        <ExternalLink size={10} />
        You will be logged out after deletion.
      </p>
    </div>
  </Section>
);

export default DangerCard;
