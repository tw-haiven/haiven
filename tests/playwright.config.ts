import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false, // Disable full parallelization to reduce load
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1, // Add retries for local development
  workers: 2, // Limit to 2 workers instead of unlimited
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/test-results.json' }],
    ['junit', { outputFile: 'test-results/test-results.xml' }]
  ],
  use: {
    baseURL: 'http://localhost:8080',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    // Add longer timeouts for better stability
    actionTimeout: 30000,
    navigationTimeout: 30000,
  },
  // Add global timeout
  timeout: 60000,
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    }
  ],
  webServer: {
    command: 'cd ui && yarn copy && cd .. && poetry run app',
    url: 'http://localhost:8080',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
}); 