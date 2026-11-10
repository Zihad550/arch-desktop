# arch-desktop

Personal Hyprland and Quickshell desktop, Arch desktop installers, themes, and tests.
Portable shell, editor, Git, and agent configuration lives in
[dotfiles](https://github.com/Zihad550/dotfiles).

## Install

Start from base Arch Linux with Git installed, as your normal user. Every
machine starts from dotfiles, which clones this repo for the Arch targets:

```sh
git clone https://github.com/Zihad550/dotfiles.git ~/dotfiles
~/dotfiles/setup/boot.sh arch-workstation
# Or, on the development machine:
~/dotfiles/setup/boot.sh arch-devbox
```

`~/arch-desktop/setup/boot.sh <target>` still works from an existing checkout.
Both profiles install the shared desktop. The workstation is a remote-development
client; the devbox adds development tools, Docker and SSH. Headless installers
(Ubuntu, Proxmox) and the setup helpers they share with these profiles live in
dotfiles `setup/`.

Setup clones a missing `~/dotfiles` checkout and preserves an existing checkout.
`DOTFILES_DIR` can select another portable checkout. `portable/` is an ignored
link to that dependency; configuration is not copied between repositories.
`ARCH_DESKTOP_DIR` selects this checkout for scripts that accept it.
The selected machine profile remains `DOTFILES_PROFILE`.

DevVM consumes only the portable dotfiles repo. Its shell and skills bootstrap
stay there; a VM does not need this repository.

## Existing machines

Keep both checkouts. Pulling only dotfiles after this split removes desktop
files, so obtain this repo first. Then run:

```sh
~/arch-desktop/setup/common/ensure-dotfiles
~/arch-desktop/setup/common/setup-desktop-links --dry-run
~/arch-desktop/setup/common/setup-desktop-links
```

The Arch installers call shared setup helpers in dotfiles, so pull dotfiles too
before rerunning an installer: `git -C ~/dotfiles pull`.

This repairs managed user links whose targets moved and exposes desktop
commands in `~/.local/bin`. Existing unrelated commands are preserved. Open a
new shell to load the updated PATH. Rerun your profile installer to apply any
system-owned service updates; the link migration does not restart the desktop.

## Develop

Run `setup/common/ensure-dotfiles` before testing. Tests for desktop code and
host provisioning live here; portable tooling tests live with dotfiles.

```sh
node --test --test-isolation=none tests/launcher/*.test.js tests/lock/*.test.js
python -m unittest discover -s tests/quickshell -p 'test_*.py'
```

Live compositor, microphone, power, and hardware checks require the actual host.
Historical issue references remain in [dotfiles Issues](https://github.com/Zihad550/dotfiles/issues).
Create new desktop work in this repository.
Task specs and verification evidence belong in GitHub Issues; usage and recovery
guides, the glossary, and architectural decisions remain beside the code.
