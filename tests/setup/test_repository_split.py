import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class RepositorySplitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='repository-split-')
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.desktop = self.home / 'arch-desktop'
        self.portable = self.home / 'dotfiles'
        (self.desktop / 'setup/common').mkdir(parents=True)
        self.env = dict(os.environ, HOME=str(self.home), ARCH_DESKTOP_DIR=str(self.desktop),
                        DOTFILES_DIR=str(self.portable), XDG_CONFIG_HOME=str(self.home / ".config"),
                        XDG_DATA_HOME=str(self.home / ".local/share"))
        shutil.copy2(ROOT / 'setup/common/ensure-dotfiles', self.desktop / 'setup/common/ensure-dotfiles')
        shutil.copy2(ROOT / 'setup/boot.sh', self.desktop / 'setup/boot.sh')

    def seed_portable(self):
        for name in ['zsh/.zshenv', 'scripts/stow/stow-ai']:
            path = self.portable / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        (self.portable / 'setup/common').mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / 'portable/setup/common/check-machine-profile',
                     self.portable / 'setup/common/check-machine-profile')

    def run_script(self, relative, *args):
        return subprocess.run(['bash', str(self.desktop / relative), *args], env=self.env,
                              text=True, capture_output=True)

    def test_existing_checkout_is_linked_without_changing_local_edits(self):
        self.seed_portable()
        marker = self.portable / 'local-edits'
        marker.write_text('keep')
        result = self.run_script('setup/common/ensure-dotfiles')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.desktop / 'portable').resolve(), self.portable)
        self.assertEqual(marker.read_text(), 'keep')
        self.assertEqual(result.stdout.strip(), str(self.portable))

    def test_missing_checkout_uses_the_portable_remote_and_a_shallow_clone(self):
        commands = self.home / 'commands'
        commands.mkdir()
        git = commands / 'git'
        git.write_text('''#!/bin/bash
set -eu
printf '%s\\n' "$@" > "$HOME/clone-args"
[[ "$1 $2 $3 $4" == "clone --depth 1 https://github.com/Zihad550/dotfiles.git" ]]
mkdir -p "$5/zsh" "$5/scripts/stow"
touch "$5/zsh/.zshenv" "$5/scripts/stow/stow-ai"
''')
        git.chmod(0o755)
        self.env['PATH'] = str(commands) + ':' + self.env['PATH']
        result = self.run_script('setup/common/ensure-dotfiles')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.desktop / 'portable').resolve(), self.portable)
        self.assertNotIn('arch-desktop.git', (self.home / 'clone-args').read_text())

    def test_both_profiles_receive_the_same_dependency(self):
        self.seed_portable()
        for profile in ['arch-workstation', 'arch-devbox']:
            target = self.desktop / 'setup' / profile
            target.mkdir()
            script = target / 'init'
            script.write_text('#!/bin/bash\nprintf "%s\\n" "$DOTFILES_DIR" "$ARCH_DESKTOP_DIR" "$PATH"\n')
            script.chmod(0o755)
            result = self.run_script('setup/boot.sh', profile)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(str(self.portable), result.stdout)
            self.assertIn(str(self.desktop / 'bin'), result.stdout)

    def test_boot_help_does_not_clone_or_link_dependencies(self):
        result = self.run_script('setup/boot.sh', '--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.desktop / 'portable').exists())
        self.assertFalse(self.portable.exists())

    def test_real_stow_links_configuration_from_both_repositories(self):
        if not shutil.which('stow'):
            self.skipTest('GNU Stow is required')
        env = dict(self.env, ARCH_DESKTOP_DIR=str(ROOT), DOTFILES_DIR=str((ROOT / 'portable').resolve()))
        result = subprocess.run(['bash', str(ROOT / 'setup/arch-workstation/stow')],
                                env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.home / '.config/hypr').exists(), False)
        self.assertEqual((self.home / '.config/zsh/.zshrc').resolve(), (ROOT / 'portable/zsh/.config/zsh/.zshrc').resolve())
        self.assertEqual((self.home / '.config/kanata/config.kbd').resolve(), (ROOT / 'kanata/.config/kanata/config.kbd').resolve())
        self.assertEqual((self.home / '.config/herdr/config.toml').resolve(),
                         (ROOT / 'portable/herdr/.config/herdr/config.toml').resolve())

    def test_link_migration_relocates_managed_desktop_targets_only(self):
        shutil.copy2(ROOT / 'setup/common/setup-desktop-links', self.desktop / 'setup/common/setup-desktop-links')
        self.seed_portable()
        (self.desktop / 'portable').symlink_to(self.portable)
        (self.desktop / 'hypr/.config/hypr').mkdir(parents=True)
        self.home.joinpath('.config').mkdir()
        managed = self.home / '.config/hypr'
        (self.portable / 'hypr/.config/hypr').mkdir(parents=True)
        managed.symlink_to(self.portable / 'hypr/.config/hypr')
        other = self.home / '.config/other'
        other.symlink_to(self.home / 'unrelated/missing')
        root_link = self.home / '.config/portable-root'
        root_link.symlink_to(self.portable)
        result = subprocess.run(['python3', str(self.desktop / 'setup/common/setup-desktop-links')],
                                env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(managed.resolve(), self.desktop / 'hypr/.config/hypr')
        self.assertEqual(os.readlink(other), str(self.home / 'unrelated/missing'))
        self.assertEqual(root_link.resolve(), self.portable)


    def test_exposed_command_uses_the_real_checkout_without_inherited_root(self):
        shutil.copy2(ROOT / 'setup/common/setup-desktop-links', self.desktop / 'setup/common/setup-desktop-links')
        self.seed_portable()
        (self.desktop / 'portable').symlink_to(self.portable)
        commands = self.desktop / 'bin'
        commands.mkdir()
        script = commands / 'root-check'
        script.write_text('#!/bin/bash\ncd "$(dirname "${BASH_SOURCE[0]}")/.."; pwd\n')
        script.chmod(0o755)
        existing = self.home / '.local/bin/user-command'
        existing.parent.mkdir(parents=True)
        existing.write_text('keep this command')
        result = subprocess.run(['python3', str(self.desktop / 'setup/common/setup-desktop-links')],
                                env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        env = dict(self.env)
        env.pop('ARCH_DESKTOP_DIR', None)
        result = subprocess.run([str(self.home / '.local/bin/root-check')], env=env,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), str(self.desktop))
        self.assertEqual(existing.read_text(), 'keep this command')

    def test_optional_background_packages_are_linked_from_their_own_checkout(self):
        if not shutil.which('stow'):
            self.skipTest('GNU Stow is required')
        backgrounds = self.home / 'backgrounds'
        (backgrounds / '.git').mkdir(parents=True)
        for package in ['backgrounds', 'theme-previews']:
            image = backgrounds / package / '.config' / package / 'image.png'
            image.parent.mkdir(parents=True)
            image.touch()
        result = subprocess.run(['bash', str(ROOT / 'scripts/stow/stow-backgrounds')], env=self.env,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for package in ['backgrounds', 'theme-previews']:
            self.assertEqual((self.home / '.config' / package / 'image.png').resolve(),
                             backgrounds / package / '.config' / package / 'image.png')

    def test_legacy_lazygit_theme_remains_local_when_portable_defaults_are_detached(self):
        shutil.copy2(ROOT / 'setup/common/setup-desktop-links', self.desktop / 'setup/common/setup-desktop-links')
        self.seed_portable()
        (self.desktop / 'portable').symlink_to(self.portable)
        managed = self.portable / 'lazygit/.config/lazygit'
        managed.mkdir(parents=True)
        (managed / 'config.yml').write_text('portable defaults')
        (managed / 'state.yml').write_text('local state')
        theme = self.home / '.config/theme/lazygit.yml'
        theme.parent.mkdir(parents=True)
        theme.write_text('desktop colors')
        config_dir = self.home / '.config/lazygit'
        config_dir.symlink_to(managed)
        result = subprocess.run(['python3', str(self.desktop / 'setup/common/setup-desktop-links')],
                                env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(config_dir.is_symlink())
        self.assertEqual((config_dir / 'config.yml').resolve(), theme)
        self.assertEqual((config_dir / 'state.yml').read_text(), 'local state')
        self.assertEqual((managed / 'config.yml').read_text(), 'portable defaults')

if __name__ == '__main__':
    unittest.main()
