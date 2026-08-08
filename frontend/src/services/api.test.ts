import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { AxiosError } from 'axios';
import api, { registerLogoutHandler } from './api';

/** Pull the rejection handler off the response interceptor axios registered. */
const getRejectionHandler = () => {
  const handlers = (api.interceptors.response as unknown as {
    handlers: { rejected: (e: AxiosError) => Promise<unknown> }[];
  }).handlers;
  return handlers[0].rejected;
};

const makeError = (status: number, url: string, extra: Record<string, unknown> = {}) =>
  ({ config: { url, ...extra }, response: { status } }) as unknown as AxiosError;

describe('api response interceptor', () => {
  let onLogout: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    onLogout = vi.fn();
    registerLogoutHandler(onLogout);
  });

  it('clears auth state on a 401', async () => {
    await expect(getRejectionHandler()(makeError(401, '/api/user/history'))).rejects.toBeDefined();
    expect(onLogout).toHaveBeenCalledTimes(1);
  });

  it('ignores 401s from /auth/me', async () => {
    // /auth/me returning 401 is the normal "not signed in" answer during the
    // initial session probe. Treating it as a logout would fight AuthContext.
    await expect(getRejectionHandler()(makeError(401, '/api/auth/me'))).rejects.toBeDefined();
    expect(onLogout).not.toHaveBeenCalled();
  });

  it('honours _skipAuthRedirect', async () => {
    await expect(
      getRejectionHandler()(makeError(401, '/api/user/x', { _skipAuthRedirect: true })),
    ).rejects.toBeDefined();
    expect(onLogout).not.toHaveBeenCalled();
  });

  it('leaves non-401 errors alone', async () => {
    for (const status of [400, 403, 404, 429, 500]) {
      await expect(getRejectionHandler()(makeError(status, '/api/x'))).rejects.toBeDefined();
    }
    expect(onLogout).not.toHaveBeenCalled();
  });

  it('does not manipulate browser history', async () => {
    // Regression: the interceptor used to call history.pushState + dispatch a
    // popstate event, which never re-rendered React. Navigation belongs to
    // React Router; clearing auth state is what redirects.
    const pushState = vi.spyOn(window.history, 'pushState');
    await expect(getRejectionHandler()(makeError(401, '/api/user/history'))).rejects.toBeDefined();
    expect(pushState).not.toHaveBeenCalled();
    pushState.mockRestore();
  });

  it('sends credentials so httpOnly auth cookies are attached', () => {
    expect(api.defaults.withCredentials).toBe(true);
  });
});
