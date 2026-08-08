import { test, expect, mockApi, json } from './fixtures';

const Q1 = 'Walk me through a backend service you designed.';
const Q2 = 'How did you handle partial failures there?';

// The page loads its role list from GET /api/mock-interview before rendering
// either mode, so that must be stubbed too.
const baseRoutes = {
  '/api/mock-interview': (r: never) => json(r, { roles: ['Backend Development'] }),
  '/api/mock-interview/Backend%20Development': (r: never) => json(r, { questions: [] }),
};

const interviewRoutes = () => ({
  ...baseRoutes,
  '/api/mock-interview/start': (r: never) =>
    json(r, { session_id: 's1', question: Q1, role: 'Backend Development' }),
  '/api/mock-interview/answer': (r: never) =>
    json(r, { feedback: 'Clear and specific.', next_question: Q2, question_number: 2 }),
});

const openAiMode = async (page: import('@playwright/test').Page) => {
  await page.goto('/mock-interview');
  // Wait for the role list to land, otherwise the mode toggle re-renders and
  // swallows the click.
  await expect(page.getByRole('combobox')).toBeVisible();
  await page.getByRole('button', { name: 'AI Interview' }).click();
  await expect(page.getByRole('button', { name: /start interview/i })).toBeVisible();
};

test.describe('AI interview', () => {
  test('the first question is visible before the user answers', async ({ page }) => {
    // Regression: currentQuestion was held in state but never rendered, so the
    // question only appeared after it had been answered.
    await mockApi(page, interviewRoutes() as never);
    await openAiMode(page);

    await page.getByRole('button', { name: /start interview/i }).click();

    await expect(page.getByText(Q1)).toBeVisible();
    // Nothing typed yet - the question is there on its own.
    await expect(page.getByPlaceholder(/type your answer/i)).toHaveValue('');
  });

  test('answering reveals the follow-up question and the coach note', async ({ page }) => {
    await mockApi(page, interviewRoutes() as never);
    await openAiMode(page);
    await page.getByRole('button', { name: /start interview/i }).click();
    await expect(page.getByText(Q1)).toBeVisible();

    await page.getByPlaceholder(/type your answer/i).fill('I built an ingestion pipeline.');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByText(Q2)).toBeVisible();
    await expect(page.getByText(/Clear and specific\./)).toBeVisible();
    // The answered question stays in the transcript exactly once.
    await expect(page.getByText(Q1)).toHaveCount(1);
  });

  test('a failed answer keeps the question and the typed text', async ({ page }) => {
    await mockApi(page, {
      ...baseRoutes,
      '/api/mock-interview/start': (r: never) =>
        json(r, { session_id: 's1', question: Q1, role: 'Backend Development' }),
      '/api/mock-interview/answer': (r: never) => json(r, { detail: 'AI provider down' }, 503),
    } as never);
    await openAiMode(page);
    await page.getByRole('button', { name: /start interview/i }).click();
    await expect(page.getByText(Q1)).toBeVisible();

    await page.getByPlaceholder(/type your answer/i).fill('my answer');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByRole('alert')).toBeVisible();
    // The user can retry rather than losing their work.
    await expect(page.getByPlaceholder(/type your answer/i)).toHaveValue('my answer');
    await expect(page.getByText(Q1)).toBeVisible();
  });
});
