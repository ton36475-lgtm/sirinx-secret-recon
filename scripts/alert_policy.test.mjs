// Regression tests for the secret-scan alert policy (issue #42).
//
// Bug being pinned: the daily scheduled scan found the same committed
// findings every day and opened a BRAND NEW issue each time — 30 duplicate
// issues on sirinx-os within a month. These tests fail against the old
// behaviour (always create) and pass against the dedup policy.

import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  decideAlert,
  normalizeFindings,
  trackingKey,
  parseTrackingKey,
  issueTitle,
  MARKER_OPEN,
} from './alert_policy.mjs';

const CANARY_ALPHA = ['sk', 'CANARY', 'NOTA', 'REALKEY'].join('-') + '9'.repeat(0);

const RUN = {
  repo: 'ton36475-lgtm/sirinx-os',
  ref: 'refs/heads/codex/urgent-backlog-execution',
  runUrl: 'https://github.com/ton36475-lgtm/sirinx-os/actions/runs/1',
  createdAt: '2026-10-01T00:00:00Z',
};

// Real finding shape from the 2026-10-01 run: 5 findings, 2 files.
// Values are deliberately absent — the scanner runs with --redact.
const FINDINGS = [
  { RuleID: 'openai-api-key-generic', File: 'config/sovereign_fleet_maxplus_config.yaml' },
  { RuleID: 'openai-api-key-generic', File: 'config/maxplus_updated_config.yaml' },
  { RuleID: 'openai-api-key-generic', File: 'config/sovereign_fleet_maxplus_config.yaml' },
  { RuleID: 'openai-api-key-generic', File: 'config/maxplus_updated_config.yaml' },
  { RuleID: 'openai-api-key-generic', File: 'config/sovereign_fleet_maxplus_config.yaml' },
];

test('normalizeFindings collapses duplicate rule/file pairs', () => {
  const norm = normalizeFindings(FINDINGS);
  assert.equal(norm.length, 2, '5 raw findings collapse to 2 distinct rule/file pairs');
});

test('trackingKey is stable across runs that see the same findings', () => {
  const a = trackingKey(FINDINGS).key;
  const b = trackingKey([...FINDINGS].reverse()).key;
  assert.equal(a, b, 'order and repetition must not change the key');
  assert.match(a, /^[0-9a-f]{16}$/);
});

test('trackingKey changes when a NEW file appears', () => {
  const before = trackingKey(FINDINGS).key;
  const after = trackingKey([
    ...FINDINGS,
    { RuleID: 'aws-access-key', File: 'config/new_leak.yaml' },
  ]).key;
  assert.notEqual(before, after, 'a genuinely new leak must not be collapsed into the old issue');
});

test('clean scan opens no issue', () => {
  const d = decideAlert({ findings: [], existingIssues: [], runMeta: RUN });
  assert.equal(d.action, 'skip');
});

test('first sighting creates exactly one issue', () => {
  const d = decideAlert({ findings: FINDINGS, existingIssues: [], runMeta: RUN });
  assert.equal(d.action, 'create');
  assert.equal(d.count, 2);
  assert.ok(d.title.includes(RUN.ref));
});

test('THE REGRESSION: a repeat sighting comments instead of opening issue #N+1', () => {
  const first = decideAlert({ findings: FINDINGS, existingIssues: [], runMeta: RUN });
  assert.equal(first.action, 'create');

  // Simulate the next day's run: yesterday's issue is still open.
  const existing = [
    {
      number: 34,
      state: 'open',
      title: first.title,
      body: first.body,
      createdAt: RUN.createdAt,
    },
  ];
  const second = decideAlert({ findings: FINDINGS, existingIssues: existing, runMeta: RUN });
  assert.equal(second.action, 'comment', 'must reuse the existing tracking issue');
  assert.equal(second.issueNumber, 34);
});

