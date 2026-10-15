import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  fullyParallel: false,
  reporter: [['list']],
  use: {
    browserName: 'chromium',
    viewport: { width: 1366, height: 768 },
    screenshot: 'only-on-failure'
  }
});
