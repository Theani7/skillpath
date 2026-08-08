import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider, useAuth } from './AuthContext';
import api from '../services/api';

vi.mock('../services/api', async () => {
  const actual = await vi.importActual<typeof import('../services/api')>('../services/api');
  return {
    ...actual,
    default: { get: vi.fn(), post: vi.fn() },
    registerLogoutHandler: actual.registerLogoutHandler,
  };
});

const mockApi = api as unknown as { get: ReturnType<typeof vi.fn>; post: ReturnType<typeof vi.fn> };

const ME = { role: 'user', username: 'ada', full_name: 'Ada L', email: 'ada@x.io' };

const Probe = () => {
  const { user, loading, logout } = useAuth();
  return (
    <div>
      <span data-testid="loading">{String(loading)}</span>
      <span data-testid="user">{user ? user.username : 'anonymous'}</span>
      <button onClick={() => void logout()}>Log out</button>
    </div>
  );
};

const renderAuth = () => render(<AuthProvider><Probe /></AuthProvider>);

describe('AuthContext', () => {
  beforeEach(() => {
    mockApi.get.mockReset();
    mockApi.post.mockReset();
  });

  it('resolves the session from /api/auth/me on mount', async () => {
    mockApi.get.mockResolvedValue({ data: ME });
    renderAuth();
    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('ada'));
    expect(screen.getByTestId('loading')).toHaveTextContent('false');
    expect(mockApi.get).toHaveBeenCalledWith('/api/auth/me', expect.anything());
  });

  it('ends in an anonymous, non-loading state when there is no session', async () => {
    mockApi.get.mockRejectedValue(new Error('401'));
    renderAuth();
    // loading must reach false even on failure, or the app renders a spinner forever
    await waitFor(() => expect(screen.getByTestId('loading')).toHaveTextContent('false'));
    expect(screen.getByTestId('user')).toHaveTextContent('anonymous');
  });

  it('clears the cached profile when the session check fails', async () => {
    localStorage.setItem('skillpath_profile', JSON.stringify(ME));
    mockApi.get.mockRejectedValue(new Error('401'));
    renderAuth();
    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('anonymous'));
    // A stale cache would keep showing a logged-in user after the cookie expired.
    expect(localStorage.getItem('skillpath_profile')).toBeNull();
  });

  it('clears user and cache on logout', async () => {
    mockApi.get.mockResolvedValue({ data: ME });
    mockApi.post.mockResolvedValue({ data: {} });
    renderAuth();
    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('ada'));

    await userEvent.click(screen.getByRole('button', { name: 'Log out' }));

    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('anonymous'));
    expect(mockApi.post).toHaveBeenCalledWith('/api/auth/logout');
    expect(localStorage.getItem('skillpath_profile')).toBeNull();
  });

  it('still clears local state when the logout request fails', async () => {
    mockApi.get.mockResolvedValue({ data: ME });
    mockApi.post.mockRejectedValue(new Error('network down'));
    renderAuth();
    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('ada'));

    await userEvent.click(screen.getByRole('button', { name: 'Log out' }));

    // If a failed request left the user signed in, "log out" would appear to
    // do nothing on a flaky connection.
    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('anonymous'));
    expect(localStorage.getItem('skillpath_profile')).toBeNull();
  });

  it('does not set state after unmount', async () => {
    // Regression guard for the cancelled flag in the mount effect.
    const errors: string[] = [];
    const spy = vi.spyOn(console, 'error').mockImplementation((...a) => void errors.push(String(a[0])));
    let resolve!: (v: unknown) => void;
    mockApi.get.mockReturnValue(new Promise((r) => { resolve = r; }));

    const { unmount } = renderAuth();
    unmount();
    await act(async () => {
      resolve({ data: ME });
      await Promise.resolve();
    });

    expect(errors.filter((e) => e.includes('unmounted'))).toEqual([]);
    spy.mockRestore();
  });
});
