/**
 * ASTRA /uat-parallel — UAT Runner
 * Reads UAT case .md files (YAML frontmatter + Markdown), dispatches each
 * case as a Playwright test running in its own isolated BrowserContext.
 * Managed file. Overwritten on every /uat-parallel run from the plugin.
 */
import { test, expect, Page, Request, Response } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// ────────────────────────────────────────────────────────────────────────────
// Configuration via env (set by the skill)
// ────────────────────────────────────────────────────────────────────────────
const SESSION_DIR = process.env.UAT_SESSION_DIR!;
const CASES_GLOB = process.env.UAT_CASES_GLOB || 'docs/tests/uat-cases/*.md';
const FILTER_PRIORITY = (process.env.UAT_FILTER_PRIORITY || '').trim();
const FILTER_FEATURE = (process.env.UAT_FILTER_FEATURE || '').trim();
const PROJECT_ROOT = process.env.UAT_PROJECT_ROOT || process.cwd();

// ────────────────────────────────────────────────────────────────────────────
// Types
// ────────────────────────────────────────────────────────────────────────────
type Frontmatter = {
  id: string;
  name: string;
  priority?: 'critical' | 'high' | 'medium' | 'low';
  feature?: string;
  base_url?: string;
  created?: string;
};
type Step = { num: number; name: string; action: string; expected: string[] };
type Case = { file: string; meta: Frontmatter; steps: Step[] };

type NetworkEntry = { method: string; url: string; status: number; ts: number };
type ConsoleEntry = { level: string; text: string; ts: number };

// ────────────────────────────────────────────────────────────────────────────
// Case loader
// ────────────────────────────────────────────────────────────────────────────
function globSync(pattern: string): string[] {
  // Minimal glob: support `dir/*.md` and a single absolute/relative path.
  const abs = path.isAbsolute(pattern) ? pattern : path.join(PROJECT_ROOT, pattern);
  if (!abs.includes('*')) {
    return fs.existsSync(abs) ? [abs] : [];
  }
  const dir = path.dirname(abs);
  const ext = path.extname(abs);
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(ext))
    .map((f) => path.join(dir, f))
    .sort();
}

