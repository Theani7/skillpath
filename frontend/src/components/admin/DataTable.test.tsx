import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { DataTable } from './DataTable';

const columns = [
  { label: 'Name', render: (r: Record<string, unknown>) => r.name as string },
  { label: 'Role', render: (r: Record<string, unknown>) => r.role as string },
];

describe('DataTable', () => {
  it('renders a row per record', () => {
    render(
      <DataTable
        columns={columns}
        rows={[
          { id: 1, name: 'Ada', role: 'admin' },
          { id: 2, name: 'Grace', role: 'user' },
        ]}
        keyField="id"
        empty="Nothing here."
      />,
    );
    expect(screen.getByText('Ada')).toBeInTheDocument();
    expect(screen.getByText('Grace')).toBeInTheDocument();
  });

  it('shows the empty message when there are no rows', () => {
    render(<DataTable columns={columns} rows={[]} keyField="id" empty="Nothing here." />);
    expect(screen.getByText('Nothing here.')).toBeInTheDocument();
  });

  it('passes the keyField value to onDelete, not the row index', async () => {
    // Regression: the delete handler must receive the record id. Passing an
    // index deleted the wrong record.
    const onDelete = vi.fn();
    render(
      <DataTable
        columns={columns}
        rows={[
          { id: 41, name: 'Ada', role: 'admin' },
          { id: 42, name: 'Grace', role: 'user' },
        ]}
        keyField="id"
        empty="Nothing here."
        onDelete={onDelete}
      />,
    );
    await userEvent.click(screen.getByRole('button', { name: /Delete 42/ }));
    expect(onDelete).toHaveBeenCalledWith(42);
  });

  it('never renders an undefined React key', () => {
    // Regression: the backend returns lowercase `id` because the Postgres
    // column is unquoted `ID`. Components using keyField="ID" produced
    // key={undefined} for every row, so React collapsed the list and logged
    // "two children with the same key". Fail loudly if that recurs.
    const warn = vi.spyOn(console, 'error').mockImplementation(() => {});
    render(
      <DataTable
        columns={columns}
        rows={[
          { id: 1, name: 'Ada', role: 'admin' },
          { id: 2, name: 'Grace', role: 'user' },
        ]}
        keyField="id"
        empty="Nothing here."
      />,
    );
    const keyWarnings = warn.mock.calls
      .map((c) => String(c[0]))
      .filter((m) => m.includes('same key') || m.includes('unique "key"'));
    expect(keyWarnings).toEqual([]);
    expect(screen.getAllByRole('row')).toHaveLength(3); // header + 2 data rows
    warn.mockRestore();
  });
});
