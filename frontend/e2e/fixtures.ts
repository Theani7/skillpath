import { test as base, type Page, type Route } from '@playwright/test';

export const USER = {
  role: 'user',
  username: 'ada',
  full_name: 'Ada Lovelace',
  email: 'ada@example.com',
};

export const ADMIN = { ...USER, role: 'admin', username: 'admin', full_name: 'Site Admin' };

const json = (route: Route, body: unknown, status = 200) =>
  route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });

/**
 * Stub every /api/** call so the suite exercises real routing, rendering and
 * navigation without needing a live backend or database.
 *
 * Handlers are matched most-specific-first; anything unmatched returns 404 so
 * a forgotten route surfaces as a visible failure rather than a hang.
 */
export async function mockApi(
  page: Page,
  overrides: Record<string, (route: Route) => Promise<void> | void> = {},
) {
  const defaults: Record<string, (route: Route) => Promise<void> | void> = {
    '/api/auth/me': (r) => json(r, USER),
    '/api/auth/logout': (r) => json(r, { message: 'Logged out successfully' }),
    '/api/user/history': (r) => json(r, { history: [] }),
    '/api/user/profile': (r) => json(r, { profile: {} }),
    '/api/user/preferences': (r) => json(r, { preferences: {} }),
    '/api/user/skill-trends': (r) => json(r, { trends: [], analyses_count: 0 }),
    '/api/user/latest-analysis': (r) => json(r, { found: false }),
    '/api/job-roles': (r) => json(r, { roles: ['Software Engineering', 'Data Science'] }),
    '/api/notifications': (r) => json(r, { notifications: [] }),
  };

  const handlers = { ...defaults, ...overrides };

  await page.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname;
    const key = Object.keys(handlers)
      .filter((k) => path === k || path.startsWith(k))
      .sort((a, b) => b.length - a.length)[0];
    if (key) return handlers[key](route);
    return json(route, { error: `unmocked: ${path}` }, 404);
  });
}

export const test = base.extend<{ mockedPage: Page }>({
  mockedPage: async ({ page }, use) => {
    await mockApi(page);
    await use(page);
  },
});

export { expect, type Page, type Route } from '@playwright/test';
export { json };
