import { test, expect } from '@playwright/test';
import { dismissModalIfPresent, waitForStreamingCompleteWithFallback, waitForElementStable } from './test-utils';

test.describe('Client Research - Sources Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/boba/');
    await dismissModalIfPresent(page);
    await page.waitForLoadState('networkidle');
  });

  test('should verify Company Overview page has mandatory sources', async ({ page }) => {
    // Navigate to company research page using the correct URL
    await page.goto('/boba/company-research');
    await page.waitForLoadState('networkidle');
    
    // Wait for the textbox to be visible and stable
    await waitForElementStable(page, 'input[placeholder="Enter company name"]', 10000);
    
    // Fill in a company name
    await page.fill('input[placeholder="Enter company name"]', 'Microsoft');
    
    // Click the Research button
    await page.click('button:has-text("Research")');
    
    // Wait for content to load
    await waitForStreamingCompleteWithFallback(page);
    
    // Verify sources are present
    const sourceLinks = page.locator('a[href^="http"]');
    const sourceLinksCount = await sourceLinks.count();
    
    expect(sourceLinksCount).toBeGreaterThan(0);
    console.log(`✓ Found ${sourceLinksCount} source links`);
    
    // Verify each source link is properly formatted
    for (let i = 0; i < Math.min(sourceLinksCount, 5); i++) { // Check first 5 links
      const link = sourceLinks.nth(i);
      const href = await link.getAttribute('href');
      const text = await link.textContent();
      
      expect(href).toBeTruthy();
      expect(href).toMatch(/^https?:\/\//);
      // Text content might be empty but href should be valid
      console.log(`✓ Source link ${i + 1}: "${text || '[no text]'}" -> ${href}`);
    }
  });

  test('should verify Company Overview with AI tools config has sources', async ({ page }) => {
    // Navigate to company research page with AI tools config
    await page.goto('/boba/company-research?config=ai-tool');
    await page.waitForLoadState('networkidle');
    
    // Wait for the textbox to be visible and stable
    await waitForElementStable(page, 'input[placeholder="Enter company name"]', 10000);
    
    // Fill in a company name
    await page.fill('input[placeholder="Enter company name"]', 'OpenAI');
    
    // Click the Research button
    await page.click('button:has-text("Research")');
    
    // Wait for content to load
    await waitForStreamingCompleteWithFallback(page);
    
    // Verify sources are present
    const sourceLinks = page.locator('a[href^="http"]');
    const sourceLinksCount = await sourceLinks.count();
    
    expect(sourceLinksCount).toBeGreaterThan(0);
    console.log(`✓ Found ${sourceLinksCount} source links with AI tools config`);
  });

  test('should verify Ideas to Pitch page has sources', async ({ page }) => {
    // Navigate to ideas to pitch page
    await page.goto('/boba/cards?prompt=company-research-ideas-to-pitch-cdbaba6g');
    await page.waitForLoadState('networkidle');
    
    // Wait for the textbox to be visible and stable
    await waitForElementStable(page, 'textarea, input[type="text"]', 10000);
    
    // Fill in a company name
    await page.fill('textarea, input[type="text"]', 'Tesla');
    
    // Click the SEND button
    await page.click('button:has-text("SEND")');
    
    // Wait for content to load
    await waitForStreamingCompleteWithFallback(page);
    
    // Verify sources are present
    const sourceLinks = page.locator('a[href^="http"]');
    const sourceLinksCount = await sourceLinks.count();
    
    expect(sourceLinksCount).toBeGreaterThan(0);
    console.log(`✓ Found ${sourceLinksCount} source links for ideas to pitch`);
  });
}); 