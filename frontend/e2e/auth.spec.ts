import { test, expect, mockApi, json, ADMIN } from './fixtures';

test.describe('Route protection', () => {
  test('anonymous visitors are redirected off protected routes', async ({ page }) => {
    await mockApi(page, { '/api/auth/me': (r) => json(r, { detail: 'Unauthorized' }, 401) });
    await page.goto('/app');
    // The landing page must take over rather than leaving a blank shell.
    await expect(page).toHaveURL('/');
    await expect(page.locator('body')).not.toBeEmpty();
  });

  test('signed-in users can reach the analyzer', async ({ page }) => {
    await mockApi(page);
    await page.goto('/app');
    await expect(page).toHaveURL(/\/app/);
    await expect(page.locator('input[type="file"]')).toBeAttached();
  });

  test('non-admins cannot reach the admin panel', async ({ page }) => {
    await mockApi(page); // default role: user
    await page.goto('/admin/dashboard');
    // Must not land on the admin dashboard.
    await expect(page).not.toHaveURL(/\/admin\/dashboard/);
  });

  test('admins are routed away from the analyzer to their dashboard', async ({ page }) => {
    await mockApi(page, {
      '/api/auth/me': (r) => json(r, ADMIN),
      '/api/admin': (r) => json(r, {}),
    });
    await page.goto('/app');
    await expect(page).toHaveURL(/\/admin/);
  });

  test('an expired session during navigation returns the user to the landing page', async ({ page }) => {
    let authed = true;
    await mockApi(page, {
      '/api/auth/me': (r) => (authed ? json(r, { role: 'user', username: 'ada', full_name: 'Ada', email: 'a@x.io' }) : json(r, { detail: 'Unauthorized' }, 401)),
      '/api/user/history': (r) => json(r, { detail: 'Unauthorized' }, 401),
    });
    await page.goto('/app');
    await expect(page).toHaveURL(/\/app/);

    // Cookie expires, then a real API call 401s.
    authed = false;
    await page.goto('/profile');
    await expect(page).toHaveURL('/', { timeout: 15_000 });
  });
});

test.describe('Landing page', () => {
  test('renders without console errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });

    await mockApi(page, { '/api/auth/me': (r) => json(r, { detail: 'Unauthorized' }, 401) });
    await page.goto('/');
    await expect(page.locator('body')).not.toBeEmpty();

    // Ignore network noise from blocked third parties; fail on real JS errors.
    const real = errors.filter((e) => !/Failed to load resource|net::ERR/.test(e));
    expect(real).toEqual([]);
  });

  test('exposes a way to sign in', async ({ page }) => {
    await mockApi(page, { '/api/auth/me': (r) => json(r, { detail: 'Unauthorized' }, 401) });
    await page.goto('/');
    const signIn = page.getByRole('button', { name: /log ?in|sign ?in/i }).first();
    await expect(signIn).toBeVisible();
  });
});
