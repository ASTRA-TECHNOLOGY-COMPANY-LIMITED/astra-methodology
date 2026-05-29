#!/usr/bin/env bash
# ASTRA /uat-parallel — merge per-case JSON into index.html + issues.md + session.json
# Usage: uat-parallel-report.sh <SESSION_DIR> <REPORT_TEMPLATE_HTML>
set -euo pipefail

SESSION_DIR="${1:?SESSION_DIR required}"
TEMPLATE="${2:?TEMPLATE path required}"
RESULTS_DIR="$SESSION_DIR/raw/results"

if [ ! -d "$RESULTS_DIR" ]; then
  echo "[uat-parallel] No results in $RESULTS_DIR — nothing to merge." >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "[uat-parallel] node is required to merge results." >&2
  exit 2
fi

node - "$SESSION_DIR" "$TEMPLATE" "$RESULTS_DIR" <<'NODE'
const fs = require('fs');
const path = require('path');

const [SESSION_DIR, TEMPLATE, RESULTS_DIR] = process.argv.slice(2);

// 1. Load all per-case results
const cases = fs
  .readdirSync(RESULTS_DIR)
  .filter((f) => f.endsWith('.json'))
  .sort()
  .map((f) => JSON.parse(fs.readFileSync(path.join(RESULTS_DIR, f), 'utf8')));

if (cases.length === 0) {
  console.error('[uat-parallel] No case results found.');
  process.exit(0);
}

// 2. Aggregate
const startedAt = cases.map((c) => c.started_at).sort()[0];
const finishedAt = cases.map((c) => c.finished_at).sort().slice(-1)[0];
const passCount = cases.filter((c) => c.status === 'pass').length;
const failCount = cases.filter((c) => c.status === 'fail').length;
const durationMs = new Date(finishedAt).getTime() - new Date(startedAt).getTime();
const sessionId = path.basename(SESSION_DIR.replace(/\/$/, ''));

const sevCount = { critical: 0, high: 0, medium: 0, low: 0 };
const issues = [];
for (const c of cases) {
  if (c.status !== 'fail' || !c.first_failure) continue;
  const sev = c.first_failure.severity || 'low';
  sevCount[sev] = (sevCount[sev] || 0) + 1;
  issues.push({
    case_id: c.id,
    case_name: c.name,
    step_num: c.first_failure.step?.num ?? '?',
    step_total: c.steps.length,
    step_name: c.first_failure.step?.name ?? '(action error)',
    severity: sev,
    reason: c.first_failure.reason,
    expected: c.first_failure.assertion?.text || c.first_failure.step?.action_error || '',
    actual: c.first_failure.assertion?.actual || c.first_failure.step?.action_error || '',
    screenshot: c.first_failure.step?.screenshot || '',
    trace_hint: `npx playwright show-trace ./traces/${c.id}.zip`,
  });
}

// 3. Render HTML cases
function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function renderCase(c) {
  const stepsHtml = c.steps
    .map((s) => {
      const cls = s.status === 'fail' ? 'fail' : '';
      const asserts = (s.assertions || [])
        .map((a) => `<li class="${a.ok ? 'ok' : 'ng'}">${esc(a.text)}${!a.ok && a.actual ? ` <code>(actual: ${esc(a.actual).slice(0, 80)})</code>` : ''}</li>`)
        .join('');
      const sevBadge =
        s.status === 'fail' && c.first_failure
          ? `<span class="severity ${c.first_failure.severity}">${c.first_failure.severity.toUpperCase()}</span>`
          : '';
      const shot = s.screenshot ? `<div class="thumb"><a href="./${s.screenshot}" target="_blank"><img src="./${s.screenshot}" alt="step ${s.num}"></a></div>` : '';
      return `
      <div class="step ${cls}">
        <div class="num">${s.num}</div>
        <div class="body">
          <div class="title">${esc(s.name)}${sevBadge}</div>
          <div class="action">${esc(s.action)}</div>
          <div class="asserts"><ul>${asserts || '<li class="ok">(no assertions)</li>'}</ul></div>
        </div>
        ${shot}
      </div>`;
    })
    .join('');
  const statusClass = c.status === 'pass' ? 'pass' : 'fail';
  return `
  <div class="tc">
    <div class="tc-head">
      <div><span class="id">${esc(c.id)}</span><span class="name">${esc(c.name)}</span></div>
      <span class="tc-status ${statusClass}">${c.status.toUpperCase()}</span>
    </div>
    <div class="steps">${stepsHtml}</div>
  </div>`;
}

