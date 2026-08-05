import { Database, FileDown, Download, RefreshCw, Trash2 } from 'lucide-react';
import { Section, DataAction } from './';

type Props = {
  handleExportData: () => void;
  onClearHistory: (v: boolean) => void;
};

const DataPrivacyCard = ({ handleExportData, onClearHistory }: Props) => (
  <Section
    icon={Database}
    title="Data & Privacy"
    description="Export your data or clear your analysis history."
    accent="emerald"
  >
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <DataAction
        icon={FileDown}
        iconColor="indigo"
        title="Export all data"
        description="Download a JSON file with your profile, preferences, and analysis history."
        action={
          <button
            onClick={handleExportData}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: '5px',
              height: '34px', padding: '0 14px', borderRadius: 'var(--radius-md)',
              background: 'var(--color-surface)', border: '1px solid var(--color-border)',
              color: 'var(--color-text)', fontSize: '12px', fontWeight: 'var(--font-semibold)',
              cursor: 'pointer', flexShrink: 0,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--color-primary)';
              e.currentTarget.style.color = 'var(--color-primary)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--color-border)';
              e.currentTarget.style.color = 'var(--color-text)';
            }}
          >
            <Download size={13} /> Download
          </button>
        }
      />
      <DataAction
        icon={RefreshCw}
        iconColor="amber"
        title="Reset analysis history"
        description="Remove every past resume analysis. Your profile and preferences stay intact."
        action={
          <button
            onClick={() => onClearHistory(true)}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: '5px',
              height: '34px', padding: '0 14px', borderRadius: 'var(--radius-md)',
              background: 'transparent', border: '1px solid var(--color-border)',
              color: '#D97706', fontSize: '12px', fontWeight: 'var(--font-semibold)',
              cursor: 'pointer', flexShrink: 0,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#FEF3C7';
              e.currentTarget.style.borderColor = '#D97706';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.borderColor = 'var(--color-border)';
            }}
          >
            <Trash2 size={13} /> Clear
          </button>
        }
      />
    </div>
  </Section>
);

export default DataPrivacyCard;
