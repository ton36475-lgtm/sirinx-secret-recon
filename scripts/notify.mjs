#!/usr/bin/env node
// GitHub I/O half of the alert policy. All decisions live in alert_policy.mjs.
//
// Read by the workflow, so it must never treat a missing/unreadable scanner
// report as a clean scan: a broken reporter must fail the job loudly rather
// than silently skip the alert.
//
// Test hook so tests NEVER touch GitHub:
//   GH_STUB=<abs path to an executable>  run every gh invocation through it
//
// CI note: GITLEAKS_REPORT should be an ABSOLUTE path. gitleaks-action writes
// its report next to the runner workspace, not inside the checked-out repo,
// so a relative default resolves to the wrong file and every run would alert.

import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { decideAlert, LABELS_FOR_ISSUES } from './alert_policy.mjs';

const REPORT = process.env.GITLEAKS_REPORT || 'gitleaks-report.json';
const REPO = process.env.GITHUB_REPOSITORY || 'unknown/unknown';
const REF = process.env.GITHUB_REF || 'refs/heads/unknown';
const RUN_URL =
  process.env.RUN_URL ||
  (process.env.GITHUB_SERVER_URL && process.env.GITHUB_RUN_ID
    ? `${process.env.GITHUB_SERVER_URL}/${REPO}/actions/runs/${process.env.GITHUB_RUN_ID}`
    : 'local run');
const CREATED_AT = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
const STUB = process.env.GH_STUB || '';

function gh(args, { allowFail = false } = {}) {
  try {
    const [bin, ...rest] = STUB ? [STUB, ...args] : ['gh', ...args];
    return execFileSync(bin, rest, { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 });
  } catch (err) {
    if (allowFail) return '';
    throw err;
  }
}

function ghJson(args, fallback) {
  const out = gh(args, { allowFail: true }).trim();
  if (!out) return fallback;
  try {
    return JSON.parse(out);
  } catch {
    return fallback;
  }
}

/** gitleaks JSON is a flat array of finding objects. Normalise defensively. */
function loadFindings() {
  let raw;
  try {
    raw = JSON.parse(readFileSync(REPORT, 'utf8'));
  } catch (err) {
    console.error(
      `::error::gitleaks report unreadable at ${REPORT} (${err.code || err.message}) — ` +
        'refusing to report a clean scan on an unreadable report'
    );
    process.exit(2);
  }
  if (!Array.isArray(raw)) {
    console.error(`::error::gitleaks report is not a JSON array: ${REPORT}`);
    process.exit(2);
  }
  return raw;
}

const findings = loadFindings();

// Fetch existing tracking issues ONCE. The earlier double-fetch silently
// emptied the list and turned every recurrence into a new issue.
const existingIssues =
  findings.length === 0
    ? []
    : ghJson(
        ['issue', 'list', '--repo', REPO, '--state', 'open', '--limit', '100',
         '--json', 'number,title,body,state'],
        []
      ).filter((i) => String(i.title || '').startsWith('[SECRET-RECON]'));

const decision = decideAlert({
  findings,
  existingIssues,
  runMeta: { repo: REPO, ref: REF, runUrl: RUN_URL, createdAt: CREATED_AT },
});

switch (decision.action) {
  case 'skip':
    console.log(`No alert (${decision.reason}): ${findings.length} finding(s) in the report.`);
    break;

  case 'comment':
    gh(['issue', 'comment', String(decision.issueNumber), '--repo', REPO, '--body', decision.body]);
    console.log(
      `Recurrence of #${decision.issueNumber} — ${decision.count} rule/file pair(s). ` +
        'Appended a comment instead of opening a duplicate.'
    );
    break;

  case 'create': {
    const present = new Set(
      ghJson(['label', 'list', '--repo', REPO, '--limit', '100', '--json', 'name'], [])
        .map((l) => l.name)
    );
    const args = ['issue', 'create', '--repo', REPO, '--title', decision.title, '--body', decision.body];
    for (const l of LABELS_FOR_ISSUES) if (present.has(l)) args.push('--label', l);
    const url = gh(args).trim();
    console.log(`Opened ${url} — ${decision.count} rule/file pair(s), key ${decision.key}.`);
    break;
  }
}