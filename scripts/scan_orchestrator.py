#!/usr/bin/env python3
"""SIRINX / GhostClaw L1+L2 secret recon orchestrator (defensive, own-assets only)."""
from __future__ import annotations
import argparse, hashlib, json, math, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", ".venv", "venv", "__pycache__", ".terraform", "coverage", ".cache", "artifacts"}
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".woff", ".woff2", ".ttf", ".mp4", ".mp3", ".wasm", ".lock"}
MAX_FILE_BYTES = 1_500_000
PLACEHOLDER_RE = re.compile(r"(your[-_ ]?(openai|api|key)|sk-x+|replace[_-]?me|example[_-]?key|dummy[_-]?token|changeme|xxx+|todo|placeholder|not[_-]?a[_-]?secret)", re.I)
RULES = [
    {"id": "openai-api-key", "severity_hint": "critical", "regex": re.compile(r"sk-[a-zA-Z0-9]{20,}T3BlbkFJ[a-zA-Z0-9]{20,}")},
    {"id": "openai-api-key-generic", "severity_hint": "high", "regex": re.compile(r"sk-(?:proj-)?[a-zA-Z0-9_-]{32,}")},
    {"id": "anthropic-api-key", "severity_hint": "critical", "regex": re.compile(r"sk-ant-[a-zA-Z0-9\\-_]{20,}")},
    {"id": "aws-access-key", "severity_hint": "critical", "regex": re.compile(r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}")},
    {"id": "cloudflare-api-token", "severity_hint": "high", "regex": re.compile(r"(?i)(?:cloudflare|cf[_-]?api[_-]?token|CF_API_TOKEN)\\s*[:=]\\s*['\"]?[A-Za-z0-9_-]{37,}['\"]?")},
    {"id": "supabase-jwt", "severity_hint": "high", "regex": re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\\.eyJ[a-zA-Z0-9_-]{10,}\\.[a-zA-Z0-9_-]{10,}")},
    {"id": "jwt-secret-assignment", "severity_hint": "high", "regex": re.compile(r"(?i)(?:jwt[_-]?secret|signing[_-]?key|secret[_-]?key)\\s*[:=]\\s*['\"][^'\"]{16,}['\"]")},
    {"id": "generic-api-key-assignment", "severity_hint": "medium", "regex": re.compile(r"(?i)(?:api[_-]?key|apikey|access[_-]?token|auth[_-]?token|OPENAI_API_KEY)\\s*[:=]\\s*['\"]?[A-Za-z0-9_\\-]{20,}['\"]?")},
]
def shannon_entropy(s: str) -> float:
    if not s: return 0.0
    freq = {}
    for ch in s: freq[ch] = freq.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())
def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:16]
def mask(value: str) -> str:
    return "****" if len(value) <= 8 else value[:4] + "…" + value[-3:]
def is_placeholder(value: str, path: str) -> bool:
    name = path.lower()
    if any(x in name for x in (".example", "sample", "fixture", "dummy", "readme", "/docs/")): return True
    return bool(PLACEHOLDER_RE.search(value))
def classify(rule_id: str, value: str, path: str, hint: str):
    if is_placeholder(value, path): return "false_positive_placeholder", "low", "optional docs cleanup"
    if rule_id in {"openai-api-key", "anthropic-api-key", "aws-access-key"}: return "true_positive_candidate", "critical", "human gate + rotate after approval"
    if hint == "high": return "needs_review", "high", "issue + PR within 24h"
    return "needs_review", "medium", "classify and gitignore if leftover"
def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix.lower() in SKIP_SUFFIXES: continue
            try:
                if p.stat().st_size > MAX_FILE_BYTES: continue
            except OSError:
                continue
            yield p
def scan_path(root: Path):
    findings = []
    for path in iter_files(root):
        try: text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError: continue
        rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
        for rule in RULES:
            for m in rule["regex"].finditer(text):
                raw = m.group(0)
                line = text[: m.start()].count("\n") + 1
                verdict, sev, action = classify(rule["id"], raw, rel, rule["severity_hint"])
                findings.append({"rule_id": rule["id"], "path": rel, "line": line, "fingerprint": fingerprint(raw), "masked": mask(raw), "entropy": round(shannon_entropy(raw), 3), "verdict": verdict, "severity": sev, "action": action})
    return findings
def write_reports(findings, out_dir: Path, scan_path: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = out_dir / f"findings-{ts}.json"
    sum_path = out_dir / f"summary-{ts}.txt"
    json_path.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    by_rule, by_sev = {}, {}
    for f in findings:
        by_rule[f["rule_id"]] = by_rule.get(f["rule_id"], 0) + 1
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
    lines = ["SIRINX Defensive Secret Recon Summary", f"Timestamp (UTC): {ts}", f"Scan path: {scan_path}", f"Findings (redacted): {len(findings)}", f"By severity: {by_sev}", f"By rule: {by_rule}", "---", "Policy: own assets only. Never harvest third-party keys."]
    for f in findings:
        lines.append(f"- [{f['severity']}] {f['rule_id']} {f['path']}:{f['line']} fp={f['fingerprint']} verdict={f['verdict']}")
    sum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sum_path
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--report-dir", default="./secret-scan-reports")
    ap.add_argument("--fail-on", default="critical", choices=["none", "high", "critical"])
    args = ap.parse_args()
    root = Path(args.path).resolve()
    print(f"[secret-recon] scanning {root} (dry-run classify, redacted)")
    findings = scan_path(root)
    summary = write_reports(findings, Path(args.report_dir), str(root))
    print(summary.read_text())
    if args.fail_on != "none":
        rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        if any(rank.get(f["severity"], 0) >= rank[args.fail_on] and "placeholder" not in f["verdict"] for f in findings):
            return 2
    return 0
if __name__ == "__main__":
    sys.exit(main())
