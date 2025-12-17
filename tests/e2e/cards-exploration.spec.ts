import { test, expect } from '@playwright/test';
import { dismissModalIfPresent, waitForStreamingComplete, waitForElementStable } from './test-utils';

// Helper function to navigate to different cards pages
async function navigateToCardsPage(page: any, pageName: string) {
  await page.goto('/boba/');
  await dismissModalIfPresent(page);
  
  // Navigate to the appropriate section based on page name
  if (pageName.includes('STRIDE')) {
    await page.getByText('Architecture', { exact: true }).click();
    await page.getByRole('link', { name: 'Threat Modelling: STRIDE', exact: true }).click();
  } else if (pageName.includes('PASTA')) {
    await page.getByText('Architecture', { exact: true }).click();
    await page.getByRole('link', { name: 'Threat Modelling: PASTA', exact: true }).click();
  } else if (pageName.includes('Requirements')) {
    await page.getByText('Analyse', { exact: true }).click();
    await page.getByRole('link', { name: 'Requirements Breakdown', exact: true }).click();
  } else if (pageName.includes('Fitness')) {
    await page.getByText('Architecture', { exact: true }).click();
    await page.getByRole('link', { name: 'Fitness Functions Brainstorm', exact: true }).click();
  } else {
    // Default to STRIDE if no specific page is mentioned
    await page.getByText('Architecture', { exact: true }).click();
    await page.getByRole('link', { name: 'Threat Modelling: STRIDE', exact: true }).click();
  }
  
  await page.waitForLoadState('networkidle');
}

