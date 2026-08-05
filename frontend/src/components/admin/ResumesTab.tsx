import type { ReactNode } from 'react';
import type { AdminUserRow } from '../../types';
import { DataTable } from './DataTable';

type Props = {
  rows: AdminUserRow[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (updater: (prev: number) => number) => void;
  onView: (id: number) => void;
  onDelete: (id: number) => void;
};

const ResumesTab = ({ rows, total, page, pageSize, onPageChange, onView, onDelete }: Props) => (
  <div>
    <DataTable
      columns={[
        { label: 'Name', render: (r) => r.Name as ReactNode },
        { label: 'Email', render: (r) => r.Email_ID as ReactNode, mono: true },
        { label: 'Role', render: (r) => (r.target_role || r.Predicted_Field) as ReactNode },
        { label: 'Score', render: (r) => r.resume_score as ReactNode },
        { label: 'When', render: (r) => r.Timestamp as ReactNode },
        {
          label: '',
          render: (r) => {
            const item = r as unknown as AdminUserRow;
            return (
              <button type="button" onClick={() => onView(item.ID)} style={{ padding: '4px 10px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: 'var(--color-text)', fontSize: '12px', cursor: 'pointer' }}>
                View
              </button>
            );
          },
        },
      ]}
      rows={rows as unknown as Record<string, unknown>[]}
      keyField="ID"
      empty="No resume analyses yet."
      onDelete={onDelete}
      deleteLabel="Delete log"
    />
    {total > pageSize && (
      <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '16px' }}>
        <button type="button" disabled={page === 0} onClick={() => onPageChange((p) => p - 1)} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: page === 0 ? 'var(--color-text-muted)' : 'var(--color-text)', cursor: page === 0 ? 'default' : 'pointer', fontSize: '13px' }}>Previous</button>
        <span style={{ padding: '6px 14px', fontSize: '13px', color: 'var(--color-text-muted)' }}>Page {page + 1} of {Math.ceil(total / pageSize)}</span>
        <button type="button" disabled={(page + 1) * pageSize >= total} onClick={() => onPageChange((p) => p + 1)} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: (page + 1) * pageSize >= total ? 'var(--color-text-muted)' : 'var(--color-text)', cursor: (page + 1) * pageSize >= total ? 'default' : 'pointer', fontSize: '13px' }}>Next</button>
      </div>
    )}
  </div>
);

export { ResumesTab };
