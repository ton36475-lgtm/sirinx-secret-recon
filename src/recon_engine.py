#!/usr/bin/env python3
"""SIRINX defensive secret recon engine.

Scans local trees for high-signal credential patterns.
Stores fingerprints only. Never prints raw secret values.
Own-assets hygiene only — not a third-party key harvester.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

SKIP_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", ".venv", "venv",
    "__pycache__", ".terraform", "coverage", ".cache", "artifacts",
}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".gz",
    ".woff", ".woff2", ".ico", ".mp4", ".mov", ".bin",
}
PLACEHOLDER_MARKERS = (
    "your-openai-api-key", "sk-xxxxxxxx", "replace_me", "changeme",
    "example_key", "dummy_token", "xxxxx", "todo", "placeholder",
    "sample", "<your", "xxx-xxx",
)
RULES = [
    ("openai-api-key", re.compile(r"sk-[a-zA-Z0-9]{20,}T3BlbkFJ[a-zA-Z0-9]{20,}")),
    ("openai-api-key-generic", re.compile(r"sk-[a-zA-Z0-9]{48,}")),
    ("anthropic-api-key", re.compile(r"sk-ant-[a-zA-Z0-9\-]{40,}")),
    ("aws-access-key", re.compile(r"(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}")),
    ("cloudflare-api-token", re.compile(r"(?i)(cloudflare|cf[_-]?api[_-]?token|CF_API_TOKEN)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{37,}['\"]?")),
    ("supabase-jwt", re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}")),
    ("jwt-secret-assign", re.compile(r"(?i)(jwt[_-]?secret|signing[_-]?key)\s*[:=]\s*['\"][^'\"]{16,}['\"]")),
    ("generic-api-key-assign", re.compile(r"(?i)(api[_-]?key|apikey|access[_-]?token|auth[_-]?token|secret[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9_\-/.+=]{20,}['\"]?")),
    ("private-key-block", re.compile(r"-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----")),
]

@dataclass
class Finding:
    rule_id: str
    file: str
    line: int
    fingerprint: str
    preview: str
    classification: str
    severity_hint: str

def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:16]

def mask(value: str) -> str:
    compact = re.sub(r"\s+", " ", value).strip()
    if len(compact) <= 8:
        return "****"
    return compact[:4] + "\u2026" + compact[-3:]

def classify(value: str, path: str) -> tuple[str, str]:
    lower = value.lower()
    path_l = path.lower()
    if any(m in lower for m in PLACEHOLDER_MARKERS) or any(
        part in path_l for part in ("example", "sample", "fixture", "dummy", "readme", "docs/")
    ):
        return "likely_placeholder", "low"
    if path_l.endswith(".env.example") or path_l.endswith(".env.sample"):
        return "likely_placeholder", "low"
    if "BEGIN" in value and "PRIVATE KEY" in value:
        return "needs_review", "critical"
    if value.startswith("sk-ant-") or value.startswith("sk-") or value.startswith("AKIA"):
        return "needs_review", "high"
    return "needs_review", "medium"

def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() in SKIP_SUFFIXES:
                continue
            try:
                if p.stat().st_size > 2_000_000:
                    continue
            except OSError:
                continue
            yield p

def scan_text(rel: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for rule_id, rx in RULES:
            for match in rx.finditer(line):
                raw = match.group(0)
                kind, sev = classify(raw, rel)
                findings.append(
                    Finding(
                        rule_id=rule_id,
                        file=rel,
                        line=idx,
                        fingerprint=fingerprint(raw),
                        preview=mask(raw),
                        classification=kind,
                        severity_hint=sev,
                    )
                )
    return findings

def scan_path(root: Path) -> list[Finding]:
    out: list[Finding] = []
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(path.relative_to(root))
        out.extend(scan_text(rel, text))
    return out

def write_reports(findings: list[Finding], report_dir: Path, scan_path: str) -> dict:
    report_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "system": "sirinx-secret-recon",
        "mode": "defensive-own-assets-only",
        "timestamp_utc": ts,
        "scan_path": scan_path,
        "finding_count": len(findings),
        "needs_review": sum(1 for f in findings if f.classification == "needs_review"),
        "placeholders": sum(1 for f in findings if f.classification == "likely_placeholder"),
        "findings": [asdict(f) for f in findings],
        "policy": "raw secret values are never stored",
    }
    json_path = report_dir / f"findings-{ts}.json"
    summary_path = report_dir / f"summary-{ts}.txt"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "SIRINX Defensive Secret Recon Summary",
        f"Timestamp (UTC): {ts}",
        f"Scan path: {scan_path}",
        f"Findings: {payload['finding_count']}  needs_review={payload['needs_review']}  placeholders={payload['placeholders']}",
        "---",
    ]
    by_rule: dict[str, int] = {}
    for f in findings:
        by_rule[f.rule_id] = by_rule.get(f.rule_id, 0) + 1
    for rule, n in sorted(by_rule.items(), key=lambda kv: -kv[1]):
        lines.append(f"  {rule}: {n}")
    lines += [
        "---",
        "Next: L2 classify -> GhostClaw human gate for High/Critical -> remediate -> re-scan",
        "Never persist raw secret values.",
    ]
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload["_reports"] = {"json": str(json_path), "summary": str(summary_path)}
    return payload

def main() -> int:
    parser = argparse.ArgumentParser(description="Defensive secret recon (own assets only)")
    parser.add_argument("path", nargs="?", default=".", help="Directory to scan")
    parser.add_argument("--report-dir", default="./secret-scan-reports")
    args = parser.parse_args()
    root = Path(args.path).resolve()
    if not root.exists():
        print(f"[secret-recon] path not found: {root}", file=sys.stderr)
        return 2
    print(f"[secret-recon] scanning {root}")
    findings = scan_path(root)
    payload = write_reports(findings, Path(args.report_dir), str(root))
    print(payload["_reports"]["summary"])
    print(Path(payload["_reports"]["summary"]).read_text(encoding="utf-8"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
