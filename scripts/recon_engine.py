#!/usr/bin/env python3
"""SIRINX / GhostClaw L1 defensive secret recon engine.

Scans local trees owned by the operator. Never prints raw secret values.
Does not require gitleaks. Produces redacted JSON + summary.
"""
from __future__ import annotations

import argparse, hashlib, json, math, re, sys
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", ".venv", "venv", "__pycache__", ".terraform", "coverage", ".cache"}
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".woff", ".woff2", ".ttf", ".mp4", ".mp3", ".lock"}
MAX_FILE_BYTES = 1_500_000
RULES = [
    ("openai-api-key", re.compile(r"sk-[a-zA-Z0-9]{20,}T3BlbkFJ[a-zA-Z0-9]{20,}"), 3.5, "Critical"),
    ("openai-api-key-generic", re.compile(r"sk-[a-zA-Z0-9]{48,}"), 3.8, "Critical"),
    ("anthropic-api-key", re.compile(r"sk-ant-[a-zA-Z0-9\-]{40,}"), 3.5, "Critical"),
    ("aws-access-key", re.compile(r"(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"), 3.0, "Critical"),
    ("cloudflare-api-token", re.compile(r"(?i)(CF_API_TOKEN|CLOUDFLARE_API_TOKEN)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{30,}"), 3.4, "High"),
    ("supabase-jwt", re.compile(r"eyJ[a-zA-Z0-9_-]{20,}\.eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}"), 3.5, "High"),
    ("generic-api-key", re.compile(r"(?i)(api[_-]?key|apikey|access[_-]?token|auth[_-]?token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}['\"]"), 3.4, "Medium"),
]
ALLOW_PATH = re.compile(r"(test|example|sample|dummy|fixture|mock|\.env\.example|README|docs/|SKILL\.md)", re.I)
PLACEHOLDER = re.compile(r"(your[-_ ]?(openai|api)[-_ ]?key|sk-x+|REPLACE_ME|example_key|dummy_token|changeme|xxx+|placeholder|TODO)", re.I)

def shannon(s):
    if not s: return 0.0
    freq = {}
    for ch in s: freq[ch] = freq.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())

def redact(value):
    if len(value) <= 8: return "***REDACTED***"
    return value[:4] + "…" + value[-4:] + f" (len={len(value)})"

def fingerprint(rule, path, value):
    return hashlib.sha256(f"{rule}|{path}|{value}".encode("utf-8", errors="ignore")).hexdigest()[:16]

def classify(path, value, default_sev):
    if ALLOW_PATH.search(path) or PLACEHOLDER.search(value):
        kind = "docs_example" if re.search(r"README|docs/|SKILL\.md", path, re.I) else "false_positive"
        return kind, "Low"
    return "needs_review", default_sev

def iter_files(root):
    for p in root.rglob("*"):
        if not p.is_file(): continue
        if any(part in SKIP_DIRS for part in p.parts): continue
        if p.suffix.lower() in SKIP_SUFFIX: continue
        try:
            if p.stat().st_size > MAX_FILE_BYTES: continue
        except OSError:
            continue
        yield p

def scan_path(root):
    findings = []
    for path in iter_files(root):
        try: text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError: continue
        rel = str(path)
        for rule_id, rx, min_entropy, sev in RULES:
            for m in rx.finditer(text):
                value = m.group(0)
                if shannon(value) < min_entropy and rule_id.startswith(("openai", "anthropic", "aws", "supabase")):
                    continue
                kind, severity = classify(rel, value, sev)
                findings.append({"rule_id": rule_id, "file": rel, "line": text[:m.start()].count("\n")+1, "redacted": redact(value), "fingerprint": fingerprint(rule_id, rel, value), "classification": kind, "severity": severity, "entropy": round(shannon(value), 3)})
    return findings

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--out-dir", default="./secret-scan-reports")
    args = ap.parse_args(argv)
    root = Path(args.path).resolve(); out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    findings = scan_path(root)
    by_rule, by_sev = {}, {}
    for f in findings:
        by_rule[f["rule_id"]] = by_rule.get(f["rule_id"], 0) + 1
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
    payload = {"policy": "own-assets-only", "mode": "dry-run", "scanned_at": ts, "scan_path": str(root), "summary": {"count": len(findings), "by_rule": by_rule, "by_severity": by_sev, "needs_review": sum(1 for f in findings if f["classification"]=="needs_review")}, "findings": findings}
    (out / f"findings-{ts}.json").write_text(json.dumps(payload, indent=2)+"\n")
    print(f"Findings (redacted): {len(findings)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