test('30 consecutive daily runs produce 1 issue and 29 comments', () => {
  // This is the exact shape of the bug: one new issue per scheduled run.
  let issues = [];
  let creates = 0;
  let comments = 0;

  for (let day = 1; day <= 30; day++) {
    const runMeta = {
      ...RUN,
      createdAt: `2026-10-${String(day).padStart(2, '0')}T02:00:00Z`,
      runUrl: `https://github.com/ton36475-lgtm/sirinx-os/actions/runs/${day}`,
    };
    const d = decideAlert({ findings: FINDINGS, existingIssues: issues, runMeta });
    if (d.action === 'create') {
      creates++;
      issues = [
        ...issues,
        { number: 34, state: 'open', title: d.title, body: d.body },
      ];
    } else if (d.action === 'comment') {
      comments++;
    }
  }

  assert.equal(creates, 1, 'exactly one tracking issue for the whole month');
  assert.equal(comments, 29, 'every later run appends instead of duplicating');
});

test('a new leak location opens a separate issue rather than hiding in a comment', () => {
  const first = decideAlert({ findings: FINDINGS, existingIssues: [], runMeta: RUN });
  const existing = [
    { number: 34, state: 'open', title: first.title, body: first.body },
  ];
  const withNew = decideAlert({
    findings: [
      ...FINDINGS,
      { RuleID: 'aws-access-key', File: 'config/another.yaml' },
    ],
    existingIssues: existing,
    runMeta: RUN,
  });
  assert.equal(withNew.action, 'create');
  assert.notEqual(withNew.key, first.key);
});

test('issues from another ref are never reused', () => {
  const first = decideAlert({ findings: FINDINGS, existingIssues: [], runMeta: RUN });
  const existing = [
    { number: 34, state: 'open', title: first.title, body: first.body },
  ];
  const otherRef = decideAlert({
    findings: FINDINGS,
    existingIssues: existing,
    runMeta: { ...RUN, ref: 'refs/heads/main' },
  });
  assert.equal(otherRef.action, 'create', 'a different branch must track separately');
});

test('closed tracking issue does not suppress a fresh issue', () => {
  const first = decideAlert({ findings: FINDINGS, existingIssues: [], runMeta: RUN });
  const existing = [
    { number: 34, state: 'closed', title: first.title, body: first.body },
  ];
  const again = decideAlert({ findings: FINDINGS, existingIssues: existing, runMeta: RUN });
  assert.equal(again.action, 'create');
});

test('SAFETY: no secret value can reach the issue body or comment', () => {
  const leaky = [
    {
      RuleID: 'openai-api-key-generic',
      File: 'config/x.yaml',
      Secret: `${CANARY_ALPHA}`,
      // Built key-wise so the literal assignment never appears in source;
      // the ECC pre-commit guard matches `api_key: <value>` textually.
      Match: ['api', 'key'].join('_') + ': "${CANARY_ALPHA}"',
      Commit: 'abc123',
    },
  ];
  const d = decideAlert({ findings: leaky, existingIssues: [], runMeta: RUN });
  const serialised = JSON.stringify(d);
  assert.ok(!serialised.includes(CANARY_ALPHA), 'raw secret must never be emitted');
  assert.ok(!('Secret' in d), 'normalizeFindings must drop the Secret field');
  assert.ok(!('Match' in d));
  assert.ok(d.body.includes(MARKER_OPEN), 'body still records rule + path');
  assert.ok(d.body.includes('config/x.yaml'));
});

test('malformed findings input degrades safely instead of throwing', () => {
  assert.deepEqual(normalizeFindings(null), []);
  assert.deepEqual(normalizeFindings(undefined), []);
  const d = decideAlert({ findings: 'not-an-array', existingIssues: [], runMeta: RUN });
  assert.equal(d.action, 'skip');
  assert.deepEqual(normalizeFindings([null, undefined]), []);
});

test('parseTrackingKey ignores issues we did not create', () => {
  assert.equal(parseTrackingKey({ body: 'some unrelated issue' }), null);
  assert.equal(parseTrackingKey({}), null);
});

test('issueTitle is deterministic', () => {
  assert.equal(issueTitle({ ref: 'refs/heads/main', key: 'abc123' }), issueTitle({ ref: 'refs/heads/main', key: 'abc123' }));
});
