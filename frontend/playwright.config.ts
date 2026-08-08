import { defineConfig, devices } from '@playwright/test';

const PORT = 4173;

export default defineConfig({
  testDir: './e2e',
  // Kept out of src/ so Vitest and Playwright never pick up each other's specs.
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : [['list']],
  timeout: 30_000,
  expect: { timeout: 10_000 },

  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],

  // Serve the production build. These specs stub the API at the network layer,
  // so no backend is required.
  webServer: {
    // --host 127.0.0.1 is required, not cosmetic. `vite preview` otherwise
    // binds IPv4 loopback only, while Node 22+ on the CI runners resolves
    // localhost to ::1 first, so the readiness probe never connects and the
    // job dies on "Timed out waiting from config.webServer".
    command: `npm run preview -- --host 127.0.0.1 --port ${PORT} --strictPort`,
    url: `http://127.0.0.1:${PORT}/`,
    reuseExistingServer: !process.env.CI,
    // The build is a separate CI step, so this only covers server boot.
    timeout: 120_000,
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
