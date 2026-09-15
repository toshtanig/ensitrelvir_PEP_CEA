from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FILES_TO_CHECK = [
    "README.md",
    "SUBMISSION_AHEHP.md",
    "CITATION.cff",
    ".zenodo.json",
    "pyproject.toml",
]
PATTERNS = [
    re.compile(r"REPLACE_WITH_[A-Z0-9_]+"),
    re.compile(r"\{\{[^{}]+\}\}"),
    re.compile(r"\[\[[^\[\]]+\]\]"),
]


def main() -> int:
    problems = []
    for rel in FILES_TO_CHECK:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in PATTERNS:
            for match in pattern.finditer(text):
                problems.append(f"{rel}: {match.group(0)}")
        if "\u2014" in text:
            problems.append(f"{rel}: contains an em dash")
    try:
        cff = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
        if cff.get("version") != "0.3.2":
            problems.append("CITATION.cff: version is not 0.3.2")
        if not cff.get("doi"):
            problems.append("CITATION.cff: DOI missing")
        if not cff.get("authors"):
            problems.append("CITATION.cff: authors missing")
    except Exception as exc:
        problems.append(f"CITATION.cff parse error: {exc}")
    try:
        zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
        for key in ["title", "creators", "version", "license", "upload_type"]:
            if not zenodo.get(key):
                problems.append(f".zenodo.json: {key} missing")
    except Exception as exc:
        problems.append(f".zenodo.json parse error: {exc}")
    if problems:
        print("Release readiness: FAIL")
        for problem in problems:
            print("-", problem)
        return 1
    print("Release readiness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
