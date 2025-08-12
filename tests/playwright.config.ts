import { defineConfig, devices } from '@playwright/test';
import { existsSync } from 'fs';

// Determine if we're running local tests (includes webServer)  
const isLocalTest = !process.env.PLAYWRIGHT_PROJECT || 
  process.env.PLAYWRIGHT_PROJECT === 'local';

// Check if auth files exist
const demoAuthExists = existsSync('playwright/.auth/demo-user.json');
const prodAuthExists = existsSync('playwright/.auth/prod-user.json');

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false, // Disable full parallelization to reduce load
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1, // Add retries for local development
  workers: 5, // Limit to 5 workers instead of unlimited
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/test-results.json' }],
    ['junit', { outputFile: 'test-results/test-results.xml' }]
  ],
  // Add global timeout
  timeout: 60000,
  projects: [
    // Local development environment
    {
      name: 'local',
      use: { 
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:8080',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
        actionTimeout: 30000,
        navigationTimeout: 30000,
      },
    },
    // Demo environment
    {
      name: 'demo',
      use: { 
        ...devices['Desktop Chrome'],
        baseURL: 'https://team-ai-owd2wjctzq-uc.a.run.app',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
        actionTimeout: 60000,
        navigationTimeout: 60000,
        ...(demoAuthExists ? { storageState: 'playwright/.auth/demo-user.json' } : {}),
      },
    },
    // Production environment
    {
      name: 'prod',
      use: { 
        ...devices['Desktop Chrome'],
        baseURL: 'https://haiven.thoughtworks-labs.net',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
        actionTimeout: 60000,
        navigationTimeout: 60000,
        ...(prodAuthExists ? { storageState: 'playwright/.auth/prod-user.json' } : {}),
      },
    }
  ],
  // Only include webServer for local tests
  ...(isLocalTest && {
    webServer: {
      command: 'cd ui && yarn copy && cd .. && poetry run app',
      url: 'http://localhost:8080',
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
  }),
}); 