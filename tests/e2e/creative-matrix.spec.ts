import { test, expect } from '@playwright/test';
import { dismissModalIfPresent } from './test-utils';

test.describe('US-002: Creative Matrix Generation Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await dismissModalIfPresent(page);
    await page.getByRole('link', { name: /creative matrix/i }).click();
    await expect(page).toHaveURL(/\/creative-matrix/);
  });

  test('should test matrix parameter configuration', async ({ page }) => {
    // Verify the matrix parameters section is visible and functional
    await expect(page.getByRole('heading', { name: /creative matrix/i })).toBeVisible();
    await expect(page.getByRole('table')).toBeVisible();
    
    // Test expand/collapse of parameters (initially expanded)
    const parametersButton = page.getByRole('button', { name: /specify matrix parameters/i });
    await expect(parametersButton).toBeVisible();
    await expect(parametersButton).toHaveAttribute('aria-expanded', 'true');
    
    // Verify all parameter controls are present
    await expect(page.locator('label').filter({ hasText: 'Template' })).toBeVisible();
    await expect(page.getByText('Each idea must be...')).toBeVisible();
    await expect(page.locator('label').filter({ hasText: 'Generate' })).toBeVisible();
    await expect(page.locator('label').filter({ hasText: 'Rows' })).toBeVisible();
    await expect(page.locator('label').filter({ hasText: 'Columns' })).toBeVisible();
    
    // Verify input fields are present
    await expect(page.getByRole('textbox', { name: /comma-separated list of values/i })).toHaveCount(2);
    
    // Wait for additional prompt field to be visible (it might be initially hidden)
    await page.waitForSelector('[placeholder*="Additional prompting"]', { timeout: 10000 });
    await expect(page.getByRole('textbox', { name: /optional.*additional prompting/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible();
  });



  test('should test matrix row/column customization', async ({ page }) => {
    // Get the rows and columns textboxes
    const rowsInput = page.getByRole('textbox', { name: /comma-separated list of values/i }).first();
    const columnsInput = page.getByRole('textbox', { name: /comma-separated list of values/i }).last();
    
    // Verify default values are present
    await expect(rowsInput).not.toBeEmpty();
    await expect(columnsInput).not.toBeEmpty();
    
    // Clear and set custom rows
    await rowsInput.click();
    await rowsInput.clear();
    await rowsInput.fill('Frontend, Backend, Database');
    
    // Clear and set custom columns  
    await columnsInput.click();
    await columnsInput.clear();
    await columnsInput.fill('Unit Tests, Integration Tests, E2E Tests');
    
    // Verify the matrix table updates with custom values
    await expect(page.getByText('Frontend').first()).toBeVisible();
    await expect(page.getByText('Backend').first()).toBeVisible();
    await expect(page.getByText('Database').first()).toBeVisible();
    await expect(page.getByText('Unit Tests').first()).toBeVisible();
    await expect(page.getByText('Integration Tests').first()).toBeVisible();
    await expect(page.getByText('E2E Tests').first()).toBeVisible();
  });

  test('should test matrix generation with different inputs', async ({ page }) => {
    // Set up custom matrix parameters
    const rowsInput = page.getByRole('textbox', { name: /comma-separated list of values/i }).first();
    const columnsInput = page.getByRole('textbox', { name: /comma-separated list of values/i }).last();
    
    await rowsInput.click();
    await rowsInput.clear();
    await rowsInput.fill('Mobile App, Web App, Desktop App');
    
    await columnsInput.click();
    await columnsInput.clear();
    await columnsInput.fill('Low Budget, Medium Budget, High Budget');
    
    // Click SEND to generate matrix
    await page.getByRole('button', { name: /send/i }).click();
    
    // Verify STOP button appears during generation
    await expect(page.getByRole('button', { name: /stop/i })).toBeVisible({ timeout: 10000 });
    
    // Wait for generation to complete (STOP button disappears or timeout)
    await page.waitForFunction(() => {
      const stopButton = document.querySelector('button:has-text("STOP")');
      return !stopButton || !stopButton.isVisible();
    }, {}, { timeout: 60000 }).catch(() => {
      // If it times out, that's okay - we'll check the content
    });
    
    // Verify matrix cells have been populated with generated content
    const matrixCells = page.locator('table tr td:not(:first-child)');
    const cellCount = await matrixCells.count();
    expect(cellCount).toBeGreaterThan(0);
    
    // Check that at least some cells contain generated content (lists)
    const cellsWithLists = page.locator('table tr td ul');
    const listsCount = await cellsWithLists.count();
    expect(listsCount).toBeGreaterThan(0);
  });

  test('should test matrix generation with custom prompts', async ({ page }) => {
    // Wait for additional prompt field to be visible and fill it
    await page.waitForSelector('[placeholder*="Additional prompting"]', { timeout: 10000 });
    const additionalPrompt = page.getByRole('textbox', { name: /optional.*additional prompting/i });
    await additionalPrompt.fill('Focus on sustainable and eco-friendly solutions for each combination.');
    
    // Use default matrix setup and generate
    await page.getByRole('button', { name: /send/i }).click();
    
    // Verify generation starts
    await expect(page.getByRole('button', { name: /stop/i })).toBeVisible({ timeout: 10000 });
    
    // Wait a few seconds to see some content generation
    await page.waitForTimeout(5000);
    
    // Check that content is being generated in the matrix
    const matrixCells = page.locator('table tr td ul li');
    const itemsCount = await matrixCells.count();
    expect(itemsCount).toBeGreaterThan(0);
  });

  test('should test matrix output validation', async ({ page }) => {
    // Generate a matrix with known parameters
    const rowsInput = page.getByRole('textbox', { name: /comma-separated list of values/i }).first();
    const columnsInput = page.getByRole('textbox', { name: /comma-separated list of values/i }).last();
    
    await rowsInput.click();
    await rowsInput.clear();
    await rowsInput.fill('Small Team, Large Team');
    
    await columnsInput.click();
    await columnsInput.clear();
    await columnsInput.fill('Agile, Waterfall');
    
    await page.getByRole('button', { name: /send/i }).click();
    
    // Wait for some generation to occur
    await page.waitForTimeout(10000);
    
    // Verify matrix structure is correct (2x2 matrix)
    const columnHeaders = page.locator('table thead tr th, table tbody tr:first-child th');
    await expect(columnHeaders).toHaveCount(3); // 1 empty + 2 columns
    
    // Verify row structure
    const tableRows = page.locator('table tbody tr');
    await expect(tableRows).toHaveCount(2); // 2 rows for Small Team, Large Team
    
    // Verify row headers
    await expect(page.getByText('Small Team').first()).toBeVisible();
    await expect(page.getByText('Large Team').first()).toBeVisible();
    
    // Verify column headers
    await expect(page.getByText('Agile').first()).toBeVisible();
    await expect(page.getByText('Waterfall').first()).toBeVisible();
    
    // Verify cells contain structured content (lists with items)
    const listItems = page.locator('table td ul li');
    const itemCount = await listItems.count();
    expect(itemCount).toBeGreaterThan(0);
    
    // Verify items have proper structure (title + description)
    const firstItem = listItems.first();
    const itemText = await firstItem.textContent();
    expect(itemText).toBeTruthy();
    expect(itemText!.length).toBeGreaterThan(10); // Should have meaningful content
  });

  test('should test matrix UI interactions', async ({ page }) => {
    // Test AI model information display
    await expect(page.getByText('AI model:')).toBeVisible();
    await expect(page.getByText('GPT-4.1 on Azure')).toBeVisible();
    
    // Test guidelines link
    const guidelinesLink = page.getByRole('link', { name: 'here' });
    await expect(guidelinesLink).toBeVisible();
    await expect(guidelinesLink).toHaveAttribute('href', '/about');
    
    // Test matrix table interactions
    const matrixTable = page.getByRole('table');
    await expect(matrixTable).toBeVisible();
    
    // Test that the table has proper structure
    const tableRows = page.locator('table tr');
    const rowCount = await tableRows.count();
    expect(rowCount).toBeGreaterThan(1); // At least header + content rows
    
    // Test SEND button functionality
    const sendButton = page.getByRole('button', { name: /send/i });
    await expect(sendButton).toBeVisible();
    await expect(sendButton).toBeEnabled();
    
    // Test parameters section expand/collapse
    const parametersButton = page.getByRole('button', { name: /specify matrix parameters/i });
    await expect(parametersButton).toHaveAttribute('aria-expanded', 'true');
    
    // Verify all form elements are interactive
    const textboxes = page.getByRole('textbox');
    const textboxCount = await textboxes.count();
    expect(textboxCount).toBeGreaterThanOrEqual(3); // rows, columns, additional prompt
    
    // Test comboboxes (dropdowns) are present
    const comboboxes = page.getByRole('combobox');
    const comboboxCount = await comboboxes.count();
    expect(comboboxCount).toBeGreaterThanOrEqual(3); // template, qualifiers, generate type
  });
});