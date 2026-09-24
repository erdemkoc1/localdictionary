import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

patterns = [
    ("HARDCODED_USER_PATH", re.compile(r'C:[/\\]Users[/\\][a-zA-Z0-9_.-]+', re.IGNORECASE)),
    ("API_KEY_OR_SECRET", re.compile(r'(api[_-]?key|secret[_-]?key|access[_-]?token|bearer[_-]?token)\s*[:=]\s*[\'"][^\'"]+[\'"]', re.IGNORECASE)),
    ("PRIVATE_KEY", re.compile(r'-----BEGIN\s+.*PRIVATE\s+KEY-----', re.IGNORECASE)),
    ("OPENAI_KEY", re.compile(r'sk-[a-zA-Z0-9]{20,}', re.IGNORECASE)),
    ("PASSWORD", re.compile(r'password\s*[:=]\s*[\'"][^\'"]+[\'"]', re.IGNORECASE)),
    ("USERNAME", re.compile(r'\berdem\b', re.IGNORECASE))
]

ignored_dirs = {'.git', 'venv', '.venv', 'build', 'dist', '__pycache__', 'scratch', '.vscode', '.idea'}

findings = []

for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if d not in ignored_dirs]
    for f in files:
        if f.endswith(('.py', '.json', '.txt', '.md', '.yml', '.yaml', '.sh', '.bat', '.ps1')):
            fpath = os.path.join(root, f)
            relpath = os.path.relpath(fpath, base_dir)
            # Skip this security script itself
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

print("=" * 70)
print(f"SECURITY & PRIVACY AUDIT REPORT (Total findings: {len(findings)})")
print("=" * 70)
for label, relpath, line_no, content in findings:
    print(f"[{label}] {relpath}:{line_no} -> {content[:100]}")
print("=" * 70)
