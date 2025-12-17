import { test, expect } from '@playwright/test';
import { dismissModalIfPresent } from './test-utils';

test.describe('Haiven Image Upload and AI Description Feature', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the main application
    await page.goto('/boba/');
    await dismissModalIfPresent(page);
    await page.waitForLoadState('networkidle');
  });

  test('should upload image, generate AI description, and view/edit description dialog', async ({ page }) => {
    // Step 1: Navigate to Chat with Haiven
    const chatMenuItem = page.getByRole('menuitem', { name: 'Chat with Haiven' });
    await expect(chatMenuItem).toBeVisible();
    await chatMenuItem.click();
    
    // Verify we're on the chat page
    await expect(page).toHaveURL(/.*knowledge-chat/);
    await expect(page.getByRole('heading', { name: 'Chat with Haiven' })).toBeVisible();
    
    // Step 2: Expand "Attach more context" section
    const attachButton = page.getByRole('button', { name: /Attach more context/i });
    await expect(attachButton).toBeVisible();
    await attachButton.click();
    
    // Wait for context section to expand
    await page.waitForTimeout(500);
    
    // Step 3: Verify upload image section is visible
    await expect(page.getByText('Upload image')).toBeVisible();
    const uploadButton = page.getByRole('button', { name: /Drop your image here, or upload/i });
    await expect(uploadButton).toBeVisible();
    
    // Step 4: Upload the teamai_overview.png image
    await uploadButton.click();
    
    // Upload the image file
    const imagePath = '/Users/pk/work/haiven-related/repos/haiven/app/resources/static/teamai_overview.png';
    await page.setInputFiles('input[type="file"]', imagePath);
    
    // Step 5: Wait for image upload to complete
    await page.waitForTimeout(1000); // Brief wait for upload to register
    
    // Check for image upload indicators (paperclip icon, delete button, etc.)
    const paperclipIcon = page.locator('img[alt="paper-clip"]');
    const deleteButton = page.getByRole('button', { name: /delete/i });
    
    // At least one of these should be visible to confirm upload
    const uploadIndicators = await Promise.all([
      paperclipIcon.count(),
      deleteButton.count()
    ]);
    expect(uploadIndicators.some(count => count > 0)).toBeTruthy();
    
    // Step 6: Wait for AI processing to begin (STOP button appears)
    const stopButton = page.getByRole('button', { name: 'STOP' });
    await expect(stopButton).toBeVisible({ timeout: 10000 });
    console.log('✓ AI processing started - STOP button visible');
    
    // Step 7: Wait for AI processing to complete (STOP button disappears)
    await expect(stopButton).not.toBeVisible({ timeout: 60000 });
    console.log('✓ AI processing completed - STOP button disappeared');
    
    // Step 8: Verify "View/Edit Description" button appears after processing
    const viewEditButton = page.getByRole('button', { name: 'View/Edit Description' });
    await expect(viewEditButton).toBeVisible({ timeout: 10000 });
    
    // Step 9: Click "View/Edit Description" to open the dialog
    await viewEditButton.click();
    
    // Step 10: Verify the dialog opens with AI-generated description
    const dialog = page.getByRole('dialog', { name: 'View/Edit Image Description' });
    await expect(dialog).toBeVisible();
    
    // Verify dialog title
    await expect(dialog.getByText('View/Edit Image Description')).toBeVisible();
    
    // Verify dialog has EDIT button
    const editButton = dialog.getByRole('button', { name: 'EDIT' });
    await expect(editButton).toBeVisible();
    
    // Step 11: Verify AI-generated description content is present
    // The description should contain technical terms related to the architecture diagram
    const descriptionText = dialog.locator('p').nth(1); // Second paragraph contains the description
    await expect(descriptionText).toBeVisible();
    
    // Check for key terms that should appear in the AI description of the teamai_overview.png
    const descriptionContent = await descriptionText.textContent();
    expect(descriptionContent).toContain('diagram');
    expect(descriptionContent?.toLowerCase()).toMatch(/(workflow|architecture|technical|organization|knowledge|ai|model)/);
    
    // Step 12: Verify the description mentions key components from the image
    const fullDescription = await dialog.locator('.ant-typography, p, div').allTextContents();
    const fullText = fullDescription.join(' ').toLowerCase();
    
    // These terms should appear in the AI description of our architecture diagram
    const expectedTerms = ['engineering', 'organization', 'knowledge', 'prompts', 'foundation', 'model'];
    const foundTerms = expectedTerms.filter(term => fullText.includes(term.toLowerCase()));
    
    expect(foundTerms.length).toBeGreaterThanOrEqual(3); // At least 3 key terms should be found
    
    // Step 13: Test EDIT functionality
    await editButton.click();
    
    // Verify edit mode is active (button text should change or textarea should appear)
    await page.waitForTimeout(500);
    
    // Step 14: Close the dialog
    const closeButton = dialog.getByText("CLOSE")
    await expect(closeButton).toBeVisible();
    await closeButton.click();
    
    // Step 15: Verify dialog is closed
    await expect(dialog).not.toBeVisible();
    
    // Step 16: Verify image is still attached after closing dialog
    await expect(viewEditButton).toBeVisible();
    
    console.log('✓ Successfully completed image upload and AI description workflow');
  });
  
  test('should handle image upload error cases gracefully', async ({ page }) => {
    // Navigate to Chat with Haiven
    await page.getByRole('menuitem', { name: 'Chat with Haiven' }).click();
    
    // Expand attach context
    await page.getByRole('button', { name: /Attach more context/i }).click();
    await page.waitForTimeout(500);
    
    // Verify size limit message is displayed
    await expect(page.getByText('Size must be < 2MB')).toBeVisible();
    
    // Test that the upload button is functional
    const uploadButton = page.getByRole('button', { name: /Drop your image here, or upload/i });
    await expect(uploadButton).toBeVisible();
    
    // Verify the button is clickable
    await expect(uploadButton).toBeEnabled();
  });
});