const testCasesHtml = cases.map(renderCase).join('\n');

const issuesHtml =
  failCount === 0
    ? `<div class="empty"><div class="icon">🎉</div>Không có lỗi nào trong session này.</div>`
    : `<p>Xem chi tiết tại <a href="./issues.md">issues.md</a> (${failCount} lỗi: ${sevCount.critical} CRITICAL, ${sevCount.high} HIGH, ${sevCount.medium} MEDIUM, ${sevCount.low} LOW)</p>`;

// 4. Render HTML report
const tpl = fs.readFileSync(TEMPLATE, 'utf8');
const html = tpl
  .replace(/\{\{SESSION_ID\}\}/g, sessionId)
  .replace(/\{\{STARTED_AT\}\}/g, startedAt)
  .replace(/\{\{FINISHED_AT\}\}/g, finishedAt)
  .replace(/\{\{MODE\}\}/g, `auto-parallel (${process.env.UAT_WORKERS || '?'} workers)`)
  .replace(/\{\{TOTAL_CASES\}\}/g, String(cases.length))
  .replace(/\{\{PASS_COUNT\}\}/g, String(passCount))
  .replace(/\{\{FAIL_COUNT\}\}/g, String(failCount))
  .replace(/\{\{DURATION\}\}/g, `${(durationMs / 1000).toFixed(1)}s`)
  .replace(/\{\{TEST_CASES_HTML\}\}/g, testCasesHtml)
  .replace(/\{\{ISSUES_HTML\}\}/g, issuesHtml);

fs.writeFileSync(path.join(SESSION_DIR, 'index.html'), html);

// 5. Render issues.md
if (failCount > 0) {
  const lines = [
    `# UAT Issues Report (parallel)`,
    `**Session**: ${sessionId}`,
    `**Test Cases chạy**: ${cases.length}`,
    `**Tổng số lỗi**: ${failCount} (${sevCount.critical} CRITICAL, ${sevCount.high} HIGH, ${sevCount.medium} MEDIUM, ${sevCount.low} LOW)`,
    ``,
    `---`,
    ``,
  ];
  issues.forEach((iss, idx) => {
    lines.push(`## Issue #${idx + 1} — ${iss.severity.toUpperCase()}`);
    lines.push(`**Test Case**: ${iss.case_id} - ${iss.case_name}`);
    lines.push(`**Bước**: ${iss.step_num}/${iss.step_total} — ${iss.step_name}`);
    lines.push(``);
    lines.push(`### Expected`);
    lines.push(`- ${iss.expected || '(action execution)'}`);
    lines.push(``);
    lines.push(`### Actual`);
    lines.push(`- ${iss.actual || '(no detail)'}`);
    lines.push(``);
    lines.push(`### Lý do gán ${iss.severity.toUpperCase()}`);
    lines.push(iss.reason || '(no rationale)');
    lines.push(``);
    if (iss.screenshot) {
      lines.push(`### Screenshot`);
      lines.push(`![${iss.case_id} step ${iss.step_num}](./${iss.screenshot})`);
      lines.push(``);
    }
    lines.push(`### Trace (Playwright)`);
    lines.push('```bash');
    lines.push(iss.trace_hint);
    lines.push('```');
    lines.push(``);
    lines.push(`---`);
    lines.push(``);
  });
  fs.writeFileSync(path.join(SESSION_DIR, 'issues.md'), lines.join('\n'));
}

// 6. Consolidated session.json
const session = {
  session_id: sessionId,
  mode: 'auto-parallel',
  started_at: startedAt,
  finished_at: finishedAt,
  duration_ms: durationMs,
  summary: {
    total: cases.length,
    pass: passCount,
    fail: failCount,
    severity: sevCount,
  },
  cases: cases.map((c) => ({
    id: c.id,
    name: c.name,
    status: c.status,
    duration_ms: c.duration_ms,
    worker_index: c.worker_index,
  })),
  issues,
};
fs.writeFileSync(path.join(SESSION_DIR, 'session.json'), JSON.stringify(session, null, 2));

// 7. Cleanup raw/ on success
fs.rmSync(path.join(SESSION_DIR, 'raw'), { recursive: true, force: true });

console.log(`[uat-parallel] Merged ${cases.length} cases → ${SESSION_DIR}/index.html`);
NODE
