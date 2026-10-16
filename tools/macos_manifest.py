#!/usr/bin/env python3
"""Publish notices/provenance only for a completed, configured source graph.

This receipt establishes build provenance, not binary redistribution clearance.
Private configured inputs stay in the build directory, outside the public receipt.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def encoded(data):
    return (json.dumps(data, sort_keys=True, indent=2) + '\n').encode()


def digest(content):
    return hashlib.sha256(content).hexdigest()


def write_changed(path, content):
    if not path.exists() or path.read_bytes() != content:
        path.write_bytes(content)


def fail(message):
    raise SystemExit(message)


def configure(a):
    inventory = a.inventory.read_bytes()
    if inventory != a.live_inventory.read_bytes():
        fail('Configured inventory differs from the live inventory; reconfigure')
    settings = dict(value.split('=', 1) for value in a.setting)
    inputs = {str(path.relative_to(a.recipes)): digest(path.read_bytes())
              for path in a.input}
    context = {
        'schema_version': 1,
        'source_inventory_sha256': digest(inventory),
        'recipe_inputs': inputs,
        'settings': settings,
        'paths': {key: str(getattr(a, key).absolute()) for key in
                  ('inventory', 'live_inventory', 'recipes', 'build', 'sources', 'prefix')},
    }
    context['configuration_sha256'] = digest(encoded(context))
    write_changed(a.configured, encoded(context))


def validate(configured, completed=True):
    context = json.loads(configured.read_bytes())
    identity = context.pop('configuration_sha256')
    if identity != digest(encoded(context)):
        fail('Configured build identity was modified; reconfigure')
    context['configuration_sha256'] = identity
    paths = {key: Path(value) for key, value in context['paths'].items()}
    for key in ('inventory', 'live_inventory'):
        if digest(paths[key].read_bytes()) != context['source_inventory_sha256']:
            fail('Source inventory changed; select a fresh build directory')
    for relative, expected in context['recipe_inputs'].items():
        if digest((paths['recipes'] / relative).read_bytes()) != expected:
            fail(f'Configured recipe input changed: {relative}; reconfigure')
    data = json.loads(paths['inventory'].read_bytes())
    for name in data['components'] if completed else ():
        stamp = paths['build'] / 'Stamp' / name
        marker = stamp / 'macos-configured-build.json'
        done = stamp / (name + '-done')
        if not marker.is_file() or marker.read_bytes() != configured.read_bytes():
            fail(f'Component {name} has not completed this configured build')
        if not done.is_file() or done.stat().st_mtime_ns < marker.stat().st_mtime_ns:
            fail(f'Component {name} completion is missing or stale')
    return context, paths, data


def replace_metadata(output, staged, previous):
    if output.exists():
        output.rename(previous)
    try:
        staged.rename(output)
    except OSError:
        if previous.exists():
            previous.rename(output)
        raise


def begin_install(a):
    context, paths, data = validate(a.configured, completed=False)
    if a.component not in data['components']:
        fail(f'Unknown component: {a.component}')
    stamp = paths['build'] / 'Stamp' / a.component
    (stamp / 'macos-configured-build.json').unlink(missing_ok=True)
    (stamp / (a.component + '-done')).unlink(missing_ok=True)
    (paths['build'] / 'macos-build-complete.json').unlink(missing_ok=True)
    output = paths['prefix'] / 'share/ror-dependencies'
    output.parent.mkdir(parents=True, exist_ok=True)
    state = {key: context[key] for key in ('source_inventory_sha256', 'configuration_sha256')}
    state.update(schema_version=1, state='in-progress', profile=data['profile'],
                 dependencies_version=data['dependencies_version'])
    with tempfile.TemporaryDirectory(prefix='.ror-metadata-', dir=output.parent) as temporary:
        staged = Path(temporary) / 'ror-dependencies'
        staged.mkdir()
        (staged / 'build-receipt.json').write_bytes(encoded(state))
        replace_metadata(output, staged, Path(temporary) / 'previous')
    print('Invalidated completed metadata before component install')


def publish(a):
    context, paths, data = validate(a.configured)
    completion_path = paths['build'] / 'macos-build-complete.json'
    completion = json.loads(completion_path.read_bytes()) if completion_path.exists() else {}
    identity = {key: context[key] for key in ('configuration_sha256', 'source_inventory_sha256')}
    matches = completion.get('state') == 'complete' and all(
        completion.get(key) == value for key, value in identity.items())
    if a.phase == 'refresh' and not matches:
        fail('No successful completion for this configured build; build macos-manifest first')
    if not matches:
        completion = dict(identity, schema_version=1, state='complete',
                          completed_at=datetime.now(timezone.utc).isoformat())
    revision = subprocess.check_output(
        ['git', '-C', str(paths['recipes']), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = bool(subprocess.check_output(
        ['git', '-C', str(paths['recipes']), 'status', '--porcelain'], text=True).strip())
    public = dict(completion, recipe_revision=revision, recipe_tree_dirty=dirty)
    data.update(public)
    settings = context['settings']
    receipt = dict(public, profile=data['profile'], dependencies_version=data['dependencies_version'],
                   toolchain={key: settings[source] for key, source in {
                       'cmake_version': 'cmake_version', 'compiler': 'compiler',
                       'sdk_version': 'sdk_version', 'architecture': 'CMAKE_OSX_ARCHITECTURES',
                       'deployment_target': 'CMAKE_OSX_DEPLOYMENT_TARGET',
                       'build_type': 'CMAKE_BUILD_TYPE'}.items()})
    labels = {'CMake': 'cmake_version', 'Compiler': 'compiler', 'SDK': 'sdk_version',
              'Architecture': 'architecture', 'Deployment target': 'deployment_target',
              'Build type': 'build_type'}
    text = ''.join(f'{label}: {receipt["toolchain"][key]}\n' for label, key in labels.items())
    # Validate every notice/patch before touching the installed receipt. Stage the
    # entire metadata directory so validation/copy failures preserve the old one.
    output = paths['prefix'] / 'share/ror-dependencies'
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.ror-metadata-', dir=output.parent) as temporary:
        staged = Path(temporary) / 'ror-dependencies'
        staged.mkdir()
        for name, row in data['components'].items():
            for patch in row.get('patches', []):
                if digest((paths['recipes'] / patch['path']).read_bytes()) != patch['sha256']:
                    fail(f'Source patch hash changed: {patch["path"]}')
            row['installed_notices'] = []
            for relative in row['license_paths']:
                source = paths['sources'] / name / relative
                if not source.is_file():
                    fail(f'Missing selected notice: {name}/{relative}')
                destination = staged / 'licenses' / name / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
                row['installed_notices'].append(str(destination.relative_to(staged)))
        (staged / 'manifest.json').write_bytes(encoded(data))
        (staged / 'build-receipt.json').write_bytes(encoded(receipt))
        (staged / 'build-receipt.txt').write_text(text)
        replace_metadata(output, staged, Path(temporary) / 'previous')
    write_changed(completion_path, encoded(completion))
    print(f'Published completed {data["profile"]} metadata: {identity["configuration_sha256"]}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='phase', required=True)
    config = subparsers.add_parser('configure')
    for name in ('inventory', 'live-inventory', 'recipes', 'build', 'sources', 'prefix', 'configured'):
        config.add_argument('--' + name, type=Path, required=True)
    config.add_argument('--input', type=Path, action='append', default=[])
    config.add_argument('--setting', action='append', default=[])
    for phase in ('begin-install', 'complete', 'refresh'):
        command = subparsers.add_parser(phase)
        command.add_argument('--configured', type=Path, required=True)
        if phase == 'begin-install':
            command.add_argument('--component', required=True)
    args = parser.parse_args()
    if args.phase == 'configure':
        configure(args)
    elif args.phase == 'begin-install':
        begin_install(args)
    else:
        publish(args)


if __name__ == '__main__':
    main()
