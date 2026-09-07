"""L2 heuristic classifier. LLM/OmniRoute can wrap this JSON later."""

from __future__ import annotations

from .scanner import Finding

SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}


def classify(finding: Finding) -> dict:
    severity = finding.severity_hint
    classification = "true_positive_candidate"
    if finding.likely_placeholder or finding.allowlisted_path:
        severity = "low"
        classification = "likely_false_positive"
    if finding.rule_id == "generic-api-key" and finding.entropy < 3.7:
        severity = "medium"
        classification = "needs_review"
    action = {
        "critical": "human_gate_then_rotate",
        "high": "issue_and_pr_24h",
        "medium": "issue_or_document",
        "low": "optional_docs",
        "info": "ignore",
    }[severity]
    return {
        "fingerprint": finding.fingerprint,
        "rule_id": finding.rule_id,
        "path": finding.path,
        "line": finding.line,
        "classification": classification,
        "severity": severity,
        "action": action,
        "redacted": finding.redacted,
    }
