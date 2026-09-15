from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {
    ".git",
    ".venv",
    "venv",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "dist",
    "build",
    "release_build",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--checksum", action="store_true", help="Also write a SHA-256 sidecar for manual verification.")
    args = parser.parse_args()
    if not args.skip_tests:
        for command in [
            [sys.executable, "scripts/check_release_readiness.py"],
            [sys.executable, "scripts/validate_inputs.py"],
            [sys.executable, "scripts/audit_derived_inputs.py"],
            [sys.executable, "-m", "pytest", "-q"],
        ]:
            subprocess.run(command, cwd=ROOT, check=True)
    dist = ROOT / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir()
    archive = dist / "ensitrelvir-pep-cea-v0.3.2.zip"
    prefix = "ensitrelvir-pep-cea-v0.3.2"
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED or part.endswith(".egg-info") for part in rel.parts):
            continue
        if path.suffix == ".zip":
            continue
        files.append(path)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
        for path in files:
            zip_file.write(path, f"{prefix}/{path.relative_to(ROOT).as_posix()}")
    print(archive)
    if args.checksum:
        digest = sha256(archive)
        (dist / f"{archive.name}.sha256").write_text(
            f"{digest}  {archive.name}\n", encoding="utf-8"
        )
        print(digest)


if __name__ == "__main__":
    main()
