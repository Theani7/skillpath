import { test, expect, mockApi, json } from './fixtures';

const PDF = { name: 'resume.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4 fake') };

test.describe('Resume upload', () => {
  test('uploads a PDF and navigates to the report', async ({ page }) => {
    let posted = false;
    await mockApi(page, {
      '/api/analyze': (r) => { posted = true; return json(r, { status: 'success', resume_score: 82 }); },
      '/api/user/latest-analysis': (r) => json(r, {
        found: true,
        id: 1,
        target_role: 'Software Engineering',
        resume_score: 82,
        analysis: { status: 'success', resume_score: 82, data: { name: 'Ada', skills: ['Python'] } },
        role_skills: [],
      }),
    });

    await page.goto('/app');
    await page.locator('input[type="file"]').setInputFiles(PDF);
    await page.getByRole('button', { name: /analy/i }).click();

    await expect(page).toHaveURL(/\/analysis/, { timeout: 20_000 });
    expect(posted).toBe(true);
  });

  test('surfaces a server error and stays on the upload page', async ({ page }) => {
    await mockApi(page, {
      '/api/analyze': (r) => json(r, { detail: 'Only PDF and DOCX files are supported' }, 400),
    });

    await page.goto('/app');
    await page.locator('input[type="file"]').setInputFiles(PDF);
    await page.getByRole('button', { name: /analy/i }).click();

    await expect(page.getByText(/Only PDF and DOCX files are supported/)).toBeVisible();
    // Regression: it used to navigate regardless, showing an empty report.
    await expect(page).toHaveURL(/\/app/);
  });

  test('shows the size limit message when the file is too large', async ({ page }) => {
    await mockApi(page, {
      '/api/analyze': (r) => json(r, { detail: 'File too large. Maximum size is 5MB.' }, 413),
    });

    await page.goto('/app');
    await page.locator('input[type="file"]').setInputFiles(PDF);
    await page.getByRole('button', { name: /analy/i }).click();

    // The copy must match the real 5 MiB limit, not the old "10MB" text.
    await expect(page.getByText(/Maximum size is 5MB/)).toBeVisible();
  });

  test('recovers from a rate limit without breaking the page', async ({ page }) => {
    await mockApi(page, {
      '/api/analyze': (r) => json(r, { detail: 'Rate limit exceeded. Try again in a minute.' }, 429),
    });

    await page.goto('/app');
    await page.locator('input[type="file"]').setInputFiles(PDF);
    await page.getByRole('button', { name: /analy/i }).click();

    await expect(page.getByText(/Rate limit exceeded/)).toBeVisible();
    // The button must be usable again rather than stuck in a loading state.
    await expect(page.getByRole('button', { name: /analy/i })).toBeEnabled();
  });

  test('falls back to default roles when the roles endpoint fails', async ({ page }) => {
    await mockApi(page, { '/api/job-roles': (r) => json(r, { detail: 'boom' }, 500) });
    await page.goto('/app');
    const select = page.locator('select').first();
    await expect(select).toBeVisible();
    expect(await select.locator('option').count()).toBeGreaterThan(0);
  });
});
