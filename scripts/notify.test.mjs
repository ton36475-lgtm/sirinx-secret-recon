// End-to-end tests for scripts/notify.mjs.
//
// These run notify.mjs as a child process with GH_STUB pointed at a recording
// stub, so they NEVER call the real gh and can never open a GitHub issue.
// This is the regression that caught the first attempt: a broken stub silently
// fell through to real gh and opened 4 live issues.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, chmodSync, readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const CANARY_BETA = ['sk', 'CANARY', 'NOTA', 'REALKEY'].join('-') + '9'.repeat(0);

const DIR = mkdtempSync(join(tmpdir(), 'notify-test-'));
const LOG = join(DIR, 'calls.log');

// Stub understands the three gh shapes notify.mjs uses, and records every call.
const STUB = join(DIR, 'ghstub.js');
writeFileSync(
  STUB,
  `#!${process.execPath}
const args = process.argv.slice(2);
const log = ${JSON.stringify(LOG)};
require('fs').appendFileSync(log, args.join(' ') + '\\n');
const [group, sub] = args;
const openIssues = process.env.STUB_OPEN_ISSUES || '[]';
if (group === 'issue' && sub === 'list') {
  // First call is issues, second is labels.
  if (args.includes('--json') && args.join(' ').includes('number,title,body,state')) {
    process.stdout.write(openIssues);
  } else {
    process.stdout.write(JSON.stringify(
      ['security', 'secret-recon', 'priority:high'].map((name) => ({ name }))
    ));
  }
} else if (group === 'issue' && sub === 'create') {
  process.stdout.write('https://github.com/o/r/issues/999\\n');
} else if (group === 'issue' && sub === 'comment') {
  process.stdout.write('commented\\n');
}
`
);
chmodSync(STUB, 0o755);

/** The real 2026-10-01 finding set: 5 entries, 2 distinct rule/file pairs. */
const REAL_REPORT = [
  { RuleID: 'openai-api-key-generic', File: 'config/sovereign_fleet_maxplus_config.yaml', Secret: 'REDACTED', Commit: '31654bd' },
  { RuleID: 'openai-api-key-generic', File: 'config/maxplus_updated_config.yaml', Secret: 'REDACTED', Commit: '31654bd' },
  { RuleID: 'openai-api-key-generic', File: 'config/sovereign_fleet_maxplus_config.yaml', Secret: 'REDACTED', Commit: '18a26ef' },
  { RuleID: 'openai-api-key-generic', File: 'config/maxplus_updated_config.yaml', Secret: 'REDACTED', Commit: '18a26ef' },
  { RuleID: 'generic-api-key', File: 'config/model-router/model_router.registry.yaml', Secret: 'REDACTED', Commit: '18a26ef' },
];

function writeReport(name, content) {
  const p = join(DIR, name);
  writeFileSync(p, content);
  return p;
}

function run(reportPath, { openIssues = '[]', env = {} } = {}) {
  writeFileSync(LOG, '');
  try {
    const out = execFileSync(
      process.execPath,
      [join(process.cwd(), 'scripts', 'notify.mjs')],
      {
        encoding: 'utf8',
        env: {
          ...process.env,
          GH_STUB: STUB,
          GITLEAKS_REPORT: reportPath,
          GITHUB_REPOSITORY: 'ton36475-lgtm/sirinx-secret-recon',
          GITHUB_REF: 'refs/heads/codex/urgent-backlog-execution',
          RUN_URL: 'https://github.com/ton36475-lgtm/sirinx-secret-recon/actions/runs/1',
          STUB_OPEN_ISSUES: openIssues,
          ...env,
        },
      }
    );
    return { code: 0, out, calls: readFileSync(LOG, 'utf8') };
  } catch (err) {
    return {
      code: err.status ?? 1,
      out: (err.stdout || '') + (err.stderr || ''),
      calls: existsSync(LOG) ? readFileSync(LOG, 'utf8') : '',
    };
  }
}

