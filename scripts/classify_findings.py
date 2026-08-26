#!/usr/bin/env python3
"""L2 fallback classifier. Reads redacted gitleaks JSON. Never prints secret values."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
ALLOW_PATH = re.compile(r"(test|example|sample|dummy|fixture|mock|\.env\.example|README|docs/)", re.I)
PLACEHOLDER = re.compile(r"(your-openai-api-key|sk-x+|REPLACE_ME|example_key|dummy_token|changeme|xxx+)", re.I)
RULE_SEVERITY = {"openai-api-key": "Critical", "anthropic-api-key": "Critical", "aws-access-key": "Critical", "generic-api-key": "Medium"}

def classify(item):
    path = item.get("File") or item.get("file") or ""
    rule = item.get("RuleID") or item.get("rule_id") or "unknown"
    match = item.get("Match") or item.get("Secret") or ""
    if ALLOW_PATH.search(path) or PLACEHOLDER.search(str(match)):
        classification = "docs_example" if re.search(r"README|docs/", path, re.I) else "false_positive"
        severity = "Low"
    else:
        classification = "true_positive"
        severity = RULE_SEVERITY.get(rule, "Medium")
    return {"fingerprint": item.get("Fingerprint"), "rule_id": rule, "file": path, "classification": classification, "severity": severity}

def main():
    if len(sys.argv) < 2:
        print("usage: classify_findings.py <redacted-gitleaks.json>", file=sys.stderr)
        return 2
    data = json.loads(Path(sys.argv[1]).read_text())
    if isinstance(data, dict):
        data = data.get("findings") or data.get("leaks") or []
    json.dump([classify(x) for x in data], sys.stdout, indent=2)
    print()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
