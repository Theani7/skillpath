import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import AIInterviewMode from './AiInterviewMode';
import api from '../../services/api';

vi.mock('../../services/api', () => ({ default: { post: vi.fn() } }));
const mockApi = api as unknown as { post: ReturnType<typeof vi.fn> };

const Q1 = 'Tell me about a system you designed end to end.';
const Q2 = 'How did you handle failure modes in that design?';

const start = async () => {
  render(<AIInterviewMode selectedRole="Backend Development" />);
  await userEvent.click(screen.getByRole('button', { name: /start interview/i }));
};

describe('AIInterviewMode', () => {
  beforeEach(() => {
    mockApi.post.mockReset();
    mockApi.post.mockImplementation((url: string) => {
      if (url.includes('/start')) {
        return Promise.resolve({ data: { session_id: 's1', question: Q1, role: 'Backend Development' } });
      }
      if (url.includes('/answer')) {
        return Promise.resolve({ data: { feedback: 'Good structure.', next_question: Q2, question_number: 2 } });
      }
      return Promise.resolve({ data: {} });
    });
  });

  it('shows the first question immediately after starting', async () => {
    // Regression: the first question was stored in state but never rendered.
    // It only appeared after the user submitted an answer, so people were
    // answering a question they had never been shown.
    await start();
    expect(await screen.findByText(Q1)).toBeInTheDocument();
  });

  it('shows the question before the user has typed anything', async () => {
    await start();
    await screen.findByText(Q1);
    // The answer box must still be empty - proving the question is visible
    // without any interaction.
    expect(screen.getByPlaceholderText(/type your answer/i)).toHaveValue('');
  });

  it('does not duplicate the question after answering', async () => {
    await start();
    await screen.findByText(Q1);

    await userEvent.type(screen.getByPlaceholderText(/type your answer/i), 'I built a queue-backed pipeline.');
    await userEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => expect(screen.getAllByText(Q1)).toHaveLength(1));
  });

  it('renders the follow-up question after answering', async () => {
    await start();
    await screen.findByText(Q1);

    await userEvent.type(screen.getByPlaceholderText(/type your answer/i), 'I used retries and a DLQ.');
    await userEvent.click(screen.getByRole('button', { name: /send/i }));

    expect(await screen.findByText(Q2)).toBeInTheDocument();
    expect(await screen.findByText(/Good structure\./)).toBeInTheDocument();
  });

  it('keeps the answer in the box if submitting fails', async () => {
    await start();
    await screen.findByText(Q1);

    mockApi.post.mockRejectedValueOnce(new Error('network'));
    const box = screen.getByPlaceholderText(/type your answer/i);
    await userEvent.type(box, 'my answer');
    await userEvent.click(screen.getByRole('button', { name: /send/i }));

    // Losing the typed answer on a failed request means retyping it.
    await waitFor(() => expect(box).toHaveValue('my answer'));
  });

  it('does not lose the current question when submitting fails', async () => {
    await start();
    await screen.findByText(Q1);

    mockApi.post.mockRejectedValueOnce(new Error('network'));
    await userEvent.type(screen.getByPlaceholderText(/type your answer/i), 'my answer');
    await userEvent.click(screen.getByRole('button', { name: /send/i }));

    // The session must remain answerable rather than stranding the user.
    await waitFor(() => expect(screen.getAllByText(Q1).length).toBeGreaterThan(0));
  });
});
