import { Page } from '@playwright/test';

// Helper function to dismiss modal if present
export async function dismissModalIfPresent(page: Page) {
  try {
    const modal = page.getByRole('dialog');
    const understandButton = modal.getByRole('button', { name: /i understand/i });
    if (await understandButton.isVisible()) {
      await understandButton.click();
      await page.waitForTimeout(500); // Wait for modal to close
    }
  } catch (e) {
    // Modal might not be present, continue
  }
}

// Helper function to wait for element to be visible and stable
export async function waitForElementStable(page: Page, selector: string, timeout = 10000) {
  await page.waitForSelector(selector, { state: 'visible', timeout });
  // Additional wait to ensure element is fully stable
  await page.waitForTimeout(1000);
}

// Helper function to wait for streaming to complete
export async function waitForStreamingComplete(page: Page) {
  try {
    // Wait for either substantial content or specific elements to appear
    await page.waitForFunction(() => {
      // Check for substantial content
      const contentElements = document.querySelectorAll('p, div, span, h1, h2, h3, h4, h5, h6, li');
      const textContent = Array.from(contentElements).map(el => el.textContent).join(' ');
      
      // Check for specific elements that indicate completion
      const hasCards = document.querySelectorAll('.ant-card').length > 0;
      const hasCopyAll = Array.from(document.querySelectorAll('button')).some(btn => btn.textContent?.includes('COPY ALL'));
      const hasGenerateMore = Array.from(document.querySelectorAll('button')).some(btn => btn.textContent?.includes('GENERATE MORE CARDS'));
      const hasEnrichCards = Array.from(document.querySelectorAll('button')).some(btn => btn.textContent?.includes('ENRICH CARDS'));
      
      // Check for loading indicators (if any exist)
      const loadingElements = document.querySelectorAll('[class*="loading"], [class*="spinner"], [class*="typing"], [class*="animate"], [class*="pulse"]');
      const typingIndicators = document.querySelectorAll('[class*="cursor"], [class*="blink"]');
      
      // If there are loading indicators, wait for them to disappear
      if (loadingElements.length > 0 || typingIndicators.length > 0) {
        return false;
      }
      
      // Return true if we have substantial content or specific completion indicators
      return textContent.length > 200 || hasCards || hasCopyAll || hasGenerateMore || hasEnrichCards;
    }, { timeout: 60000 });
    
    console.log('✓ Content generation completed');
  } catch (error) {
    console.log('⚠ Streaming detection timed out, using fallback wait');
    // Fallback: wait for any substantial content
    await page.waitForFunction(() => {
      const contentElements = document.querySelectorAll('p, div, span, h1, h2, h3, h4, h5, h6, li');
      const textContent = Array.from(contentElements).map(el => el.textContent).join(' ');
      return textContent.length > 100; // Lower threshold for fallback
    }, { timeout: 30000 });
    console.log('✓ Fallback: Content detected');
  }
  
  // Brief wait to ensure content is fully rendered
  await page.waitForTimeout(2000);
}

// Helper function to navigate to the main page and dismiss modal
export async function navigateToMainPage(page: Page) {
  await page.goto('/');
  await dismissModalIfPresent(page);
  await page.waitForLoadState('networkidle');
}

// Helper function to wait for streaming with fallback (for client research)
export async function waitForStreamingCompleteWithFallback(page: Page) {
  try {
    // Wait for either substantial content or specific elements to appear
    await page.waitForFunction(() => {
      // Check for substantial content
      const contentElements = document.querySelectorAll('p, div, span, h1, h2, h3, h4, h5, h6, li');
      const textContent = Array.from(contentElements).map(el => el.textContent).join(' ');
      
      // Check for specific elements that indicate completion
      const hasSources = Array.from(document.querySelectorAll('h5')).some(h5 => h5.textContent?.includes('Sources')) || document.querySelector('a[href*="http"]');
      const hasCards = document.querySelectorAll('.scenarios-collection .ant-card').length > 0;
      const hasCopyAll = Array.from(document.querySelectorAll('button')).some(btn => btn.textContent?.includes('COPY ALL'));
      
      return textContent.length > 500 || hasSources || hasCards || hasCopyAll;
    }, { timeout: 60000 });
    
    console.log('✓ Content generation completed');
  } catch (error) {
    console.log('⚠ Streaming detection timed out, using fallback wait');
    // Fallback: wait for any substantial content
    await page.waitForFunction(() => {
      const contentElements = document.querySelectorAll('p, div, span, h1, h2, h3, h4, h5, h6, li');
      const textContent = Array.from(contentElements).map(el => el.textContent).join(' ');
      return textContent.length > 200; // Lower threshold for fallback
    }, { timeout: 30000 });
    console.log('✓ Fallback: Content detected');
  }
  
  // Brief wait to ensure content is fully rendered
  await page.waitForTimeout(1000);
} 