#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
ENGINE = HERE / "recon_engine.py"
CLASSIFY = HERE / "classify_findings.py"
ROOT = HERE.parent

def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)

def main():
    scan_path = sys.argv[1] if len(sys.argv) > 1 else str(ROOT)
    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    run([sys.executable, str(ENGINE), scan_path, "--out-dir", str(report_dir)])
    files = sorted(report_dir.glob("findings-*.json"))
    findings_file = files[-1]
    classified = run([sys.executable, str(CLASSIFY), str(findings_file)])
    print(classified.stdout)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
