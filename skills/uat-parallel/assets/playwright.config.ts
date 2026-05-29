/**
 * ASTRA /uat-parallel — Playwright config
 * Managed file. Overwritten on every /uat-parallel run from the plugin.
 * Do not hand-edit; edits will be lost.
 */
import { defineConfig } from '@playwright/test';
import * as path from 'path';

const SESSION_DIR = process.env.UAT_SESSION_DIR;
if (!SESSION_DIR) {
  throw new Error('UAT_SESSION_DIR is required (set by /uat-parallel skill)');
}

const STEP_TIMEOUT_MS = Number(process.env.UAT_STEP_TIMEOUT_MS || 30_000);
const CASE_TIMEOUT_MS = Number(process.env.UAT_CASE_TIMEOUT_MS || 300_000);

export default defineConfig({
  testDir: __dirname,
  testMatch: /uat-runner\.spec\.ts$/,
  fullyParallel: true,
  forbidOnly: false,
  retries: 0,
  timeout: CASE_TIMEOUT_MS,
  expect: { timeout: STEP_TIMEOUT_MS },
  reporter: [
    ['list'],
    ['json', { outputFile: path.join(SESSION_DIR, 'raw', 'playwright-report.json') }],
  ],
  outputDir: path.join(SESSION_DIR, 'raw', 'test-output'),
  use: {
    actionTimeout: STEP_TIMEOUT_MS,
    navigationTimeout: STEP_TIMEOUT_MS,
    trace: 'retain-on-failure',
    screenshot: 'off',
    video: 'off',
  },
});
