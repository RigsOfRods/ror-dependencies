"""Metadata lifecycle fixtures; these do not claim a real dependency build."""
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
        self.configured = self.configure(self.build, 'Release')
        self.output = self.prefix / 'share/ror-dependencies'

    def invoke(self, phase, *args, success=True):
        result = subprocess.run([sys.executable, str(TOOL), phase, *map(str, args)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)

    def configure(self, build, kind):
        configured = build / 'macos-configured-build.json'
        settings = {'cmake_version': 'test', 'compiler': 'test', 'sdk_version': '27.0',
                    'CMAKE_OSX_ARCHITECTURES': 'arm64', 'CMAKE_OSX_DEPLOYMENT_TARGET': '11.0',
                    'CMAKE_BUILD_TYPE': kind}
        args = ['--inventory', self.inventory, '--live-inventory', self.inventory,
                '--recipes', REPO, '--build', build, '--sources', self.root / 'sources',
                '--prefix', self.prefix, '--configured', configured, '--input', TOOL]
        for key, value in settings.items():
            args += ['--setting', key + '=' + value]
        self.invoke('configure', *args)
        return configured

    def finish_fixture(self):
        stamp = self.build / 'Stamp/fixture'
        stamp.mkdir(parents=True, exist_ok=True)
        (stamp / 'macos-configured-build.json').write_bytes(self.configured.read_bytes())
        (stamp / 'fixture-done').touch()
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


if __name__ == '__main__':
    unittest.main()