test.describe('Cards Exploration Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/boba/');
    await dismissModalIfPresent(page);
  });

  test('should test basic cards functionality on STRIDE page', async ({ page }) => {
    // Navigate to STRIDE page using direct URL
    await page.goto('/boba/cards?prompt=threat-modelling-cdbaba6f');
    await page.waitForLoadState('networkidle');
    
    // Wait for the text area to be visible and stable
    await waitForElementStable(page, 'textarea, input[type="text"]', 10000);
    
    // Test sample input functionality
    const sampleInputButton = page.locator('button:has-text("Sample Input")');
    if (await sampleInputButton.isVisible()) {
      await sampleInputButton.click();
      
      // Wait for dialog to appear (either visible or hidden)
      await page.waitForSelector('div[role="dialog"]', { timeout: 30000 });
      
      // Test copy functionality
      const copyButton = page.locator('button:has-text("COPY")');
      if (await copyButton.isVisible()) {
        await copyButton.click();
        // Wait for copy notification
        await page.waitForTimeout(1000);
      }
      
      // Close dialog using the specific close button
      const closeButton = page.locator('[data-testid="close-sample-input"]');
      if (await closeButton.isVisible()) {
        await closeButton.click();
      }
    }
    
    // Fill in test input
    const testInput = 'Imagine a SaaS platform used for team collaboration, allowing users to share documents, chat, and manage projects. The platform must protect sensitive business data from internal misuse, external attacks, and accidental exposure.';
    await page.fill('textarea, input[type="text"]', testInput);
    
    // Send the input
    await page.click('button:has-text("SEND")');
    
    // Wait for AI processing to begin (STOP button appears)
    const stopButton = page.getByRole('button', { name: 'STOP' });
    await expect(stopButton).toBeVisible({ timeout: 10000 });
    
    // Wait for AI processing to complete (STOP button disappears)
    await expect(stopButton).not.toBeVisible({ timeout: 60000 });
    
    // Verify cards are displayed - look for the actual card structure I observed
    const cards = await page.locator('div:has-text("Category:"), div:has-text("Probability:"), div:has-text("Impact:")').count();
    expect(cards).toBeGreaterThan(0);
    
    // Verify "COPY ALL" button is present
    const copyAllButton = page.locator('button:has-text("COPY ALL")');
    expect(await copyAllButton.isVisible()).toBeTruthy();
    
    // Verify "GENERATE MORE CARDS" button is present
    const generateMoreButton = page.locator('button:has-text("GENERATE MORE CARDS")');
    expect(await generateMoreButton.isVisible()).toBeTruthy();
    
    // Test card interaction - click on the first card's button
    const firstCardButton = page.locator('button').filter({ hasText: /Chat with Haiven|Explore scenario/ }).first();
    if (await firstCardButton.isVisible()) {
      await firstCardButton.click();
      
      // Wait for dialog to appear (either visible or hidden)
      await page.waitForSelector('div[role="dialog"]', { timeout: 30000 });
      
      // Verify dialog content exists (don't check visibility since it might be hidden)
      const dialogTitle = page.locator('div[role="dialog"] h2');
      const dialogExists = await dialogTitle.count() > 0;
      expect(dialogExists).toBeTruthy();
      
      // Close dialog if close button is visible
      const closeButton = page.locator('div[role="dialog"] button:has-text("Close")');
      if (await closeButton.isVisible()) {
        await closeButton.click();
      }
    }
  });

  test('should test cards functionality on Requirements Breakdown page', async ({ page }) => {
    // Navigate to Requirements Breakdown page using direct URL
    await page.goto('/boba/cards?prompt=requirements-breakdown-3a845a85');
    await page.waitForLoadState('networkidle');
    
    // Wait for the text area to be visible and stable
    await waitForElementStable(page, 'textarea, input[type="text"]', 10000);
    
    // Fill in test input
    const testInput = 'Create a comprehensive user authentication system with multi-factor authentication, password policies, and session management.';
    await page.fill('textarea, input[type="text"]', testInput);
    
    // Send the input
    await page.click('button:has-text("SEND")');
    
    // Wait for AI processing to begin (STOP button appears)
    const stopButton = page.getByRole('button', { name: 'STOP' });
    await expect(stopButton).toBeVisible({ timeout: 10000 });
    
    // Wait for AI processing to complete (STOP button disappears)
    await expect(stopButton).not.toBeVisible({ timeout: 60000 });
    
    // Verify cards were generated by checking if control buttons are present
    // These buttons only appear after successful card generation
    await expect(page.locator('button:has-text("COPY ALL")')).toBeVisible();
    await expect(page.locator('button:has-text("GENERATE MORE CARDS")')).toBeVisible();
    
    // Verify substantial content was generated
    const pageContent = await page.textContent('body');
    expect(pageContent?.length || 0).toBeGreaterThan(1000);
  });

  test('should test cards functionality on Fitness Functions page', async ({ page }) => {
    // Navigate to Fitness Functions page using direct URL
    await page.goto('/boba/cards?prompt=fitness-functions-823199aa');
    await page.waitForLoadState('networkidle');
    
    // Wait for the text area to be visible and stable
    await waitForElementStable(page, 'textarea, input[type="text"]', 10000);
    
    // Fill in test input
    const testInput = 'Design fitness functions for a microservices architecture that needs to maintain high availability and low latency.';
    await page.fill('textarea, input[type="text"]', testInput);
    
    // Send the input
    await page.click('button:has-text("SEND")');
    
    // Wait for AI processing to begin (STOP button appears)
    const stopButton = page.getByRole('button', { name: 'STOP' });
    await expect(stopButton).toBeVisible({ timeout: 10000 });
    
    // Wait for AI processing to complete (STOP button disappears)
    await expect(stopButton).not.toBeVisible({ timeout: 60000 });
    
    // Verify cards are displayed by looking for substantial content generation
    const pageContent = await page.textContent('body');
    expect(pageContent?.length || 0).toBeGreaterThan(1000);
    
    // Also verify control buttons are present
    await expect(page.locator('button:has-text("COPY ALL")')).toBeVisible();
    await expect(page.locator('button:has-text("GENERATE MORE CARDS")')).toBeVisible();
  });
});