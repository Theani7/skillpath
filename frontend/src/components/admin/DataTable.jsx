import { Trash2 } from 'lucide-react';

const Row = ({ label, value }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '13px' }}>
    <span style={{ color: 'var(--color-text-muted)' }}>{label}</span>
    <span style={{ color: 'var(--color-text)', fontWeight: 'var(--font-semibold)' }}>{value}</span>
  </div>
);

const DataTable = (props) => {
  const { columns, rows, keyField, empty, onDelete, deleteLabel = 'Delete' } = props;
  return (
  <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
        <thead>
          <tr style={{ background: 'var(--color-bg)', borderBottom: '1px solid var(--color-border)' }}>
            {columns.map((c, i) => (
              <th key={i} style={{
                padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 'var(--font-bold)',
                color: 'var(--color-text-light)', textTransform: 'uppercase', letterSpacing: '0.06em',
                minWidth: c.nowrap ? 200 : undefined,
              }}>{c.label}</th>
            ))}
            <th style={{ width: '60px' }} aria-label="Actions"></th>
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr><td colSpan={columns.length + 1} style={{ padding: '40px 16px', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '14px' }}>{empty}</td></tr>
          ) : rows.map((row) => (
            <tr key={row[keyField]} style={{ borderTop: '1px solid var(--color-border)' }}>
              {columns.map((c, i) => (
                <td key={i} style={{
                  padding: '12px 16px', color: 'var(--color-text)',
                  maxWidth: c.nowrap ? 280 : undefined,
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: c.nowrap ? 'nowrap' : undefined,
                  fontFamily: c.mono ? 'ui-monospace, SFMono-Regular, monospace' : undefined,
                  fontSize: c.mono ? '12px' : '13px',
                }}>{c.render(row)}</td>
              ))}
              <td style={{ padding: '8px 12px', textAlign: 'right' }}>
                {onDelete && (
                  <button
                    type="button"
                    onClick={() => onDelete(row[keyField])}
                    aria-label={`${deleteLabel} ${row[keyField]}`}
                    style={{
                      width: '44px', height: '44px',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid transparent',
                      background: 'transparent',
                      color: 'var(--color-text-muted)', cursor: 'pointer',
                      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                      transition: 'background 150ms ease, color 150ms ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'var(--color-error-light)';
                      e.currentTarget.style.color = 'var(--color-error)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent';
                      e.currentTarget.style.color = 'var(--color-text-muted)';
                    }}
                  >
                    <Trash2 size={15} />
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
  );
};
export { Row, DataTable };
