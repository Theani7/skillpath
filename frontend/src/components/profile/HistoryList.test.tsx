import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import HistoryList from './HistoryList';
import type { HistoryItem } from '../../types';

const item = (over: Partial<HistoryItem> = {}): HistoryItem => ({
  id: 1,
  timestamp: '2026-01-01 10:00:00',
  predicted_field: 'Software Engineering',
  target_role: 'Backend',
  resume_score: 72,
  missing_skills: ['Go'],
  actual_skills: ['Python'],
  recommended_skills: ['Rust'],
  analysis_data: { resume_score: 72 } as HistoryItem['analysis_data'],
  ...over,
});

const setup = (history: HistoryItem[], onSelect = vi.fn()) => {
  render(
    <MemoryRouter>
      <HistoryList history={history} getScoreColor={() => 'green'} onSelect={onSelect} />
    </MemoryRouter>,
  );
  return onSelect;
};

describe('HistoryList', () => {
  it('prompts for a first upload when there is no history', () => {
    setup([]);
    expect(screen.getByText(/No analyses yet/i)).toBeInTheDocument();
  });

  it('shows newest first and caps the list at six', () => {
    const many = Array.from({ length: 10 }, (_, i) =>
      item({ id: i + 1, resume_score: i + 1, target_role: `Role ${i + 1}` }),
    );
    setup(many);
    expect(screen.getByText('Role 10')).toBeInTheDocument();
    expect(screen.queryByText('Role 1')).not.toBeInTheDocument();
    expect(screen.getAllByRole('button')).toHaveLength(6);
  });

  it('passes the analysis payload to onSelect', async () => {
    const onSelect = setup([item({ target_role: 'Backend' })]);
    await userEvent.click(screen.getByRole('button'));
    expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ resume_score: 72 }));
  });

  it('disables rows that have no stored analysis', async () => {
    // Older rows predate analysis_data. Clicking one must not fire onSelect
    // and route the user to an empty report.
    const onSelect = setup([item({ analysis_data: null })]);
    const row = screen.getByRole('button');
    expect(row).toBeDisabled();
    await userEvent.click(row);
    expect(onSelect).not.toHaveBeenCalled();
  });

  it('does not crash when the score is null', () => {
    setup([item({ resume_score: null as unknown as number })]);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('does not mutate the caller history array', () => {
    // The component reverses before slicing; doing that in place would
    // scramble the parent's state and the score chart alongside it.
    const history = [item({ id: 1 }), item({ id: 2 })];
    const order = history.map((h) => h.id);
    setup(history);
    expect(history.map((h) => h.id)).toEqual(order);
  });
});
