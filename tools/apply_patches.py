#!/usr/bin/env python3
"""Apply ordered source patches strictly; reuse only an unchanged patched tree."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root):
    value = hashlib.sha256()
    for path in sorted(root.rglob('*')):
        if path.name == '.ror-patches.json' or not path.is_file():
            continue
        value.update(str(path.relative_to(root)).encode())
        value.update(bytes.fromhex(digest(path)))
    return value.hexdigest()


root = Path.cwd()
patches = [Path(arg).resolve() for arg in sys.argv[1:]]
ordered = [{'file': p.name, 'sha256': digest(p)} for p in patches]
marker = root / '.ror-patches.json'
if marker.exists():
    expected = json.loads(marker.read_text())
    if expected != {'patches': ordered, 'tree_sha256': tree_digest(root)}:
        sys.exit('Patched source changed; use a fresh ExternalProject source directory')
else:
    for patch in patches:
        subprocess.run(['git', 'apply', '--check', str(patch)], check=True)
        subprocess.run(['git', 'apply', '--whitespace=nowarn', str(patch)], check=True)
    marker.write_text(json.dumps({'patches': ordered, 'tree_sha256': tree_digest(root)}, indent=2) + '\n')
