"""Build a clean, self-contained LocalDictionary release directory.

This script never deploys to the Desktop, terminates running applications, or
copies mutable user data (settings/history/corrections/cache) into a release.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from src.version import APP_NAME, APP_VERSION

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
APP_DIR = DIST_DIR / "localdictionary"
TARGET_NAME = "localdictionary"
EXCLUDED_MODULES = [
    "argostranslate", "torch", "torchvision", "torchaudio", "spacy", "thinc",
    "stanza", "pytest", "IPython", "notebook", "torchvision", "tensorflow",
]


def _run(command: list[str]) -> None:
    print("Running:", subprocess.list2cmdline(command))
    subprocess.run(command, cwd=BASE_DIR, check=True)


def _validate_assets() -> None:
    required = [
        BASE_DIR / "data" / "dictionary.db",
        BASE_DIR / "data" / "models" / "translate-tr_en-1_5" / "model",
        BASE_DIR / "data" / "models" / "translate-en_tr-1_5" / "model",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing release assets:\n- " + "\n- ".join(missing))


def _copy_release_assets() -> None:
    data_dir = APP_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BASE_DIR / "data" / "dictionary.db", data_dir / "dictionary.db")

    source_models = BASE_DIR / "data" / "models"
    target_models = data_dir / "models"
    shutil.copytree(
        source_models,
        target_models,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("stanza", "__pycache__", "*.pyc"),
    )

    # Mutable user files are intentionally NOT part of a release.
    forbidden_names = {"settings.json", "history.db", "user_data.db", "error_log.txt"}
    for path in APP_DIR.rglob("*"):
        if path.is_file() and path.name in forbidden_names:
            raise RuntimeError(f"Refusing to package mutable user file: {path}")

    for filename in (
        "LICENSE", "README.md", "SECURITY.md", "THIRD_PARTY_NOTICES.md", "DATA_LICENSES.md"
    ):
        source = BASE_DIR / filename
        if source.is_file():
            shutil.copy2(source, APP_DIR / filename)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_source_manifest() -> Path:
    source_assets = [BASE_DIR / "data" / "dictionary.db"]
    source_assets.extend(path for path in (BASE_DIR / "data" / "models").rglob("*") if path.is_file())
    manifest = APP_DIR / "RELEASE_MANIFEST.json"
    payload = {
        "application": APP_NAME,
        "version": APP_VERSION,
        "built_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "network_policy": "runtime has no network client or remote model/package index",
        "user_data_policy": "mutable data is excluded; runtime data belongs under LOCALAPPDATA",
        "source_assets": [
            {
                "path": path.relative_to(BASE_DIR).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            for path in sorted(source_assets)
        ],
    }
    manifest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def _write_checksums() -> Path:
    manifest = APP_DIR / "SHA256SUMS.txt"
    files = sorted(
        (path for path in APP_DIR.rglob("*") if path.is_file() and path != manifest),
        key=lambda path: path.relative_to(APP_DIR).as_posix().lower(),
    )
    with manifest.open("w", encoding="utf-8", newline="\n") as stream:
        for path in files:
            relative = path.relative_to(APP_DIR).as_posix()
            stream.write(f"{_sha256(path)}  {relative}\n")
    return manifest


def _write_release_readme() -> None:
    text = (
        f"{APP_NAME} v{APP_VERSION} - OFFLINE BETA\n"
        "===========================================\n\n"
        "This build performs dictionary lookup and neural translation locally.\n"
        "It contains no telemetry, cloud API client, update client, or network feature.\n\n"
        "Run localdictionary.exe to start the application.\n"
        "SHA256SUMS.txt contains integrity hashes for every packaged file.\n\n"
        "This EXE is not code-signed. Verify its SHA-256 hash before running it.\n"
    )
    (APP_DIR / "RELEASE_README.txt").write_text(text, encoding="utf-8", newline="\n")


def _make_zip() -> Path:
    archive = DIST_DIR / f"LocalDictionary-v{APP_VERSION}-win64.zip"
    archive.unlink(missing_ok=True)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for path in sorted(APP_DIR.rglob("*")):
            if path.is_file():
                bundle.write(path, Path(TARGET_NAME) / path.relative_to(APP_DIR))
    return archive


def build(make_zip: bool = True) -> tuple[Path, Path | None]:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    _validate_assets()

    if APP_DIR.exists():
        shutil.rmtree(APP_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
        "--windowed", "--noupx", "--name", TARGET_NAME,
        "--collect-all", "customtkinter",
        "--collect-all", "pystray",
        "--collect-all", "PIL",
        "--collect-all", "ctranslate2",
        "--collect-all", "sentencepiece",
        "--hidden-import", "src.local_nmt",
        "--hidden-import", "src.user_data",
        "--hidden-import", "src.clause_splitter",
        "--hidden-import", "src.idiom_engine",
    ]
    for module in EXCLUDED_MODULES:
        command.extend(("--exclude-module", module))
    command.append(str(BASE_DIR / "main.py"))
    _run(command)

    _copy_release_assets()
    _write_release_readme()
    _write_source_manifest()
    manifest = _write_checksums()
    archive = _make_zip() if make_zip else None
    print(f"\nBuild complete: {APP_DIR}")
    print(f"Integrity manifest: {manifest}")
    if archive:
        print(f"Release archive: {archive}")
    return APP_DIR, archive


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-zip", action="store_true", help="Skip creation of the release ZIP")
    args = parser.parse_args()
    build(make_zip=not args.no_zip)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
