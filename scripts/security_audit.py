"""Offline repository security checks used before a public release."""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
IGNORED_DIRS = {".git", "venv", ".venv", "build", "dist", "__pycache__", "scratch", ".vscode", ".idea"}
SECRET_PATTERNS = [
    ("PRIVATE_KEY", re.compile(r"-----BEGIN\s+.*PRIVATE\s+KEY-----", re.I)),
    ("OPENAI_KEY", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("GITHUB_TOKEN", re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b")),
    ("AWS_ACCESS_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("API_SECRET", re.compile(r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]")),
]
PATH_PATTERN = re.compile(r"(?i)C:[\\/]Users[\\/][A-Za-z0-9_.-]+")
NETWORK_MODULES = {"argostranslate", "requests", "urllib", "http", "ftplib", "smtplib", "telnetlib"}


def _source_files(root: Path):
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in IGNORED_DIRS]
        for filename in files:
            path = Path(current) / filename
            if path.suffix.lower() in {".py", ".json", ".md", ".txt", ".yml", ".yaml", ".toml", ".ps1", ".bat", ".sh"}:
                yield path


def _git_history() -> str:
    result = subprocess.run(
        ["git", "log", "--all", "-p", "--no-ext-diff"],
        cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8", errors="ignore", check=False,
    )
    return result.stdout


def audit() -> list[str]:
    findings: list[str] = []
    for path in _source_files(BASE_DIR):
        relative = path.relative_to(BASE_DIR)
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{relative}:{line_no}: {label}")
            if PATH_PATTERN.search(line):
                findings.append(f"{relative}:{line_no}: HARDCODED_USER_PATH")
        if path.suffix == ".py" and "src" in relative.parts:
            try:
                tree = ast.parse(text)
            except SyntaxError as exc:
                findings.append(f"{relative}:{exc.lineno}: SYNTAX_ERROR")
                continue
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [(node.module or "").split(".")[0]]
                if NETWORK_MODULES.intersection(names):
                    findings.append(f"{relative}:{getattr(node, 'lineno', 1)}: NETWORK_IMPORT")
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in {"eval", "exec", "__import__"}:
                        findings.append(f"{relative}:{node.lineno}: UNSAFE_CALL")

    history = _git_history()
    for line_no, line in enumerate(history.splitlines(), 1):
        if PATH_PATTERN.search(line) and line.startswith("+"):
            findings.append(f"git-history:{line_no}: HARDCODED_USER_PATH")
        for label, pattern in SECRET_PATTERNS:
            if line.startswith("+") and pattern.search(line):
                findings.append(f"git-history:{line_no}: {label}")
    return findings


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    findings = audit()
    print("=" * 72)
    print("LOCALDICTIONARY SECURITY AUDIT")
    print("=" * 72)
    if findings:
        for finding in findings:
            print(f"[FINDING] {finding}")
        print(f"\nFAIL: {len(findings)} finding(s)")
        return 1
    print("PASS: no secret, hardcoded-path, unsafe-call, or runtime-network findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
