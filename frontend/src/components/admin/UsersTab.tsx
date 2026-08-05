import { type ChangeEvent, type ReactNode } from 'react';
import type { RegisteredUser } from '../../types';
import { DataTable } from './DataTable';

type Props = {
  users: RegisteredUser[];
  search: string;
  onSearchChange: (value: string) => void;
  onRoleChange: (userId: number, role: string) => void;
  onStatusChange: (userId: number, active: boolean) => void;
  onDelete: (id: number) => void;
};

const UsersTab = ({ users, search, onSearchChange, onRoleChange, onStatusChange, onDelete }: Props) => (
  <div>
    <div style={{ marginBottom: '16px' }}>
      <input
        type="text"
        placeholder="Search by username or email..."
        value={search}
        onChange={(e: ChangeEvent<HTMLInputElement>) => onSearchChange(e.target.value)}
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
        { label: 'Username', render: (u) => u.username as ReactNode, mono: true },
        { label: 'Email', render: (u) => u.email as ReactNode, mono: true },
        {
          label: 'Role',
          render: (u) => {
            const item = u as unknown as RegisteredUser;
            return (
              <select
                value={item.role}
                onChange={(e: ChangeEvent<HTMLSelectElement>) => onRoleChange(item.id, e.target.value)}
                style={{
                  padding: '4px 8px', borderRadius: '6px', border: '1px solid var(--color-border)',
                  background: 'var(--color-surface)', color: 'var(--color-text)', fontSize: '13px',
                  cursor: 'pointer',
                }}
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            );
          },
        },
        {
          label: 'Status',
          render: (u) => {
            const item = u as unknown as RegisteredUser;
            return (
              <button
                type="button"
                onClick={() => onStatusChange(item.id, !item.is_active)}
                style={{
                  padding: '4px 10px', borderRadius: '6px', border: 'none',
                  background: item.is_active ? 'var(--color-success)' : 'var(--color-error)',
                  color: 'white', fontSize: '12px', fontWeight: '600', cursor: 'pointer',
                }}
              >
                {item.is_active ? 'Active' : 'Inactive'}
              </button>
            );
          },
        },
      ]}
      rows={users.filter((u) => {
        if (!search) return true;
        const q = search.toLowerCase();
        return u.username?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q);
      }) as unknown as Record<string, unknown>[]}
      keyField="id"
      empty="No registered users yet."
      onDelete={onDelete}
      deleteLabel="Ban user"
    />
  </div>
);

export { UsersTab };