function parseFrontmatter(raw: string): { meta: Frontmatter; body: string } {
  const m = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!m) throw new Error('Missing YAML frontmatter');
  const meta: any = {};
  for (const line of m[1].split('\n')) {
    const kv = line.match(/^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$/);
    if (!kv) continue;
    meta[kv[1]] = kv[2].trim().replace(/^["'`]|["'`]$/g, '');
  }
  if (!meta.id || !meta.name) throw new Error('Frontmatter requires id and name');
  return { meta, body: m[2] };
}

function parseSteps(body: string, baseUrl?: string): Step[] {
  // Each step starts with `## Bước N: name` (or `## Step N: name`)
  const stepRegex = /^##\s+(?:Bước|Step)\s+(\d+)\s*:\s*(.+)$/gm;
  const matches = [...body.matchAll(stepRegex)];
  const steps: Step[] = [];
  for (let i = 0; i < matches.length; i++) {
    const m = matches[i];
    const start = m.index! + m[0].length;
    const end = i + 1 < matches.length ? matches[i + 1].index! : body.length;
    const block = body.slice(start, end);
    const actionMatch = block.match(/\*\*Action\*\*\s*:\s*(.+)/);
    if (!actionMatch) continue;
    let action = actionMatch[1].trim();
    if (baseUrl) action = action.replace(/\{base_url\}/g, baseUrl);
    const expectedBlock = block.match(/\*\*Expected\*\*\s*:\s*\n([\s\S]*?)(\n\s*\n|$)/);
    const expected: string[] = [];
    if (expectedBlock) {
      for (const line of expectedBlock[1].split('\n')) {
        const a = line.match(/^\s*[-*]\s+(.+)$/);
        if (a) expected.push(a[1].trim());
      }
    }
    steps.push({
      num: Number(m[1]),
      name: m[2].trim(),
      action,
      expected,
    });
  }
  return steps;
}

function loadCases(): Case[] {
  const files = globSync(CASES_GLOB);
  const cases: Case[] = [];
  for (const f of files) {
    try {
      const raw = fs.readFileSync(f, 'utf8');
      const { meta, body } = parseFrontmatter(raw);
      if (FILTER_PRIORITY && meta.priority !== FILTER_PRIORITY) continue;
      if (FILTER_FEATURE && meta.feature !== FILTER_FEATURE) continue;
      const steps = parseSteps(body, meta.base_url);
      cases.push({ file: f, meta, steps });
    } catch (e: any) {
      console.error(`[uat-parallel] Skip ${f}: ${e.message}`);
    }
  }
  return cases;
}

// ────────────────────────────────────────────────────────────────────────────
// Action dispatcher
// ────────────────────────────────────────────────────────────────────────────
function stripBackticks(s: string): string {
  return s.replace(/^`|`$/g, '');
}

function unquote(s: string): string {
  return s.replace(/^["'`]|["'`]$/g, '');
}

async function executeAction(page: Page, action: string): Promise<void> {
  const stamped = action.replace(/\{timestamp\}/g, String(Date.now()));
  const verbMatch = stamped.match(/^(\w+)\s+(.*)$/);
  if (!verbMatch) throw new Error(`Cannot parse action: ${action}`);
  const verb = verbMatch[1].toLowerCase();
  const rest = verbMatch[2];

  switch (verb) {
    case 'navigate': {
      const url = stripBackticks(rest.trim());
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      return;
    }
    case 'click': {
      const sel = stripBackticks(rest.trim());
      await resolveLocator(page, sel).click();
      return;
    }
    case 'fill': {
      const m = rest.match(/^(.+?)\s+value=(.+)$/);
      if (!m) throw new Error(`fill expects "selector value=...": ${rest}`);
      const sel = stripBackticks(m[1].trim());
      const value = unquote(stripBackticks(m[2].trim()));
      await resolveLocator(page, sel).fill(value);
      return;
    }
    case 'wait': {
      const t = rest.trim();
      if (/^\d+$/.test(t)) {
        await page.waitForTimeout(Number(t));
      } else if (/^\d+m?s$/.test(t)) {
        const ms = t.endsWith('ms') ? Number(t.replace('ms', '')) : Number(t.replace('s', '')) * 1000;
        await page.waitForTimeout(ms);
      } else {
        await resolveLocator(page, stripBackticks(t)).waitFor();
      }
      return;
    }
    case 'press': {
      await page.keyboard.press(stripBackticks(rest.trim()));
      return;
    }
    case 'hover': {
      await resolveLocator(page, stripBackticks(rest.trim())).hover();
      return;
    }
    default:
      throw new Error(`Unknown action verb: ${verb}`);
  }
}

function resolveLocator(page: Page, selector: string) {
  // Support :has-text("...") syntactic sugar by mapping to Playwright's :has-text
  // (already supported natively, but normalize quotes).
  return page.locator(selector);
}

// ────────────────────────────────────────────────────────────────────────────
// Assertion verifier
// ────────────────────────────────────────────────────────────────────────────
type AssertResult = { text: string; ok: boolean; actual?: string };

async function verifyAssertion(
  page: Page,
  raw: string,
  network: NetworkEntry[],
  consoleLog: ConsoleEntry[],
  stepStartTs: number,
): Promise<AssertResult> {
  const text = raw.trim();
  const kindMatch = text.match(/^(url|network|dom|console)\s*:\s*(.+)$/i);
  if (!kindMatch) return { text, ok: false, actual: 'Cannot parse assertion' };
  const kind = kindMatch[1].toLowerCase();
  const body = kindMatch[2].trim();

  try {
    switch (kind) {
      case 'url':
        return await verifyUrl(page, body, text);
      case 'network':
        return verifyNetwork(network, body, text, stepStartTs);
      case 'dom':
        return await verifyDom(page, body, text);
      case 'console':
        return verifyConsole(consoleLog, body, text, stepStartTs);
      default:
        return { text, ok: false, actual: `Unknown kind: ${kind}` };
    }
  } catch (e: any) {
    return { text, ok: false, actual: e.message };
  }
}

async function verifyUrl(page: Page, body: string, original: string): Promise<AssertResult> {
  const href = page.url();
  let m;
  if ((m = body.match(/^equals\s+(.+)$/))) {
    const want = stripBackticks(m[1].trim());
    return { text: original, ok: href === want, actual: href };
  }
  if ((m = body.match(/^contains\s+(.+)$/))) {
    const sub = stripBackticks(m[1].trim());
    return { text: original, ok: href.includes(sub), actual: href };
  }
  if ((m = body.match(/^matches\s+(.+)$/))) {
    const re = new RegExp(stripBackticks(m[1].trim()));
    return { text: original, ok: re.test(href), actual: href };
  }
  if ((m = body.match(/^pathname\s+equals\s+(.+)$/))) {
    const want = stripBackticks(m[1].trim());
    const p = new URL(href).pathname;
    return { text: original, ok: p === want, actual: p };
  }
  return { text: original, ok: false, actual: `Unsupported url assertion: ${body}` };
}

function verifyNetwork(
  log: NetworkEntry[],
  body: string,
  original: string,
  since: number,
): AssertResult {
  const window = log.filter((e) => e.ts >= since);
  let m;
  if ((m = body.match(/^(GET|POST|PUT|DELETE|PATCH)\s+(\S+)\s*(?:→|->)\s*(\d+)$/i))) {
    const [, method, pathPat, status] = m;
    const hit = window.find(
      (e) => e.method.toUpperCase() === method.toUpperCase() && matchPath(e.url, stripBackticks(pathPat)),
    );
    if (!hit) return { text: original, ok: false, actual: `No ${method} ${pathPat} in window` };
    return { text: original, ok: hit.status === Number(status), actual: `${hit.status}` };
  }
  if (/^no\s+failed\s+requests$/i.test(body)) {
    const failed = window.filter((e) => e.status >= 400);
    return {
      text: original,
      ok: failed.length === 0,
      actual: failed.length === 0 ? 'none' : failed.map((f) => `${f.status} ${f.url}`).join(', '),
    };
  }
  return { text: original, ok: false, actual: `Unsupported network assertion: ${body}` };
}

function matchPath(url: string, pattern: string): boolean {
  try {
    const p = new URL(url).pathname;
    if (!pattern.includes('*')) return p === pattern || p.endsWith(pattern);
    const re = new RegExp('^' + pattern.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*') + '$');
    return re.test(p);
  } catch {
    return false;
  }
}

async function verifyDom(page: Page, body: string, original: string): Promise<AssertResult> {
  let m;
  if ((m = body.match(/^(.+?)\s+exists$/))) {
    const sel = stripBackticks(m[1].trim());
    const count = await page.locator(sel).count();
    return { text: original, ok: count > 0, actual: `count=${count}` };
  }
  if ((m = body.match(/^(.+?)\s+not\s+exists$/))) {
    const sel = stripBackticks(m[1].trim());
    const count = await page.locator(sel).count();
    return { text: original, ok: count === 0, actual: `count=${count}` };
  }
  if ((m = body.match(/^(.+?)\s+visible$/))) {
    const sel = stripBackticks(m[1].trim());
    const ok = await page.locator(sel).first().isVisible().catch(() => false);
    return { text: original, ok, actual: ok ? 'visible' : 'hidden/missing' };
  }
  if ((m = body.match(/^(.+?)\s+contains\s+"(.+)"$/))) {
    const sel = stripBackticks(m[1].trim());
    const want = m[2];
    const txt = (await page.locator(sel).first().textContent().catch(() => null)) || '';
    return { text: original, ok: txt.includes(want), actual: txt.slice(0, 120) };
  }
  if ((m = body.match(/^(.+?)\s+has\s+value\s+"(.+)"$/))) {
    const sel = stripBackticks(m[1].trim());
    const want = m[2];
    const val = await page.locator(sel).first().inputValue().catch(() => '');
    return { text: original, ok: val === want, actual: val };
  }
  if ((m = body.match(/^(.+?)\s+has\s+value\s+matching\s+(.+)$/))) {
    const sel = stripBackticks(m[1].trim());
    const re = new RegExp(stripBackticks(m[2].trim()));
    const val = await page.locator(sel).first().inputValue().catch(() => '');
    return { text: original, ok: re.test(val), actual: val };
  }
  if ((m = body.match(/^(.+?)\s+count\s*=\s*(\d+)$/))) {
    const sel = stripBackticks(m[1].trim());
    const want = Number(m[2]);
    const count = await page.locator(sel).count();
    return { text: original, ok: count === want, actual: `count=${count}` };
  }
  if ((m = body.match(/^text\s+"(.+)"\s+exists$/))) {
    const want = m[1];
    const ok = (await page.content()).includes(want);
    return { text: original, ok, actual: ok ? 'found' : 'not found' };
  }
  if ((m = body.match(/^title\s+contains\s+"(.+)"$/))) {
    const want = m[1];
    const t = await page.title();
    return { text: original, ok: t.includes(want), actual: t };
  }
  return { text: original, ok: false, actual: `Unsupported dom assertion: ${body}` };
}

function verifyConsole(
  log: ConsoleEntry[],
  body: string,
  original: string,
  since: number,
): AssertResult {
  const window = log.filter((e) => e.ts >= since);
  if (/^no\s+error$/i.test(body)) {
    const errs = window.filter((e) => e.level === 'error');
    return {
      text: original,
      ok: errs.length === 0,
      actual: errs.length === 0 ? 'none' : errs.map((e) => e.text).slice(0, 3).join(' | '),
    };
  }
  if (/^no\s+warning$/i.test(body)) {
    const ws = window.filter((e) => e.level === 'warning' || e.level === 'warn');
    return { text: original, ok: ws.length === 0, actual: ws.length === 0 ? 'none' : `${ws.length} warning(s)` };
  }
  let m;
  if ((m = body.match(/^contains\s+"(.+)"$/))) {
    const want = m[1];
    const hit = window.some((e) => e.text.includes(want));
    return { text: original, ok: hit, actual: hit ? 'found' : 'not found' };
  }
  return { text: original, ok: false, actual: `Unsupported console assertion: ${body}` };
}

// ────────────────────────────────────────────────────────────────────────────
// Severity assignment (mirrors user-test/references/assertion-guide.md §3)
// ────────────────────────────────────────────────────────────────────────────
function assignSeverity(failedAssertion: AssertResult, network: NetworkEntry[], consoleLog: ConsoleEntry[]): {
  severity: 'critical' | 'high' | 'medium' | 'low';
  reason: string;
} {
  const text = failedAssertion.text;
  const actual = failedAssertion.actual || '';

  // CRITICAL
  if (network.some((n) => n.status >= 500)) {
    const hit = network.find((n) => n.status >= 500)!;
    return { severity: 'critical', reason: `Network 5xx tại ${hit.url}. Theo rule: 5xx ⇒ CRITICAL.` };
  }
  if (consoleLog.some((c) => c.level === 'error' && /Uncaught/.test(c.text))) {
    return { severity: 'critical', reason: 'Uncaught error trên window. Theo rule: Uncaught ⇒ CRITICAL.' };
  }

  // HIGH
  if (/^network:\s+(POST|PUT|DELETE|PATCH)/i.test(text) && /4\d\d/.test(actual)) {
    return { severity: 'high', reason: '4xx trên endpoint primary (POST/PUT/DELETE). Theo rule: ⇒ HIGH.' };
  }
  if (/^url:/i.test(text) && (text.includes('contains') || text.includes('equals')) && actual.includes('/login')) {
    return { severity: 'high', reason: 'URL không đổi sau primary action. Theo rule: ⇒ HIGH.' };
  }
  if (network.some((n) => n.status === 401 || n.status === 403)) {
    return { severity: 'high', reason: 'Unexpected 401/403. Theo rule: auth-fail ⇒ HIGH.' };
  }

  // MEDIUM
  if (/^dom:.*exists$/i.test(text)) {
    return { severity: 'medium', reason: 'Element CTA/form/heading không tồn tại. Theo rule: ⇒ MEDIUM.' };
  }
  if (/^dom:.*contains/i.test(text)) {
    return { severity: 'medium', reason: 'Text không khớp expected (typo/mistranslation). Theo rule: ⇒ MEDIUM.' };
  }

  // LOW (default)
  return { severity: 'low', reason: 'Không khớp rule CRITICAL/HIGH/MEDIUM, gán LOW theo mặc định.' };
}

// ────────────────────────────────────────────────────────────────────────────
// Result writer (per-case JSON)
// ────────────────────────────────────────────────────────────────────────────
function writeCaseResult(caseId: string, payload: any): void {
  const dir = path.join(SESSION_DIR, 'raw', 'results');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, `${caseId}.json`), JSON.stringify(payload, null, 2));
}

// ────────────────────────────────────────────────────────────────────────────
// Test generation
// ────────────────────────────────────────────────────────────────────────────
const cases = loadCases();
if (cases.length === 0) {
  // Emit a placeholder so Playwright does not error out
  test('no cases matched filters', () => {
    test.skip();
  });
}

for (const c of cases) {
  test(`${c.meta.id} — ${c.meta.name}`, async ({ page }, testInfo) => {
    const network: NetworkEntry[] = [];
    const consoleLog: ConsoleEntry[] = [];
    page.on('response', (resp: Response) => {
      network.push({
        method: resp.request().method(),
        url: resp.url(),
        status: resp.status(),
        ts: Date.now(),
      });
    });
    page.on('console', (msg) => {
      consoleLog.push({ level: msg.type(), text: msg.text(), ts: Date.now() });
    });
    page.on('pageerror', (err) => {
      consoleLog.push({ level: 'error', text: `Uncaught ${err.message}`, ts: Date.now() });
    });

    const stepResults: any[] = [];
    const startedAt = new Date().toISOString();
    let caseStatus: 'pass' | 'fail' = 'pass';
    let firstFailure: any = null;

    const shotDir = path.join(SESSION_DIR, 'screenshots', c.meta.id);
    fs.mkdirSync(shotDir, { recursive: true });

    for (const step of c.steps) {
      const stepStartTs = Date.now();
      const padded = String(step.num).padStart(2, '0');
      const shotPath = path.join(shotDir, `step-${padded}.png`);
      const stepResult: any = {
        num: step.num,
        name: step.name,
        action: step.action,
        expected: step.expected,
        assertions: [],
        status: 'pass',
        screenshot: path.relative(SESSION_DIR, shotPath),
      };

      try {
        await executeAction(page, step.action);
      } catch (e: any) {
        stepResult.status = 'fail';
        stepResult.action_error = e.message;
        await page.screenshot({ path: shotPath, fullPage: false }).catch(() => {});
        stepResults.push(stepResult);
        caseStatus = 'fail';
        const sev = assignSeverity({ text: 'action', ok: false, actual: e.message }, network, consoleLog);
        firstFailure = { step: stepResult, ...sev };
        break;
      }

      await page.screenshot({ path: shotPath, fullPage: false }).catch(() => {});

      for (const a of step.expected) {
        const res = await verifyAssertion(page, a, network, consoleLog, stepStartTs);
        stepResult.assertions.push(res);
        if (!res.ok) {
          stepResult.status = 'fail';
          caseStatus = 'fail';
          if (!firstFailure) {
            const sev = assignSeverity(res, network, consoleLog);
            firstFailure = { step: stepResult, assertion: res, ...sev };
          }
        }
      }

      stepResults.push(stepResult);
      if (stepResult.status === 'fail') break;
    }

    const finishedAt = new Date().toISOString();
    writeCaseResult(c.meta.id, {
      id: c.meta.id,
      name: c.meta.name,
      file: path.relative(PROJECT_ROOT, c.file),
      priority: c.meta.priority || null,
      feature: c.meta.feature || null,
      status: caseStatus,
      started_at: startedAt,
      finished_at: finishedAt,
      duration_ms: new Date(finishedAt).getTime() - new Date(startedAt).getTime(),
      steps: stepResults,
      first_failure: firstFailure,
      worker_index: testInfo.workerIndex,
    });

    expect(caseStatus, firstFailure ? `${firstFailure.severity}: ${firstFailure.reason}` : 'ok').toBe('pass');
  });
}
