type Props = {
  page: number;
  total: number;
  pageSize: number;
  onPageChange: (updater: (prev: number) => number) => void;
};

const Pager = ({ page, total, pageSize, onPageChange }: Props) => (
  <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '16px' }}>
    <button type="button" disabled={page === 0} onClick={() => onPageChange((p) => p - 1)} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: page === 0 ? 'var(--color-text-muted)' : 'var(--color-text)', cursor: page === 0 ? 'default' : 'pointer', fontSize: '13px' }}>Previous</button>
    <span style={{ padding: '6px 14px', fontSize: '13px', color: 'var(--color-text-muted)' }}>Page {page + 1} of {Math.ceil(total / pageSize)}</span>
    <button type="button" disabled={(page + 1) * pageSize >= total} onClick={() => onPageChange((p) => p + 1)} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid var(--color-border)', background: 'var(--color-surface)', color: (page + 1) * pageSize >= total ? 'var(--color-text-muted)' : 'var(--color-text)', cursor: (page + 1) * pageSize >= total ? 'default' : 'pointer', fontSize: '13px' }}>Next</button>
  </div>
);

export { Pager };
