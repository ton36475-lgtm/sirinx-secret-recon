"""L1 local scanner — regex + entropy, redacted output only."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .fingerprint import fingerprint, redact, shannon_entropy
from .patterns import ALLOW_PATH_FRAGMENTS, PLACEHOLDER_HINTS, RULES, SKIP_SUFFIXES

MAX_FILE_BYTES = 1_500_000
SKIP_DIR_NAMES = {".git", "node_modules", ".next", "dist", "build", "__pycache__", ".venv", "venv", ".terraform", "coverage"}


@dataclass
class Finding:
    rule_id: str
    description: str
    severity_hint: str
    path: str
    line: int
    fingerprint: str
    redacted: str
    entropy: float
    likely_placeholder: bool
    allowlisted_path: bool


def _is_allowlisted_path(path: str) -> bool:
    lowered = path.lower().replace("\\", "/")
    return any(frag in lowered for frag in ALLOW_PATH_FRAGMENTS)


def _is_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(hint in lowered for hint in PLACEHOLDER_HINTS)


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            yield path


def scan_text(text: str, rel_path: str) -> list[Finding]:
    findings: list[Finding] = []
    allow = _is_allowlisted_path(rel_path)
    for line_no, line in enumerate(text.splitlines(), start=1):
        for rule in RULES:
            for match in rule.regex.finditer(line):
                value = match.group(0)
                ent = shannon_entropy(value)
                if ent < rule.entropy_min:
                    continue
                findings.append(
                    Finding(
                        rule_id=rule.id,
                        description=rule.description,
                        severity_hint=rule.severity_hint,
                        path=rel_path,
                        line=line_no,
                        fingerprint=fingerprint(value),
                        redacted=redact(value),
                        entropy=round(ent, 3),
                        likely_placeholder=_is_placeholder(value) or _is_placeholder(line),
                        allowlisted_path=allow,
                    )
                )
    return findings


def scan_tree(root: str | Path) -> list[Finding]:
    root_path = Path(root).resolve()
    out: list[Finding] = []
    for path in iter_files(root_path):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(path.relative_to(root_path))
        out.extend(scan_text(text, rel))
    return out


def findings_to_report(findings: list[Finding], scan_path: str) -> dict:
    actionable = [f for f in findings if not f.likely_placeholder and not f.allowlisted_path]
    bag = {}
    for f in actionable:
        bag[f.rule_id] = bag.get(f.rule_id, 0) + 1
    return {
        "system": "sirinx-secret-recon",
        "mode": "defensive-own-assets",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "scan_path": scan_path,
        "total_matches": len(findings),
        "actionable": len(actionable),
        "suppressed_placeholder_or_docs": len(findings) - len(actionable),
        "rule_counts": bag,
        "files": sorted({f.path for f in actionable}),
        "findings": [asdict(f) for f in findings],
        "policy": "raw secret values are never included",
    }


def write_report(report: dict, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return dest
