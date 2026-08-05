import { DataTable } from './DataTable';

const UsersTab = ({ users, search, onSearchChange, onRoleChange, onStatusChange, onDelete }) => (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <input
                type="text"
                placeholder="Search by username or email..."
                value={search}
                onChange={(e) => onSearchChange(e.target.value)}
                style={{
                  width: '100%', maxWidth: '400px', height: '40px', padding: '0 14px',
                  border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)',
                  fontSize: '14px', color: 'var(--color-text)', background: 'var(--color-surface)',
                  outline: 'none',
                }}
              />
            </div>
            <DataTable
              columns={[
                { label: 'Username', render: (u) => u.username, mono: true },
                { label: 'Email', render: (u) => u.email, mono: true },
                {
                  label: 'Role',
                  render: (u) => (
                    <select
                      value={u.role}
                      onChange={(e) => onRoleChange(u.id, e.target.value)}
                      style={{
                        padding: '4px 8px', borderRadius: '6px', border: '1px solid var(--color-border)',
                        background: 'var(--color-surface)', color: 'var(--color-text)', fontSize: '13px',
                        cursor: 'pointer',
                      }}
                    >
                      <option value="user">User</option>
                      <option value="admin">Admin</option>
                    </select>
                  ),
                },
                {
                  label: 'Status',
                  render: (u) => (
                    <button
                      type="button"
                      onClick={() => onStatusChange(u.id, !u.is_active)}
                      style={{
                        padding: '4px 10px', borderRadius: '6px', border: 'none',
                        background: u.is_active ? 'var(--color-success)' : 'var(--color-error)',
                        color: 'white', fontSize: '12px', fontWeight: '600', cursor: 'pointer',
                      }}
                    >
                      {u.is_active ? 'Active' : 'Inactive'}
                    </button>
                  ),
                },
              ]}
              rows={users.filter((u) => {
                if (!search) return true;
                const q = search.toLowerCase();
                return u.username?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q);
              })}
              keyField="id"
              empty="No registered users yet."
              onDelete={onDelete}
              deleteLabel="Ban user"
            />
          </div>
);

export { UsersTab };
