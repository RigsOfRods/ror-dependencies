"""Metadata lifecycle fixtures; these do not claim a real dependency build."""
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / 'tools/macos_manifest.py'


class MetadataLifecycle(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.build = self.root / 'build'
        self.build.mkdir()
        self.prefix = self.root / 'prefix'
        self.inventory = self.root / 'inventory.json'
        self.inventory.write_text(json.dumps({
            'profile': 'native-macos-gl3', 'dependencies_version': 30,
            'components': {'fixture': {'sha256': 'a' * 64, 'patches': [],
                                       'license_paths': ['LICENSE']}}}))
        notice = self.root / 'sources/fixture/LICENSE'
        notice.parent.mkdir(parents=True)
        notice.write_text('Test fixture notice\n')
        self.recipes, self.recipe_input = REPO, TOOL
        self.configured = self.configure(self.build, 'Release')
        self.output = self.prefix / 'share/ror-dependencies'

    def invoke(self, phase, *args, success=True):
        result = subprocess.run([sys.executable, str(TOOL), phase, *map(str, args)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def configure(self, build, kind):
        configured = build / 'macos-configured-build.json'
        settings = {'cmake_version': 'test', 'compiler': 'test', 'sdk_version': '27.0',
                    'CMAKE_OSX_ARCHITECTURES': 'arm64', 'CMAKE_OSX_DEPLOYMENT_TARGET': '11.0',
                    'CMAKE_BUILD_TYPE': kind}
        args = ['--inventory', self.inventory, '--live-inventory', self.inventory,
                '--recipes', self.recipes, '--build', build, '--sources', self.root / 'sources',
                '--prefix', self.prefix, '--configured', configured, '--input', self.recipe_input]
        for key, value in settings.items():
            args += ['--setting', key + '=' + value]
        self.invoke('configure', *args)
        return configured

    def finish_fixture(self):
        for name in json.loads(self.inventory.read_bytes())['components']:
            stamp = self.build / 'Stamp' / name
            stamp.mkdir(parents=True, exist_ok=True)
            self.invoke('begin-install', '--configured', self.configured, '--component', name)
            self.invoke('finish-install', '--configured', self.configured, '--component', name)
            (stamp / (name + '-done')).touch()
        self.invoke('complete', '--configured', self.configured)

    def installed_hashes(self):
        return {str(p.relative_to(self.output)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.output.rglob('*') if p.is_file()}

    def test_inventory_mismatch_preserves_completed_metadata(self):
        self.finish_fixture()
        before = self.installed_hashes()
        self.inventory.write_text(self.inventory.read_text().replace('a' * 64, '0' * 64))
        self.invoke('complete', '--configured', self.configured, success=False)
        self.invoke('refresh', '--configured', self.configured, success=False)
        self.assertEqual(before, self.installed_hashes())

    def test_configure_only_cannot_relabel_release_as_debug(self):
        self.finish_fixture()
        before = self.installed_hashes()
        debug = self.root / 'debug'
        debug.mkdir()
        configured = self.configure(debug, 'Debug')
        self.assertEqual(before, self.installed_hashes())
        self.invoke('refresh', '--configured', configured, success=False)
        self.invoke('complete', '--configured', configured, success=False)
        self.assertEqual(before, self.installed_hashes())

    def test_interrupted_install_cannot_refresh_or_complete(self):
        self.finish_fixture()
        self.invoke('refresh', '--configured', self.configured)
        self.invoke('begin-install', '--configured', self.configured, '--component', 'fixture')
        self.assertEqual(json.loads((self.output / 'build-receipt.json').read_bytes())['state'],
                         'in-progress')
        self.assertFalse((self.output / 'manifest.json').exists())
        self.assertFalse((self.output / 'build-receipt.txt').exists())
        self.invoke('refresh', '--configured', self.configured, success=False)
        self.invoke('complete', '--configured', self.configured, success=False)
        self.finish_fixture()
        receipt = json.loads((self.output / 'build-receipt.json').read_bytes())
        manifest = json.loads((self.output / 'manifest.json').read_bytes())
        self.assertEqual(receipt['state'], 'complete')
        for key in ('configuration_sha256', 'source_inventory_sha256', 'completed_at'):
            self.assertEqual(receipt[key], manifest[key])
        self.assertEqual(receipt['toolchain']['build_type'], 'Release')

    def test_two_build_directories_cannot_publish_over_another_owner(self):
        inventory = json.loads(self.inventory.read_bytes())
        inventory['components']['second'] = inventory['components']['fixture'].copy()
        self.inventory.write_text(json.dumps(inventory))
        notice = self.root / 'sources/second/LICENSE'
        notice.parent.mkdir(parents=True)
        notice.write_text('Second test fixture notice\n')
        self.configured = self.configure(self.build, 'Release')
        self.finish_fixture()
        release = self.configured
        original_build = self.build
        debug = self.root / 'debug'
        debug.mkdir()
        other = self.configure(debug, 'Debug')
        self.invoke('begin-install', '--configured', other, '--component', 'fixture')
        before = self.installed_hashes()
        for phase in ('refresh', 'complete', 'begin-install'):
            args = ['--configured', release]
            if phase == 'begin-install':
                args += ['--component', 'fixture']
            self.invoke(phase, *args, success=False)
            self.assertEqual(before, self.installed_hashes())
        # Complete the owning build, then reject the old build's publication.
        self.build, self.configured = debug, other
        self.finish_fixture()
        completed = self.installed_hashes()
        for phase in ('refresh', 'complete'):
            self.invoke(phase, '--configured', release, success=False)
            self.assertEqual(completed, self.installed_hashes())
        self.invoke('refresh', '--configured', other)
        # Reclaiming a completed prefix creates a new installation generation.
        self.build, self.configured = original_build, release
        self.invoke('begin-install', '--configured', release, '--component', 'fixture')
        new_state = json.loads((self.output / 'build-receipt.json').read_bytes())
        self.assertEqual(new_state['state'], 'in-progress')
        self.invoke('finish-install', '--configured', release, '--component', 'fixture')
        (original_build / 'Stamp/fixture/fixture-done').touch()
        rejected = self.invoke('complete', '--configured', release, success=False)
        self.assertIn('Component second has not installed into the current prefix generation', rejected)
        self.finish_fixture()
        final = json.loads((self.output / 'build-receipt.json').read_bytes())
        self.assertEqual(final['installation_id'], new_state['installation_id'])
        self.assertEqual(final['toolchain']['build_type'], 'Release')

    def test_same_context_refresh_after_metadata_only_commit(self):
        self.recipes = self.root / 'recipes'
        self.recipes.mkdir()
        self.recipe_input = self.recipes / 'input.cmake'
        self.recipe_input.write_text('# Stable recipe input\n')
        def git(*args):
            return subprocess.check_output(['git', '-C', str(self.recipes),
                                            '-c', 'user.name=Fixture',
                                            '-c', 'user.email=fixture@example.invalid', *args],
                                           text=True).strip()
        git('init', '-q')
        git('add', 'input.cmake')
        git('commit', '-qm', 'Initial fixture')
        self.configured = self.configure(self.build, 'Release')
        self.finish_fixture()
        before = json.loads((self.output / 'build-receipt.json').read_bytes())
        (self.recipes / 'README.md').write_text('Metadata-only fixture change\n')
        git('add', 'README.md')
        git('commit', '-qm', 'Document fixture')
        self.invoke('refresh', '--configured', self.configured)
        after = json.loads((self.output / 'build-receipt.json').read_bytes())
        self.assertNotEqual(before['recipe_revision'], after['recipe_revision'])
        self.assertEqual(after['recipe_revision'], git('rev-parse', 'HEAD'))
        self.assertFalse(after['recipe_tree_dirty'])
        for key in ('installation_id', 'configuration_sha256', 'completed_at'):
            self.assertEqual(before[key], after[key])

    def test_metadata_updates_use_a_prefix_lock(self):
        self.finish_fixture()
        before = self.installed_hashes()
        with (self.prefix / 'share/.ror-dependencies.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.invoke('refresh', '--configured', self.configured, success=False)
            self.invoke('begin-install', '--configured', self.configured,
                        '--component', 'fixture', success=False)
        self.assertEqual(before, self.installed_hashes())
        self.invoke('refresh', '--configured', self.configured)


if __name__ == '__main__':
    unittest.main()
