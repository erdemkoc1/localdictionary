import os
import re
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

patterns = [
    ("HARDCODED_USER_PATH", re.compile(r'C:[/\\]Users[/\\][a-zA-Z0-9_.-]+', re.IGNORECASE)),
    ("API_KEY_OR_SECRET", re.compile(r'(api[_-]?key|secret[_-]?key|access[_-]?token|bearer[_-]?token)\s*[:=]\s*[\'"][^\'"]+[\'"]', re.IGNORECASE)),
    ("PRIVATE_KEY", re.compile(r'-----BEGIN\s+.*PRIVATE\s+KEY-----', re.IGNORECASE)),
    ("OPENAI_KEY", re.compile(r'sk-[a-zA-Z0-9]{20,}', re.IGNORECASE)),
    ("PASSWORD", re.compile(r'password\s*[:=]\s*[\'"][^\'"]+[\'"]', re.IGNORECASE)),
]

ignored_dirs = {'.git', 'venv', '.venv', 'build', 'dist', '__pycache__', 'scratch', '.vscode', '.idea'}

findings = []

# 1. Scan Working Directory Files
for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if d not in ignored_dirs]
    for f in files:
        if f.endswith(('.py', '.json', '.txt', '.md', '.yml', '.yaml', '.sh', '.bat', '.ps1')):
            fpath = os.path.join(root, f)
            relpath = os.path.relpath(fpath, base_dir)
            if "security_audit.py" in relpath:
                continue
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                    for line_no, line in enumerate(fp, 1):
                        for label, regex in patterns:
                            if regex.search(line):
                                findings.append((label, relpath, line_no, line.strip()))
            except Exception as e:
                print(f"Error reading {relpath}: {e}")

# 2. Scan Entire Git Commit History
git_history_leaks = []
try:
    res = subprocess.run(["git", "log", "-p"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    current_commit = "HEAD"
    for line in res.stdout.splitlines():
        if line.startswith("commit "):
            current_commit = line.split()[1]
        elif line.startswith("+") and not line.startswith("+++"):
            for label, regex in patterns:
                if label != "HARDCODED_USER_PATH": # Check secrets/keys in history
                    if regex.search(line):
                        git_history_leaks.append((label, current_commit[:8], line.strip()))
except Exception as e:
    print(f"Git history check warning: {e}")

# 3. Check for SQL Injection Vulnerabilities (cursor.execute with f-strings or .format)
sql_risks = []
for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if d not in ignored_dirs]
    for f in files:
        if f.endswith('.py'):
            fpath = os.path.join(root, f)
            relpath = os.path.relpath(fpath, base_dir)
            if "security_audit.py" in relpath or "test" in relpath or "scripts" in relpath:
                continue
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                for line_no, line in enumerate(fp, 1):
                    if re.search(r'execute\s*\(\s*f[\'"]', line):
                        # Flag if table/col is dynamic or if raw variable is injected into query
                        sql_risks.append((relpath, line_no, line.strip()))

# 4. Check for Unsafe Execution (eval, exec, pickle)
unsafe_calls = []
for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if d not in ignored_dirs]
    for f in files:
        if f.endswith('.py'):
            fpath = os.path.join(root, f)
            relpath = os.path.relpath(fpath, base_dir)
            if "security_audit.py" in relpath:
                continue
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                for line_no, line in enumerate(fp, 1):
                    if re.search(r'\b(eval|exec|pickle\.loads?|yaml\.unsafe_load)\s*\(', line):
                        unsafe_calls.append((relpath, line_no, line.strip()))

print("=" * 75)
print("PROFESSIONAL PRE-RELEASE SECURITY AUDIT")
print("=" * 75)
print(f"1. Working Tree Secret/Path Findings : {len(findings)}")
for label, relpath, line_no, content in findings:
    print(f"   [{label}] {relpath}:{line_no} -> {content[:80]}")

print(f"\n2. Full Git History Secret Leaks    : {len(git_history_leaks)}")
for label, commit, snippet in git_history_leaks:
    print(f"   [{label}] commit {commit} -> {snippet[:80]}")

print(f"\n3. Potential Dynamic SQL Injections : {len(sql_risks)}")
for relpath, line_no, snippet in sql_risks:
    print(f"   [SQL_INSPECT] {relpath}:{line_no} -> {snippet[:80]}")

print(f"\n4. Unsafe Function Calls (eval/exec): {len(unsafe_calls)}")
for relpath, line_no, snippet in unsafe_calls:
    print(f"   [UNSAFE_CALL] {relpath}:{line_no} -> {snippet[:80]}")

print("=" * 75)
