import { test, expect, mockApi, json, ADMIN } from './fixtures';

const resume = (id: number, name: string) => ({
  id, // lowercase: Postgres folds the unquoted ID column
  user_id: 4,
  Name: name,
  Email_ID: `${name.toLowerCase()}@x.io`,
  Timestamp: '2026-01-01 10:00:00',
  Predicted_Field: 'Software Engineering',
  resume_score: '80',
  target_role: 'Backend',
  missing_skills: 'Go',
  Actual_skills: 'Python',
  Recommended_skills: 'Rust',
  pdf_name: `${name}.pdf`,
});

const adminRoutes = (over: Record<string, unknown> = {}) => ({
  '/api/auth/me': (r: never) => json(r, ADMIN),
  '/api/admin/users': (r: never) => json(r, {
    users: [resume(1, 'Ada'), resume(2, 'Grace')], total: 2, limit: 20, offset: 0,
  }),
  '/api/admin/feedback': (r: never) => json(r, { feedback: [], total: 0, limit: 20, offset: 0 }),
  '/api/admin/feedback/stats': (r: never) => json(r, {
    total: 0, positive: 0, neutral: 0, negative: 0, ratio: 0, by_score: {},
  }),
  '/api/admin/registered-users': (r: never) => json(r, {
    users: [{ id: 1, username: 'admin', email: 'a@x.io', role: 'admin', is_active: 1 }],
  }),
  '/api/admin/courses': (r: never) => json(r, { courses: [] }),
  '/api/admin/job-roles': (r: never) => json(r, { job_roles: [] }),
  '/api/admin/analytics': (r: never) => json(r, {
    most_sought_role: 'Backend', most_common_missing_skill: 'Go',
  }),
  '/api/admin/quality-metrics': (r: never) => json(r, {
    total_requests: 10, server_errors: 0, avg_latency_ms: 5,
    resume_uploads: 2, feedback_events: 0, parse_failure_rate_pct: 0,
  }),
  '/api/admin/analytics/uploads-over-time': (r: never) => json(r, { data: [] }),
  '/api/admin/analytics/skill-gaps': (r: never) => json(r, { data: [] }),
  '/api/admin/analytics/role-distribution': (r: never) => json(r, { data: [] }),
  '/api/admin/analytics/user-growth': (r: never) => json(r, { data: [] }),
  ...over,
});

test.describe('Admin panel', () => {
  test('renders the dashboard without React key warnings', async ({ page }) => {
    // Regression: rows were keyed on `ID` while the API returns `id`, so every
    // key was undefined and React collapsed the list.
    const warnings: string[] = [];
    page.on('console', (m) => {
      const t = m.text();
      if (/same key|unique "key"/.test(t)) warnings.push(t);
    });

    await mockApi(page, adminRoutes() as never);
    await page.goto('/admin/dashboard');
    await expect(page).toHaveURL(/\/admin\/dashboard/);
    await page.waitForTimeout(1000);
    expect(warnings).toEqual([]);
  });

  test('lists resume logs with real rows', async ({ page }) => {
    await mockApi(page, adminRoutes() as never);
    await page.goto('/admin/resumes');
    // Target the name cell exactly; the email cell also contains the name.
    await expect(page.getByRole('cell', { name: 'Ada', exact: true })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'Grace', exact: true })).toBeVisible();
    await expect(page.getByRole('row')).toHaveCount(3); // header + 2 rows
  });

  test('deleting a resume log calls the analysis endpoint, never a user id', async ({ page }) => {
    // Regression: DELETE /api/admin/users/{id} deleted from the users table
    // while the UI passed a user_data row id, which wiped a real account.
    const deleted: string[] = [];
    await mockApi(page, adminRoutes({
      '/api/admin/users/': (r: never) => {
        const req = (r as unknown as { request(): { method(): string; url(): string } }).request();
        if (req.method() === 'DELETE') {
          deleted.push(new URL(req.url()).pathname);
          return json(r, { status: 'success' });
        }
        return json(r, { users: [resume(1, 'Ada')], total: 1, limit: 20, offset: 0 });
      },
    }) as never);

    await page.goto('/admin/resumes');
    await expect(page.getByRole('cell', { name: 'Ada', exact: true })).toBeVisible();

    await page.getByRole('button', { name: /Delete log 1/i }).click();
    await page.getByRole('button', { name: /^Delete$/i }).click();

    await expect.poll(() => deleted.length, { timeout: 10_000 }).toBeGreaterThan(0);
    // Must target the analysis row id we rendered.
    expect(deleted[0]).toBe('/api/admin/users/1');
  });

  test('survives an admin endpoint returning 500', async ({ page }) => {
    await mockApi(page, adminRoutes({
      '/api/admin/users': (r: never) => json(r, { detail: 'boom' }, 500),
    }) as never);

    await page.goto('/admin/dashboard');
    // A failed panel must not blank the whole app.
    await expect(page.locator('body')).not.toBeEmpty();
    await expect(page.getByText(/Control Panel|Something went wrong/i).first()).toBeVisible();
  });
});
