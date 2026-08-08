import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import Analyzer from './Analyzer';
import api from '../services/api';

const navigate = vi.fn();
vi.mock('react-router-dom', () => ({ useNavigate: () => navigate }));
vi.mock('../services/api', () => ({ default: { get: vi.fn(), post: vi.fn() } }));

const mockApi = api as unknown as { get: ReturnType<typeof vi.fn>; post: ReturnType<typeof vi.fn> };

const pdf = () => new File(['%PDF-1.4 content'], 'cv.pdf', { type: 'application/pdf' });

const pickFile = async (file: File) => {
  const input = document.querySelector('input[type="file"]') as HTMLInputElement;
  await userEvent.upload(input, file);
};

const submit = async () => {
  const btn = await screen.findByRole('button', { name: /analy/i });
  await userEvent.click(btn);
};

describe('Analyzer', () => {
  beforeEach(() => {
    navigate.mockReset();
    mockApi.get.mockReset().mockResolvedValue({ data: { roles: [] } });
    mockApi.post.mockReset();
  });

  it('rejects a file that is neither PDF nor DOCX', async () => {
    render(<Analyzer />);
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    // userEvent.upload honours the input's accept filter, so a .txt never
    // reaches onChange. The component still has to reject anything that gets
    // past the picker (drag-and-drop, a renamed file), so drive change directly.
    const bad = new File(['x'], 'notes.txt', { type: 'text/plain' });
    Object.defineProperty(input, 'files', { value: [bad], configurable: true });
    fireEvent.change(input);
    expect(await screen.findByText(/valid PDF or DOCX/i)).toBeInTheDocument();
  });

  it('accepts a .docx dropped onto the drop zone', async () => {
    render(<Analyzer />);
    const docx = new File(['PK'], 'cv.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    Object.defineProperty(input, 'files', { value: [docx], configurable: true });
    fireEvent.change(input);
    expect(await screen.findByText(/cv\.docx/)).toBeInTheDocument();
  });

  it('uploads the file and the selected role, then navigates', async () => {
    mockApi.post.mockResolvedValue({ data: { status: 'success' } });
    render(<Analyzer />);
    await pickFile(pdf());
    await submit();

    await waitFor(() => expect(mockApi.post).toHaveBeenCalled());
    const [url, body] = mockApi.post.mock.calls[0];
    expect(url).toBe('/api/analyze');
    expect(body).toBeInstanceOf(FormData);
    expect((body as FormData).get('file')).toBeInstanceOf(File);
    expect((body as FormData).get('target_role')).toBeTruthy();
    await waitFor(() => expect(navigate).toHaveBeenCalledWith('/analysis', { replace: true }));
  });

  it('shows the server error and stays put when analysis fails', async () => {
    mockApi.post.mockRejectedValue({ response: { data: { detail: 'Only PDF and DOCX files are supported' } } });
    render(<Analyzer />);
    await pickFile(pdf());
    await submit();

    expect(await screen.findByText(/Only PDF and DOCX files are supported/)).toBeInTheDocument();
    expect(navigate).not.toHaveBeenCalled();
  });

  it('does not navigate when the response carries an error payload', async () => {
    // Regression: the result was ignored, so a failed analysis still routed to
    // /analysis where the user saw stale or empty results.
    mockApi.post.mockResolvedValue({ data: { error: 'Could not parse resume' } });
    render(<Analyzer />);
    await pickFile(pdf());
    await submit();

    expect(await screen.findByText(/Could not parse resume/)).toBeInTheDocument();
    expect(navigate).not.toHaveBeenCalled();
  });

  it('falls back to the built-in roles when /api/job-roles fails', async () => {
    mockApi.get.mockRejectedValue(new Error('boom'));
    render(<Analyzer />);
    // The page must still be usable rather than rendering an empty role list.
    await waitFor(() => expect(mockApi.get).toHaveBeenCalled());
    expect(screen.getByRole('combobox')).toBeInTheDocument();
    expect(screen.getAllByRole('option').length).toBeGreaterThan(0);
  });
});
