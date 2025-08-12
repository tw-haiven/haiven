import { test, expect } from '@playwright/test';
import { dismissModalIfPresent } from './test-utils';

test.describe('US-001: Pinboard Core Functionality Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await dismissModalIfPresent(page);
  });

  test('should test pinboard dialog interactions (open/close)', async ({ page }) => {
    // Test opening pinboard
    await page.getByRole('button', { name: /pinboard/i }).click({ force: true });
    
    // Verify pinboard modal is visible
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByRole('dialog').getByText('Pinboard')).toBeVisible();
    await expect(page.getByText('Access content you\'ve pinned to reuse in your Haiven inputs.')).toBeVisible();
    
    // Test closing pinboard
    await page.getByRole('dialog').getByRole('button', { name: 'Close' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('should test adding notes to pinboard', async ({ page }) => {
    // Open pinboard
    await page.getByRole('button', { name: /pinboard/i }).click({ force: true });
    
    // Click ADD NOTE button
    await page.getByRole('button', { name: 'ADD NOTE' }).click();
    
    // Verify "Add new Note" dialog is visible
    await expect(page.getByRole('dialog', { name: 'Add new Note' })).toBeVisible();
    
    // Fill in note details
    const noteTitle = 'Test Note for US-001 Automated Test';
    const noteDescription = 'This is a test note created by automated Playwright test to validate pinboard functionality.';
    
    await page.getByTestId('add-content-title').fill(noteTitle);
    await page.getByTestId('add-content-description').fill(noteDescription);
    
    // Save the note
    await page.getByRole('button', { name: 'Save' }).click();
    
    // Verify success notification
    await expect(page.getByText('Content added successfully!')).toBeVisible();
    
    // Switch to Pins/Notes tab to verify the note was saved
    await page.getByRole('tab', { name: 'Pins/Notes' }).click();
    
    // Verify the note appears in the pinboard list (not in the form)
    await expect(page.getByTestId('pin-and-notes-tab').getByText(noteTitle)).toBeVisible();
    await expect(page.getByTestId('pin-and-notes-tab').getByText(noteDescription)).toBeVisible();
  });

  test('should test adding context to pinboard', async ({ page }) => {
    // Open pinboard
    await page.getByRole('button', { name: /pinboard/i }).click({ force: true });
    
    // Click ADD CONTEXT button
    await page.getByRole('button', { name: 'ADD CONTEXT' }).click();
    
    // Verify "Add new Context" dialog is visible
    await expect(page.getByRole('dialog', { name: 'Add new Context' })).toBeVisible();
    
    // Fill in context details
    const contextTitle = 'Test Context for US-001';
    const contextDescription = 'This is a test context created by automated test for pinboard functionality validation.';
    
    await page.getByTestId('add-content-title').fill(contextTitle);
    await page.getByTestId('add-content-description').fill(contextDescription);
    
    // Save the context
    await page.getByRole('button', { name: 'Save' }).click();
    
    // Verify success notification
    await expect(page.getByText('Content added successfully!')).toBeVisible();
    
    // Verify we're on Contexts tab and the context appears
    await expect(page.getByRole('tab', { name: 'Contexts' })).toHaveAttribute('aria-selected', 'true');
    await expect(page.getByTestId('contexts-tab').getByText(contextTitle)).toBeVisible();
    await expect(page.getByTestId('contexts-tab').getByText(contextDescription)).toBeVisible();
  });

  test('should test viewing pinned content', async ({ page }) => {
    // Open pinboard
    await page.getByRole('button', { name: /pinboard/i }).click({ force: true });
    
    // Test Contexts tab
    await page.getByRole('tab', { name: 'Contexts' }).click();
    await expect(page.getByRole('tab', { name: 'Contexts' })).toHaveAttribute('aria-selected', 'true');
    
    // Test Pins/Notes tab
    await page.getByRole('tab', { name: 'Pins/Notes' }).click();
    await expect(page.getByRole('tab', { name: 'Pins/Notes' })).toHaveAttribute('aria-selected', 'true');
    
    // Verify tab content is displayed
    await expect(page.getByRole('tabpanel', { name: 'Pins/Notes' })).toBeVisible();
  });

  test('should test pinboard data validation', async ({ page }) => {
    // Open pinboard
    await page.getByRole('button', { name: /pinboard/i }).click({ force: true });
    
    // Click ADD NOTE button
    await page.getByRole('button', { name: 'ADD NOTE' }).click();
    
    // Try to save without entering title
    await page.getByRole('button', { name: 'Save' }).click();
    
    // Verify validation error message
    await expect(page.getByText('Please enter some title')).toBeVisible();
    
    // Verify the dialog remains open for correction
    await expect(page.getByRole('dialog', { name: 'Add new Note' })).toBeVisible();
  });

  test('should test pinboard persistence across sessions', async ({ page }) => {
    // First, add a note to test persistence
    await page.getByRole('button', { name: /pinboard/i }).click({ force: true });
    await page.getByRole('button', { name: 'ADD NOTE' }).click();
    
    const testTitle = 'Persistence Test Note';
    const testDescription = 'This note tests localStorage persistence across sessions.';
    
    await page.getByTestId('add-content-title').fill(testTitle);
    await page.getByTestId('add-content-description').fill(testDescription);
    await page.getByRole('button', { name: 'Save' }).click();
    
    // Close pinboard
    await page.getByRole('dialog', { name: 'Pinboard' }).getByRole('button', { name: 'Close' }).click();
    
    // Navigate away and back to test persistence
    await page.reload();
    await dismissModalIfPresent(page);
    
    // Open pinboard again
    await page.getByRole('button', { name: /pinboard/i }).click({ force: true });
    await page.getByRole('tab', { name: 'Pins/Notes' }).click();
    
    // Verify the note persisted
    await expect(page.getByTestId('pin-and-notes-tab').getByText(testTitle)).toBeVisible();
    await expect(page.getByTestId('pin-and-notes-tab').getByText(testDescription)).toBeVisible();
  });

  test('should test using pinned content in chat context', async ({ page }) => {
    // Navigate to chat page
    await page.getByRole('link', { name: 'Chat with Haiven' }).click();
    
    // Verify we're on the chat page
    await expect(page.getByText('Chat with Haiven')).toBeVisible();
    
    // Test that pinboard button is accessible from chat page
    await page.getByRole('button', { name: /pinboard/i }).click({ force: true });
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByText('Access content you\'ve pinned to reuse in your Haiven inputs.')).toBeVisible();
    
    // Close pinboard
    await page.getByRole('dialog', { name: 'Pinboard' }).getByRole('button', { name: 'Close' }).click();
    
    // Test "Attach more context" functionality exists
    await page.getByRole('button', { name: /attach more context/i }).click();
    
    // Verify context attachment interface is available
    await expect(page.getByText('Select document')).toBeVisible();
  });
});

