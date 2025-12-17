/**
 * End-to-End Tests: Context and Document Selection Patterns
 * 
 * This test suite verifies the nuanced behavior of context and document selection
 * across different page types in the Haiven application. Each page type implements
 * a specific user workflow with optimized UI patterns:
 * 
 * 1. Knowledge Chat: Document search only (information retrieval)
 * 2. Guided Prompts: Both context + documents (expert-assisted work)
 * 3. Cards Generation: Context only (creative ideation)
 * 4. Custom Tools: Neither (specialized UIs)
 * 
 * These tests serve as living documentation of intentional design decisions
 * and prevent regression of workflow-specific optimizations.
 */

import { test, expect } from '@playwright/test';
import { dismissModalIfPresent, navigateToMainPage } from './test-utils';

test.describe('Context and Document Selection Patterns', () => {
  
  test.beforeEach(async ({ page }) => {
    // Use existing utility to navigate and handle modals
    await page.goto('/boba');
    await dismissModalIfPresent(page);
    await page.waitForLoadState('networkidle');
  });

  /**
   * Test Case 1: Knowledge Chat Page
   * URL Pattern: /knowledge-chat
   * Expected: "Select document" only (no "Select your context")
   * Use Case: Document-focused Q&A, information retrieval
   */
  test('Knowledge Chat shows document selection only', async ({ page }) => {
    // Navigate to Knowledge Chat using menu item
    const chatMenuItem = page.getByRole('menuitem', { name: 'Chat with Haiven' });
    await expect(chatMenuItem).toBeVisible();
    await chatMenuItem.click();
    
    // Verify we're on the correct page
    await expect(page).toHaveURL(/.*\/knowledge-chat/);
    await expect(page.getByRole('heading', { name: 'Chat with Haiven' })).toBeVisible();

    // Expand "Attach more context" section
    const attachButton = page.getByRole('button', { name: /Attach more context/i });
    await expect(attachButton).toBeVisible();
    await attachButton.click();
    
    // Wait for context section to expand
    await page.waitForTimeout(500);

    // Should show "Select document" (verified with MCP exploration)
    await expect(page.locator('text=Select document')).toBeVisible();
    await expect(page.locator('text=Please select the document(s)')).toBeVisible();

    // Should NOT show "Select your context" (verified with MCP exploration) 
    await expect(page.locator('text=Select your context')).not.toBeVisible();
    await expect(page.locator('text=Add Context')).not.toBeVisible();

    // Should show image upload option
    await expect(page.locator('text=Upload image')).toBeVisible();

    console.log('✅ Knowledge Chat: Documents only pattern verified');
  });

  /**
   * Test Case 2: Guided Prompt Pages (Chat with specific prompt)
   * URL Pattern: /chat?prompt=<id>
   * Expected: Both "Select your context" AND "Select document"
   * Use Case: Expert-assisted work with both guidance and supporting materials
   */
  test('Guided Prompt pages show both context and document selection', async ({ page }) => {
    // Navigate to Ideate menu
    const ideateMenuItem = page.getByRole('menuitem', { name: 'Ideate' });
    await expect(ideateMenuItem).toBeVisible();
    await ideateMenuItem.click();

    // Navigate to a specific prompt page (use first matching link to avoid strict mode violation)
    const businessValueLink = page.getByRole('link', { name: 'Business Value Articulation Assistant', exact: true });
    await expect(businessValueLink).toBeVisible();
    await businessValueLink.click();
    await expect(page).toHaveURL(/.*\/chat\?prompt=business-value-articulation/);

    // Verify we're on the correct page
    await expect(page.getByRole('heading', { name: 'Business Value Articulation Assistant' })).toBeVisible();

    // Expand context selection panel
    const attachButton = page.getByRole('button', { name: /Attach more context/i });
    await expect(attachButton).toBeVisible();
    await attachButton.click();
    
    // Wait for context section to expand
    await page.waitForTimeout(500);

    // Should show BOTH "Select your context" AND "Select document" (verified with MCP exploration)
    await expect(page.locator('text=Select your context')).toBeVisible();
    await expect(page.locator('text=Add Context')).toBeVisible();
    await expect(page.locator('text=Please select the context(s)')).toBeVisible();

    await expect(page.locator('text=Select document')).toBeVisible();
    await expect(page.locator('text=Please select the document(s)')).toBeVisible();

    // Should show image upload option
    await expect(page.locator('text=Upload image')).toBeVisible();

    // Verify both have selection limits (0 / 3)
    await expect(page.locator('text=0 / 3').first()).toBeVisible();

    console.log('✅ Guided Prompts: Both context and documents pattern verified');
  });

  /**
   * Test Case 3: Cards Generation Pages
   * URL Pattern: /cards?prompt=<id>
   * Expected: "Select your context" only (no "Select document")
   * Use Case: Creative ideation where context guides style but documents would slow flow
   */
  test('Cards Generation shows context selection only', async ({ page }) => {
    // Navigate to a cards-based prompt
    await page.click('text=Analyse');
    await page.click('text=Requirements Breakdown');
    await expect(page).toHaveURL(/.*\/cards\?prompt=requirements-breakdown/);

    // Cards pages use a different approach - the context panel might be expanded by default
    // Check if context is already visible, if not try to expand it
    const contextVisible = await page.locator('text=Select your context').isVisible();
    if (!contextVisible) {
      const advancedPrompting = page.locator('[data-testid="advanced-prompting"]');
      if (await advancedPrompting.isVisible()) {
        await advancedPrompting.click();
        await page.waitForTimeout(500);
      }
    }

    // Should show "Select your context"
    await expect(page.locator('text=Select your context')).toBeVisible();
    await expect(page.locator('text=Add Context')).toBeVisible();
    await expect(page.locator('text=Please select the context(s)')).toBeVisible();

    // Should NOT show "Select document"
    await expect(page.locator('text=Select document')).not.toBeVisible();
    await expect(page.locator('text=Please select the document(s)')).not.toBeVisible();

    // Should NOT show image upload (cards focus on text ideation)
    await expect(page.locator('text=Upload image')).not.toBeVisible();

    console.log('✅ Cards Generation: Context only pattern verified');
  });

  /**
   * Test Case 4: Custom Tool Pages
   * URL Pattern: /creative-matrix, /scenarios
   * Expected: Neither selection (specialized UIs)
   * Use Case: Custom interactive tools with their own parameter systems
   */
  test('Custom Tool pages show neither context nor document selection', async ({ page }) => {
    // Test Creative Matrix
    await page.click('text=Ideate');
    await page.click('text=Creative Matrix');
    await expect(page).toHaveURL(/.*\/creative-matrix/);

    // Should NOT show either selection type or attach context button
    await expect(page.locator('text=Select your context')).not.toBeVisible();
    await expect(page.locator('text=Select document')).not.toBeVisible();
    await expect(page.locator('text=Attach more context')).not.toBeVisible();
    await expect(page.locator('[data-testid="advanced-prompting"]')).not.toBeVisible();

    // Should show custom tool interface
    await expect(page.locator('text=Specify matrix parameters')).toBeVisible();

    console.log('✅ Creative Matrix: Neither selection pattern verified');

    // Test Scenario Design
    await page.click('text=Scenario Design');
    await expect(page).toHaveURL(/.*\/scenarios/);

    // Should NOT show either selection type
    await expect(page.locator('text=Select your context')).not.toBeVisible();
    await expect(page.locator('text=Select document')).not.toBeVisible();
    await expect(page.locator('text=Attach more context')).not.toBeVisible();

    // Should show custom scenario interface
    await expect(page.locator('text=Specify scenario parameters')).toBeVisible();

    console.log('✅ Scenario Design: Neither selection pattern verified');
  });

  /**
   * Test Case 5: Dashboard Page
   * Expected: Neither selection (navigation page)
   * Use Case: Navigation and overview, no chat functionality
   */
  test('Dashboard shows no context or document selection', async ({ page }) => {
    // Should be on dashboard already (with trailing slash)
    await expect(page).toHaveURL(/.*\/boba\/?$/);

    // Should NOT show either selection type
    await expect(page.locator('text=Select your context')).not.toBeVisible();
    await expect(page.locator('text=Select document')).not.toBeVisible();
    await expect(page.locator('text=Attach more context')).not.toBeVisible();

    // Should show dashboard content
    await expect(page.locator('text=What would you like to do today?')).toBeVisible();

    console.log('✅ Dashboard: Neither selection pattern verified');
  });

  /**
   * Test Case 6: Context Selection Functionality
   * Verify that context selection works when present
   */
  test('Context selection functionality works correctly', async ({ page }) => {
    // Go to a page with context selection (guided prompt)
    await page.click('text=Ideate');
    await page.click('text=How Might We');
    
    // Use the same selector pattern as working tests
    const attachButton = page.getByRole('button', { name: /Attach more context/i });
    await expect(attachButton).toBeVisible();
    await attachButton.click();
    await page.waitForTimeout(500);

    // Verify context selection is present and functional
    await expect(page.locator('text=Select your context')).toBeVisible();
    await expect(page.locator('text=Add Context')).toBeVisible();
    
    console.log('✅ Context selection functionality verified');
  });

  /**
   * Test Case 7: Document Selection Functionality
   * Verify that document selection works when present
   */
  test('Document selection functionality works correctly', async ({ page }) => {
    // Go to Knowledge Chat (has document selection)
    const chatMenuItem = page.getByRole('menuitem', { name: 'Chat with Haiven' });
    await expect(chatMenuItem).toBeVisible();
    await chatMenuItem.click();
    
    // Use the same selector pattern as working tests
    const attachButton = page.getByRole('button', { name: /Attach more context/i });
    await expect(attachButton).toBeVisible();
    await attachButton.click();
    await page.waitForTimeout(500);

    // Verify document selection is present and functional
    await expect(page.locator('text=Select document')).toBeVisible();
    await expect(page.locator('text=Please select the document(s)')).toBeVisible();

    console.log('✅ Document selection functionality verified');
  });

  /**
   * Test Case 8: Workflow Pattern Consistency
   * Verify that the same URL patterns consistently show the same selection types
   */
  test('URL patterns consistently show expected selection types', async ({ page }) => {
    // Test multiple chat prompts to ensure consistency
    const chatPrompts = [
      { name: 'Business Value Articulation Assistant', url: 'business-value-articulation' },
      { name: 'Feature Prioritization Assistant', url: 'feature-prioritization' },
      { name: 'How Might We', url: 'design-thinking-how-might-we' }
    ];

    for (const prompt of chatPrompts) {
      await page.click('text=Ideate');
      await page.click(`text=${prompt.name}`);
      await expect(page).toHaveURL(new RegExp(`.*\\/chat\\?prompt=.*${prompt.url.split('-')[0]}`));
      
      // Use the working selector pattern  
      const attachButton = page.getByRole('button', { name: /Attach more context/i });
      await expect(attachButton).toBeVisible();
      await attachButton.click();
      await page.waitForTimeout(500);
      
      // All chat prompts should show both selections
      await expect(page.locator('text=Select your context')).toBeVisible();
      await expect(page.locator('text=Select document')).toBeVisible();
      
      console.log(`✅ Chat prompt ${prompt.name}: Both selections verified`);
    }

    // Test multiple cards prompts
    const cardsPrompts = [
      { name: 'Requirements Breakdown', category: 'Analyse' },
      { name: 'User Story Refinement', category: 'Analyse' }
    ];

    for (const prompt of cardsPrompts) {
      await page.click(`text=${prompt.category}`);
      await page.click(`text=${prompt.name}`);
      await expect(page).toHaveURL(/.*\/cards\?prompt=/);
      
      // Cards pages use different approach than chat pages
      const advancedPrompting = page.locator('[data-testid="advanced-prompting"]');
      if (await advancedPrompting.isVisible()) {
        await advancedPrompting.click();
        await page.waitForTimeout(500);
      }
      
      // All cards prompts should show context only
      await expect(page.locator('text=Select your context')).toBeVisible();
      await expect(page.locator('text=Select document')).not.toBeVisible();
      
      console.log(`✅ Cards prompt ${prompt.name}: Context only verified`);
    }
  });

});

/**
 * Test Summary & Business Value
 * 
 * These tests verify that our application implements three distinct user workflows:
 * 
 * 1. 📄 INFORMATION RETRIEVAL (/knowledge-chat)
 *    - Documents only for factual lookup
 *    - Optimized for search accuracy
 * 
 * 2. 🎯 EXPERT-ASSISTED WORK (/chat?prompt=*)
 *    - Both context + documents for comprehensive support
 *    - Optimized for work output quality
 * 
 * 3. 💡 CREATIVE IDEATION (/cards?prompt=*)
 *    - Context only for guided brainstorming
 *    - Optimized for speed and creative flow
 * 
 * 4. 🛠️ SPECIALIZED TOOLS (/creative-matrix, /scenarios)
 *    - Custom interfaces for specific tasks
 *    - Optimized for specialized workflows
 * 
 * This design prevents feature bloat and optimizes each workflow for its intended
 * success metrics. The tests serve as living documentation of these intentional
 * design decisions and prevent regression of workflow-specific optimizations.
 */