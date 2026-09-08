#!/usr/bin/env python3
"""L2 classifier stub — redacted findings only."""
from __future__ import annotations
import json, sys
from pathlib import Path
PLACEHOLDER_MARKERS = ("your-", "example", "xxxxxxxx", "replace_me", "dummy", "changeme", "todo", "<")

def classify(item: dict) -> dict:
    path = str(item.get("File") or item.get("path") or "")
    rule = str(item.get("RuleID") or item.get("rule") or "unknown")
    redacted = str(item.get("Secret") or item.get("Match") or item.get("snippet") or "")
    lower = f"{path} {redacted}".lower()
    if any(p in path.lower() for p in (".env.example", ".env.sample", "readme", "/docs/")):
        severity, tp, rationale = "low", False, "Example/docs path."
    elif any(m in lower for m in PLACEHOLDER_MARKERS) or redacted.strip() in ("", "REDACTED"):
        severity, tp, rationale = "low", False, "Placeholder or redacted record."
    elif rule in {"openai-api-key", "anthropic-api-key", "aws-access-key", "supabase-service-role"}:
        severity, tp, rationale = "high", True, "High-signal rule; human gate before rotation."
    else:
        severity, tp, rationale = "medium", True, "Generic assignment; confirm before PR."
    return {"rule": rule, "path": path, "severity": severity, "true_positive": tp, "rationale": rationale}

def main() -> int:
    if len(sys.argv) < 2:
        print("usage: classify.py <redacted-findings.json>", file=sys.stderr); return 2
    data = json.loads(Path(sys.argv[1]).read_text())
    items = data.get("findings") if isinstance(data, dict) else data
    if items is None: items = [data]
    out = [classify(i if isinstance(i, dict) else {"Match": str(i)}) for i in items]
    print(json.dumps({"count": len(out), "classified": out}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
