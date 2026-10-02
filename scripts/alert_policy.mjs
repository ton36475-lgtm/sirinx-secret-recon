// Alert policy for the defensive secret-scan workflow.
//
// Pure decision logic, no I/O, no network. Kept separate from the GitHub API
// calls in `notify.mjs` so it can be unit tested on a laptop and in CI.
//
// SAFETY: nothing here ever receives, stores, or emits a secret value. A
// finding is identified only by rule id + file path, and the tracking key is a
// SHA-256 over that non-secret metadata.

import { createHash } from 'node:crypto';

/** Marker embedded in the body of a tracking issue so runs can find their predecessor. */
export const MARKER_OPEN = '<!-- secret-recon:tracking -->';
export const MARKER_CLOSE = '<!-- /secret-recon:tracking -->';
export const MARKER_VERSION = '2';

const LABELS = ['security', 'secret-recon', 'priority:high'];

/**
 * Reduce raw findings to the only fields we are allowed to act on.
 * Anything resembling a secret value is dropped here, at the boundary.
 */
export function normalizeFindings(findings) {
  if (!Array.isArray(findings)) return [];
  const seen = new Set();
  const out = [];
  for (const f of findings) {
    if (!f) continue;
    const rule = String(f.RuleID ?? f.ruleID ?? 'unknown');
    const file = String(f.File ?? f.file ?? 'unknown');
    const key = `${rule}:${file}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({ rule, file, key });
  }
  return out.sort((a, b) => (a.key < b.key ? -1 : a.key > b.key ? 1 : 0));
}

/**
 * Content-addressed key for a set of findings. Two runs that see the same
 * rule/file pairs produce the same key, which is what lets us collapse
 * day-after-day duplicates onto one issue.
 */
export function trackingKey(findings) {
  const norm = normalizeFindings(findings);
  const material = norm.map((f) => `${MARKER_VERSION}\t${f.key}`).join('\n');
  return {
    key: createHash('sha256').update(material).digest('hex').slice(0, 16),
    count: norm.length,
    normalized: norm,
  };
}

/** Title for a tracking issue. Deterministic, so duplicate detection is easy. */
export function issueTitle({ ref, key }) {
  return `[SECRET-RECON] ${ref} — ${key}`;
}

/**
 * Body of the tracking issue. Contains locations and run links only.
 */
export function issueBody({ repo, ref, findings, key, runUrl, createdAt }) {
  const norm = normalizeFindings(findings);
  const lines = [
    '## Defensive Secret Recon — recurring finding set',
    '',
    `- Repository: \`${repo}\``,
    `- Ref: \`${ref}\``,
    `- Tracking key: \`${key}\``,
    `- Distinct rule/file pairs: **${norm.length}**`,
    `- First seen: ${createdAt}`,
    `- First run: ${runUrl}`,
    '',
    MARKER_OPEN,
    '### Locations (rule + path only — no values are ever recorded)',
    '',
    ...norm.map((f) => `- \`${f.rule}\` → \`${f.file}\``),
    MARKER_CLOSE,
    '',
    '### Why this issue is not duplicated',
    '',
    'This workflow runs on a schedule against full history, so the same',
    'committed findings reappear on every run. New runs **append a comment** to',
    'this issue instead of opening a new one, keyed on the SHA-256 tracking key.',
    '',
    '### Triage (per SIRINX policy — human gate)',
    '',
    '1. Classify each location: true positive vs placeholder (L2 classifier).',
    '2. Placeholders are accepted into the gitleaks baseline so they stop',
    '   blocking CI; **accepted ≠ rotated**.',
    '3. True positives need an explicit human rotation decision. Deleting the',
    '   file does **not** un-leak a value already pushed — rotate at the',
    '   provider first.',
    '4. Never paste a raw value into this issue or any log.',
    '',
    'Scope: own assets only. Public key harvesting stays refused.',
  ];
  return lines.join('\n');
}

/** Comment appended when a later run sees the same finding set. */
export function commentBody({ runUrl, findings, createdAt }) {
  const norm = normalizeFindings(findings);
  return [
    `Recurrence ${createdAt} — same finding set still present.`,
    '',
    `- Run: ${runUrl}`,
    `- Distinct rule/file pairs: **${norm.length}**`,
    `- Locations: ${norm.map((f) => `\`${f.rule}\`→\`${f.file}\``).join(', ')}`,
    '',
    'No new locations added; still awaiting the L3 human gate above.',
  ].join('\n');
}

/**
 * Read the tracking key an existing issue was opened for, if any.
 * Returns null for issues we did not create.
 */
export function parseTrackingKey(issue) {
  const body = String(issue?.body ?? '');
  if (!body.includes(MARKER_OPEN)) return null;
  const m = body.match(/Tracking key: `([0-9a-f]{16})`/);
  return m ? m[1] : null;
}

/**
 * Core decision.
 *
 * @param {object} input
 * @param {Array}  input.findings       raw findings from the scanner
 * @param {Array}  input.existingIssues open issues in the repo
 * @param {object} input.runMeta        { repo, ref, runUrl, createdAt }
 * @returns {{action:'skip'|'comment'|'create', reason:string, issueNumber?:number, title?:string, body?:string, key?:string, count?:number}}
 */
export function decideAlert({ findings, existingIssues = [], runMeta }) {
  const { repo, ref, runUrl, createdAt } = runMeta;
  const norm = normalizeFindings(findings);

  if (norm.length === 0) {
    return { action: 'skip', reason: 'no_findings' };
  }

  const { key, count } = trackingKey(norm);

  // Only consider issues we own: our marker + our title shape.
  const candidate = existingIssues.find((issue) => {
    if (String(issue.state) !== 'open') return false;
    const title = String(issue.title ?? '');
    return (
      title.includes('[SECRET-RECON]') &&
      title.includes(ref) &&
      parseTrackingKey(issue) === key
    );
  });

  if (candidate) {
    return {
      action: 'comment',
      reason: 'same_finding_set_already_tracked',
      issueNumber: candidate.number,
      key,
      count,
      body: commentBody({ runUrl, findings: norm, createdAt }),
    };
  }

  return {
    action: 'create',
    reason: 'new_finding_set',
    key,
    count,
    title: issueTitle({ ref, key }),
    body: issueBody({ repo, ref, findings: norm, key, runUrl, createdAt }),
  };
}

export const LABELS_FOR_ISSUES = LABELS;
