#!/usr/bin/env python3
"""Install source/patch provenance and source notices for the selected prefix.

This inventory does not itself establish binary redistribution clearance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

p = argparse.ArgumentParser()
for name in ('inventory', 'recipes', 'sources', 'prefix'):
    p.add_argument('--' + name, type=Path, required=True)
a = p.parse_args()
data = json.loads(a.inventory.read_text())
output = a.prefix / 'share/ror-dependencies'
output.mkdir(parents=True, exist_ok=True)
data['recipe_revision'] = subprocess.check_output(
    ['git', '-C', str(a.recipes), 'rev-parse', 'HEAD'], text=True).strip()
data['recipe_tree_dirty'] = bool(subprocess.check_output(
    ['git', '-C', str(a.recipes), 'status', '--porcelain'], text=True).strip())
for name, row in data['components'].items():
    for patch in row.get('patches', []):
        actual = hashlib.sha256((a.recipes / patch['path']).read_bytes()).hexdigest()
        if actual != patch['sha256']:
            raise SystemExit(f"Source patch hash changed: {patch['path']}")
    row['installed_notices'] = []
    for relative in row['license_paths']:
        source = a.sources / name / relative
        if not source.is_file():
            raise SystemExit(f'Missing selected notice: {name}/{relative}')
        destination = output / 'licenses' / name / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        row['installed_notices'].append(str(destination.relative_to(output)))
(output / 'manifest.json').write_text(json.dumps(data, indent=2) + '\n')