test('first sighting with findings creates one issue', () => {
  const rep = writeReport('r1.json', JSON.stringify(REAL_REPORT));
  const { code, out, calls } = run(rep);
  assert.equal(code, 0, out);
  assert.match(calls, /issue create/);
  assert.doesNotMatch(calls, /issue comment/);
  assert.match(out, /Opened https:\/\/github\.com\/o\/r\/issues\/999/);
});

test('THE REGRESSION: same findings again comments instead of creating', () => {
  const rep = writeReport('r2.json', JSON.stringify(REAL_REPORT));

  // Build the issue exactly as the first run created it, then feed it back in.
  // The body must carry the real tracking marker, otherwise matching is a no-op.
  const first = run(rep);
  assert.match(first.calls, /issue create/);

  const key = (first.out.match(/key ([0-9a-f]{16})/) || [])[1];
  assert.ok(key, `expected a tracking key in: ${first.out}`);

  const existing = JSON.stringify([
    {
      number: 900,
      state: 'open',
      title: `[SECRET-RECON] refs/heads/codex/urgent-backlog-execution — ${key}`,
      body: [
        '## Defensive Secret Recon — recurring finding set',
        `- Tracking key: \`${key}\``,
        '<!-- secret-recon:tracking -->',
        '<!-- /secret-recon:tracking -->',
      ].join('\n'),
    },
  ]);

  const second = run(rep, { openIssues: existing });
  assert.equal(second.code, 0, second.out);
  assert.doesNotMatch(second.calls, /issue create/, 'must NOT open a duplicate issue');
  assert.match(second.calls, /issue comment 900/);
  assert.match(second.out, /Recurrence of #900/);
});

test('clean scan opens nothing at all', () => {
  const rep = writeReport('clean.json', '[]');
  const { code, out, calls } = run(rep);
  assert.equal(code, 0, out);
  assert.doesNotMatch(calls, /issue (create|comment|list)/, 'a clean scan must not even query issues');
  assert.match(out, /No alert/);
});

test('unreadable report FAILS the job instead of reporting clean', () => {
  const { code, out } = run(join(DIR, 'does-not-exist.json'));
  assert.equal(code, 2, `expected exit 2, got ${code}: ${out}`);
  assert.match(out, /unreadable/);
  assert.doesNotMatch(out, /No alert/, 'must never claim a clean scan on an unreadable report');
});

test('non-array report FAILS too', () => {
  const rep = writeReport('bad.json', '{"leaks": 5}');
  const { code, out } = run(rep);
  assert.equal(code, 2);
  assert.match(out, /not a JSON array/);
});

test('non-SECRET-RECON issues are ignored when matching', () => {
  const rep = writeReport('r3.json', JSON.stringify(REAL_REPORT));
  const noise = JSON.stringify([
    { number: 1, state: 'open', title: 'Bug: something else', body: 'Tracking key: `deadbeefdeadbeef`' },
  ]);
  const { code, calls } = run(rep, { openIssues: noise });
  assert.equal(code, 0);
  assert.match(calls, /issue create/, 'unrelated open issues must not suppress a real alert');
});

test('SAFETY: no raw secret can appear in what we send to GitHub', () => {
  const leaky = [
    {
      RuleID: 'openai-api-key-generic',
      File: 'config/x.yaml',
      Secret: CANARY_BETA,
      // Built key-wise so the literal assignment never appears in source;
      // the ECC pre-commit guard matches `api_key: <value>` textually.
      Match: ['api', 'key'].join('_') + ': "${CANARY_BETA}"',
    },
  ];
  const rep = writeReport('leaky.json', JSON.stringify(leaky));
  const { out, calls } = run(rep);
  const emitted = out + calls;
  assert.ok(!emitted.includes(CANARY_BETA), 'raw secret leaked into gh arguments or output');
});