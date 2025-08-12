import { test, expect } from '@playwright/test';
import { dismissModalIfPresent } from './test-utils';

test.describe('Haiven Scenario Design Page', () => {
  test('should navigate to Scenario Design and display content', async ({ page }) => {
    await page.goto('/');
    await dismissModalIfPresent(page);
    await page.getByRole('link', { name: /scenario design/i }).click();
    await expect(page).toHaveURL(/\/scenarios/);
    await expect(page.getByRole('heading', { name: /scenario design/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /specify scenario parameters/i })).toBeVisible();
    await expect(page.getByRole('textbox', { name: /enter your strategic prompt here/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible();
  });
});
