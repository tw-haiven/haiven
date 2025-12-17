import { test, expect } from '@playwright/test';
import { dismissModalIfPresent, waitForStreamingComplete } from './test-utils';

test.describe('Chat Focus Behavior', () => {
  test('should maintain focus on input after AI response completes', async ({ page }) => {
    await page.goto('/boba/knowledge-chat');
    await dismissModalIfPresent(page);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Click on the input to focus it initially
    const input = page.getByTestId('chat-user-input');
    await input.click();
    
    // Verify input is focused
    await expect(input).toBeFocused();
    
    // Type a test message
    await input.fill('Test message for focus behavior verification');
    
    // Send the message
    const sendButton = page.getByRole('button', { name: /send/i });
    await sendButton.click();
    
    // Wait for response to complete
    await waitForStreamingComplete(page);
    
    // Check that input is focused again after response
    await expect(input).toBeFocused();
    
    console.log('✓ Input focus restored after AI response');
  });

  test('should allow immediate typing without clicking after response', async ({ page }) => {
    await page.goto('/boba/knowledge-chat');
    await dismissModalIfPresent(page);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Click on the input and send first message
    const input = page.getByTestId('chat-user-input');
    await input.click();
    await input.fill('First message to start conversation');
    
    const sendButton = page.getByRole('button', { name: /send/i });
    await sendButton.click();
    
    // Wait for response to complete
    await waitForStreamingComplete(page);
    
    // Now try typing immediately without clicking
    await page.keyboard.type('Second message typed without clicking');
    
    // Verify the text was entered in the input
    await expect(input).toHaveValue('Second message typed without clicking');
    
    console.log('✓ Can type immediately without clicking after response');
  });

  test('should handle multiple conversation exchanges with maintained focus', async ({ page }) => {
    await page.goto('/boba/knowledge-chat');
    await dismissModalIfPresent(page);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    const input = page.getByTestId('chat-user-input');
    const sendButton = page.getByRole('button', { name: /send/i });
    
    // First exchange
    await input.click();
    await input.fill('Message 1');
    await sendButton.click();
    await waitForStreamingComplete(page);
    await expect(input).toBeFocused();
    
    // Second exchange - type without clicking
    await page.keyboard.type('Message 2');
    await sendButton.click();
    await waitForStreamingComplete(page);
    await expect(input).toBeFocused();
    
    // Third exchange - type without clicking
    await page.keyboard.type('Message 3');
    await sendButton.click();
    await waitForStreamingComplete(page);
    await expect(input).toBeFocused();
    
    console.log('✓ Focus maintained across multiple conversation exchanges');
  });

  test('should restore focus even after page interactions', async ({ page }) => {
    await page.goto('/boba/knowledge-chat');
    await dismissModalIfPresent(page);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    const input = page.getByTestId('chat-user-input');
    
    // Send initial message
    await input.click();
    await input.fill('Test focus restoration after interactions');
    
    const sendButton = page.getByRole('button', { name: /send/i });
    await sendButton.click();
    
    // Wait for response to complete
    await waitForStreamingComplete(page);
    
    // Click somewhere else on the page to lose focus
    await page.click('h3'); // Click on the page title
    
    // Verify focus is lost
    await expect(input).not.toBeFocused();
    
    // Send another message to trigger focus restoration
    await input.click();
    await input.fill('Another message to test focus restoration');
    await sendButton.click();
    
    // Wait for response and verify focus is restored
    await waitForStreamingComplete(page);
    await expect(input).toBeFocused();
    
    console.log('✓ Focus properly restored after page interactions');
  });
});