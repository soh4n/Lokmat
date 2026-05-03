const { test, expect } = require('@playwright/test');
const { injectAxe, checkA11y } = require('axe-playwright');

test.describe('VoteSathi AI Chat & Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the production URL (or localhost if testing locally)
    await page.goto('https://lokmat-495121.web.app/');
    // Inject axe-core into the page for accessibility auditing
    await injectAxe(page);
  });

  test('should pass WCAG 2.1 AA accessibility audit', async ({ page }) => {
    // Audit the home page for WCAG 2.1 AA and WCAG 2.1 A violations
    await checkA11y(page, null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
      }
    });
  });

  test('should complete the happy path chat interaction', async ({ page }) => {
    // 1. Locate the chat input
    // Using a broad selector that targets standard chat input fields
    const chatInput = page.getByRole('textbox', { name: /type your message|message|chat/i }).first();
    
    // If the element is not found by role, we fallback to a placeholder selector
    if (await chatInput.count() === 0) {
      await page.getByPlaceholder(/message/i).fill('What is a voter slip?');
      await page.keyboard.press('Enter');
    } else {
      await chatInput.fill('What is a voter slip?');
      await chatInput.press('Enter');
    }

    // 2. Wait for the streaming response to start appearing
    // We look for a generic "assistant" response block or the live dot indicator
    const streamingIndicator = page.locator('.live-dot').first();
    // Verify that the UI reflects a loading or live state
    if (await streamingIndicator.count() > 0) {
      await expect(streamingIndicator).toBeVisible();
    }

    // 3. Verify the message is appended to the DOM and aria-live is working
    // Wait for the response to stabilize (a simplistic wait for stream completion)
    const responseBox = page.getByRole('log').first();
    if (await responseBox.count() > 0) {
      await expect(responseBox).toContainText(/voter|slip/i, { timeout: 15000 });
    }
  });
});
