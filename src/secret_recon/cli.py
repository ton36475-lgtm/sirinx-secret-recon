#!/usr/bin/env python3
"""CLI: scan own trees, emit redacted JSON + human summary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .classify import classify
from .scanner import findings_to_report, scan_tree, write_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SIRINX defensive secret recon (own assets only)")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--report-dir", default="./secret-scan-reports")
    parser.add_argument("--json-stdout", action="store_true")
    args = parser.parse_args(argv)
    scan_path = str(Path(args.path).resolve())
    findings = scan_tree(scan_path)
    report = findings_to_report(findings, scan_path)
    report["classified"] = [classify(f) for f in findings]
    dest_dir = Path(args.report_dir)
    stamp = report["timestamp_utc"].replace(":", "").replace("-", "")[:15]
    json_path = write_report(report, dest_dir / f"findings-{stamp}.json")
    files = [f"  - {p}" for p in report["files"]] or ["  (none)"]
    summary = "\n".join([
        "SIRINX Defensive Secret Recon Summary",
        f"UTC: {report['timestamp_utc']}",
        f"Path: {scan_path}",
        f"Matches: {report['total_matches']}  Actionable: {report['actionable']}",
        f"Rules: {json.dumps(report['rule_counts'])}",
        "Files:",
        *files,
        f"Report: {json_path}",
    ])
    (dest_dir / f"summary-{stamp}.txt").write_text(summary + "\n", encoding="utf-8")
    print(summary)
    if args.json_stdout:
        print(json.dumps(report, indent=2))
    return 0 if report["actionable"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
