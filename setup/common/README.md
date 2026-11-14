# Shared setup

`setup/common/` owns setup behavior used across box directories. A script stays
here when it is intended to be reusable, even if only one box calls it today.
The box wrappers own distro-specific installation, values, ordering, and local
rationale.

The scripts are authoritative for supported inputs and defaults. This README
explains why the shared behavior has its current shape. Script comments point
here when the explanation does not belong beside the command it protects.

Helpers that headless boxes also use (machine profile, SSH hardening, DNS,
Tailscale, power, firewall library, hardware detection and Herdr) live in
dotfiles' `setup/common/`. Installers here call them through
`portable/setup/common/`; their rationale is in
[dotfiles `setup/common/README.md`](https://github.com/Zihad550/dotfiles/blob/main/setup/common/README.md).

## Inventory

### Shared Setup Scripts

| Component | Purpose | Current callers |
| --- | --- | --- |
| [`setup-devvm`](setup-devvm) | Installs QEMU, devvm and Lima, and gives new VMs the `shell` layer. | Arch Workstation, Arch devbox |
| [`setup-dirmngr`](setup-dirmngr) | Configures GnuPG DNS resolution before key retrieval. | Arch devbox |
| [`setup-first-run-sudo`](setup-first-run-sudo) | Installs and removes the temporary passwordless-sudo drop-in used during setup. | Arch Workstation, Arch devbox |
| [`setup-greeter`](setup-greeter) | Installs and enables the pinned Greeter, retiring the display manager it replaces. | Arch Workstation, Arch devbox |
| [`setup-go-timer`](setup-go-timer) | Installs the pinned go-timer GitHub release without Go or mise. | Arch Workstation, Arch devbox |
| [`setup-idle-ladder`](setup-idle-ladder) | Selects per-box Idle Ladder timing data outside the stow tree. | Arch Workstation, Arch devbox |
| [`setup-kanata`](setup-kanata) | Installs Kanata (Arch only, via yay) and runs it as a system service on the saved profile selection. | Arch Workstation, Arch devbox |
| [`setup-power-button-suspend`](setup-power-button-suspend) | Makes a short power-button press suspend and a long press power off. | Arch Workstation, Arch devbox |
| [`setup-rootless-docker`](setup-rootless-docker) | Replaces rootful Docker with a per-user daemon. | Arch devbox |
| [`setup-mise`](setup-mise) | Installs mise from pacman, with `usage` for its completions. | Arch devbox |
| [`setup-skills`](../../portable/setup/common/setup-skills) | Installs the shared agent skill set. | Arch devbox, Ubuntu, and shell-layer VM setup |
| [`setup-snapper`](setup-snapper) | Applies the root filesystem snapshot-retention policy. | Arch devbox |
| [`setup-sudo-password-feedback`](setup-sudo-password-feedback) | Shows asterisks while a user types a sudo password. | Arch Workstation, Arch devbox |
| [`setup-ts-serve`](setup-ts-serve) | Grants passwordless `ts-serve` through a validating root wrapper. | Arch devbox |
| [`setup-voxtype`](setup-voxtype) | Installs local voice dictation, its model, and user service. | Arch Workstation, Arch devbox |
| [`sync-devvm-agents`](sync-devvm-agents) | Copies the agents' dotfiles settings into devvm's agent store. | `setup-devvm`, `df-update-daily` |

### Support and package input

- [`packages/`](packages) holds executable package-command lists, not Shared
  Setup Scripts. A list lands here once more than one box runs it, on the same
  rule as the scripts above — otherwise it stays in the Box Wrapper that owns
  it (`arch-workstation/packages/pacman-apps` is that box's app layer, and
  `arch-devbox` keeps its own copy).

  | List | Installs | Current callers |
  | --- | --- | --- |
  | [`pacman-base`](packages/pacman-base) | The development CLI toolkit, fonts, coreutils replacements and gcc. | Arch devbox |
  | [`flatpak-packages`](packages/flatpak-packages) | Flatpak applications. | Arch Workstation (Arch devbox keeps it off) |
  | [`quickshell-packages`](packages/quickshell-packages) | The shell binary and every external program its QML shells out to. | Arch Workstation, Arch devbox |

## go-timer

Both Arch profiles run `setup-go-timer` to install the Linux x86-64 binary from
[go-timer v0.1.2](https://github.com/Zihad550/go-timer/releases/tag/v0.1.2) into
`~/.local/bin/go-timer`. The shell exposes it as `timer`. No Go toolchain is
needed. The installer verifies the pinned SHA-256 before extracting and removes
the old Go-installed copies that would shadow it. To update, change both the
version and checksum in the installer. Existing machines can run
`setup/common/setup-go-timer` directly.

## devvm

Both Arch profiles run `setup-devvm` for [devvm](https://devvm.dev) sandbox
VMs. It installs `qemu-base`, `minisign` and `rsync` with pacman, then devvm's
latest release with devvm's own install script. That script also installs Lima,
which Arch doesn't package, into `~/.local`. Before it runs, `SHA256SUMS` must carry
devvm's minisign signature and match `install.sh`; with minisign installed, the
install script checks the devvm binary the same way.

The install runs only when `devvm` or `limactl` isn't on PATH, so update with
`devvm upgrade`. Lima is in that check because the install script can succeed
when one of its dependency fixes fails. When `/dev/kvm` isn't writable, the
install script adds the user to the `kvm` group, which applies from the next
login. Every run sets the `shell` layer as the default for new VMs, and fails
if stow hasn't linked the layers folder yet (see
[`portable/devvm/README.md`](../../portable/devvm/README.md)).

It ends by running `sync-devvm-agents`, which copies the git-tracked files of
the `claude`, `codex` and `opencode` packages into devvm's agent store. It doesn't
use `devvm agent import`, which skips stow's links and would replace the logins
VMs saved with the host's. Skills are installed inside each shell-layer VM by
[`portable/setup/devvm/setup-skills`](../devvm/setup-skills), using the cloned dotfiles
and skills repos; see [`portable/devvm/README.md`](../../portable/devvm/README.md). The sync no
longer copies host-installed skills.

The settings store is a snapshot. On `arch-workstation`, `df-update-daily`
refreshes only devvm settings and VM tools, without installing host skills or
updating mise. Other profiles refresh them after the host's `setup-skills` when
`devvm` is on PATH; otherwise run `setup/common/sync-devvm-agents` and
`portable/bin/df-devvm-update`. After the sync, `df-update-daily` runs
`portable/bin/df-devvm-update`, which moves every VM to the newest shared
tools; see `portable/devvm/README.md` "Updating from the host". Restart the
VMs to see new settings. Copied settings keep host paths, such as Claude
Code's hooks in `~/.claude/hooks` and Codex's project and plugin paths; those
that don't exist in a VM fail there.

Existing machines can run `setup/common/setup-devvm` directly.

## Boot Branding

`boot-branding` installs the pinned Plymouth theme and keeps it aligned with
the pinned SDDM theme. It adds Plymouth to the configured initramfs hook chain
and adds `splash` to GRUB. If the host has `/etc/kernel/cmdline`, the same
arguments are written there because `mkinitcpio` uses that file when building a
UKI. The command-line update also adds `initramfs_async=0`, matching Omarchy's
Plymouth workaround for asynchronous UKI unpacking.

It also sets `GRUB_DISABLE_BOOTNEXT=true` unless `/etc/default/grub` already
sets it: GRUB 2.16 adds a menu entry for every firmware boot entry, including
ones left behind by earlier installs.

A rerun compares everything it would install with the live files and stops
when they all match: the initramfs and `grub.cfg` were already built from them,
so it skips the backup and both rebuilds. A hand edit to `/etc/default/grub`
therefore needs its own `grub-mkconfig -o /boot/grub/grub.cfg`.

### Duplicate "Arch Linux" entries

archinstall with GRUB and UKIs writes the kernel parameters, `cryptdevice=…`
included, only to `/etc/kernel/cmdline`, adds `/etc/grub.d/15_uki` (GRUB's
`uki` command), and turns off `10_linux`. It leaves `GRUB_CMDLINE_LINUX` empty.
Without UKIs it writes those parameters to `GRUB_CMDLINE_LINUX` instead.

A `grub` package upgrade reinstalls `10_linux` as executable, so the next
`grub-mkconfig` lists each kernel twice under the same name: the regular entry
and the UKI. The regular entry, and every grub-btrfs snapshot, boot with
`/etc/default/grub`'s command line; on an encrypted root they cannot unlock the
disk until `GRUB_CMDLINE_LINUX` carries the same `cryptdevice=…` as
`/etc/kernel/cmdline`. `GRUB_ENABLE_CRYPTODISK` is not needed: archinstall
keeps `/boot` on the unencrypted ESP.

Once the regular entry boots, hide the UKI one:

```sh
sudo mv /etc/grub.d/15_uki /root/15_uki.disabled
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

Setup leaves `15_uki` alone. This repo does not install it, and on a machine
whose regular entry cannot unlock the disk it is the only entry that boots.

## First-run sudo

A full install runs for longer than sudo's timestamp lifetime, so without help
it stops partway through to ask for a password again — sometimes behind the live
log panel, where the prompt is invisible. `setup-first-run-sudo` writes a
drop-in granting passwordless `systemctl`, `ufw`, `snapper` and `modprobe`, and
the init's exit trap calls it again with `--remove`.

Those grants are broad; `systemctl` alone is close to root-equivalent. That is
tolerable only because the file is temporary, which makes its removal the part
that matters. Two things protect it. The drop-in permits exactly one cleanup
command, `rm -f` on its own path, so the teardown never needs a password — which
is why `--remove` must spell that command identically. And the file is syntax
checked with `visudo -c` before installation, because a malformed drop-in breaks
every subsequent sudo, including the one that would delete it.

It is not the place to add a command merely to silence one prompt. A step that
sudoes once or twice should let sudo's ordinary credential cache cover it; see
"Serving dev ports" for what widening this list actually costs.

The cache still expires when one step runs longer than its five minutes without
calling sudo, such as a long AUR build before yay's final `sudo pacman`. So the
Arch `init`s also start a keep-alive right after this drop-in is written: a
background `sudo -n -v` every minute that refreshes the credential the user
already typed and grants nothing new. It never prompts, and the installer stops
it on exit, on an error and on Ctrl-C.

## Serving dev ports

`ts-serve` (in `portable/zsh/.config/zsh/aliasrc`) publishes a local dev port on the
tailnet. `tailscale serve` needs the tailscaled local API, which means root.

The obvious grant is `tailscale set --operator=$USER`, but that is a daemon-wide
pref: it hands the user the whole local API, so `tailscale up`, `down` and `set`
also stop needing root. A sudoers rule on `tailscale serve *` is narrower and
still too wide — every `serve` subcommand comes with it, including serving a
filesystem path off this box.

So the rule points at `/usr/local/bin/ts-serve-helper` instead. The helper takes
a port and an optional scheme, rejects surplus arguments and everything that is
not a port number or `http`/`https`, and composes the tailscale command itself;
the caller never supplies a URL or a flag. It is root-owned, so the user who
benefits from the rule cannot widen it by editing the helper.

The port glob in the sudoers file is not load-bearing. A sudoers `*` matches
whitespace and much more than a digit string, so it is a coarse prefilter — the
helper is the boundary that actually validates. The username interpolated into
the rule is checked for the same reason: `visudo -c` rejects a malformed file,
not a well-formed line someone smuggled in through `TS_SERVE_USER`.

The serve runs in the foreground, so Ctrl+C is the teardown and the rule never
has to permit `tailscale serve off`. A serve whose terminal is SIGKILLed can
outlive it; clear that with `sudo tailscale serve reset`.

Both wrappers install it during setup. It is inert on a box without tailscale.

Whether `tailscale serve` needs root at all is a per-box fact, not a documented
constant: Tailscale's own examples run it unprivileged, which holds once
`OperatorUser` is set. On these boxes it is unset, and `tailscale serve` fails
with `Access denied: serve config denied`. `tailscale serve status` succeeds
unprivileged either way — the socket is world-readable — so it does not answer
the question.

## Greeter

`setup-greeter` installs SDDM and removes the GDM these boxes used to run. It
first installs and rebuilds the pinned Omarchy Plymouth theme through the
repository's existing GRUB and `mkinitcpio` configuration, then installs the
SDDM theme, its minimal Wayland compositor config, and the Qt6 runtime pieces
that load them. The vendored sources and their upstream pins live in
[`greeter/`](greeter) and [`boot-branding/`](boot-branding), so setup is
independent of the ignored `resources/omarchy` checkout.

Boot setup rejects an unknown hook family or missing GRUB configuration before
changing live files. It preserves existing hooks and kernel arguments, keeps a
timestamped backup under `/var/lib/dotfiles/greeter-backups/`, and rolls back
when either boot rebuild fails. `df-boot-branding-set` accepts six-digit RGB
colors and a regular PNG logo, synchronizes Plymouth and SDDM, and rebuilds the
boot artifacts. `df-boot-branding-reset` restores both pinned defaults.

The order inside it is load-bearing: both units claim the
`display-manager.service` alias, so gdm is disabled before sddm is enabled —
and sddm is enabled before gdm is removed, so a failure in between leaves a
box that still boots. The enable is forced and the removal is non-fatal for the
same reason: every state a half-finished run can leave behind has to be
repairable by running it again.

The Greeter does not own the Desktop Keyring. The setup removes SDDM's
`pam_gnome_keyring` auth and password hooks, while the session creates a
passwordless default keyring and `gcr-ssh-agent.service` serves SSH keys after
login. Existing keyring files are preserved on reruns; the boundary is recorded
in [ADR 0022](../../docs/adr/0022-sddm-does-not-own-the-desktop-keyring.md).

The Greeter is password-only and remembers one account. `GREETER_USER` selects
that account explicitly. Without it, setup uses a non-root `SUDO_USER`, then
the invoking non-root account. It refuses root, missing accounts, and an
ambiguous multi-user system. It writes the selected account and
the selected Omarchy-compatible session to SDDM's state, then enables the managed autologin drop-in
when `/etc/crypttab` contains a non-comment entry or the running root is
encrypted. The latter covers `cryptdevice=` and `rd.luks.*` initramfs boots.
An absent or empty crypttab on an unencrypted-root machine removes that
drop-in without touching other SDDM configuration.

This policy runs after the Boot Branding rebuild and Greeter files install. It
does not add Omarchy's first-owner or one-shot provisioning.

The system authentication lockout policy runs after the Greeter installs its
PAM files. It applies ten failed attempts and a 120-second unlock window to
`system-auth` and SDDM's autologin stack, which covers TTY login and sudo while
keeping the Session Lock's tally and service separate. It preserves unrelated
`faillock.conf` settings and keeps timestamped recovery copies under
`/var/lib/dotfiles/auth-backups/`. The policy is recorded in [ADR 0026](../../docs/adr/0026-system-auth-lockout-policy.md).

`df-greeter-refresh` reapplies the pinned files. `df-greeter-reset` removes
only this repository's SDDM overrides and returns to stock behavior; neither
command restarts SDDM or logs out the current session. The decision is recorded
in [ADR 0024](../../docs/adr/0024-pinned-omarchy-greeter.md), which supersedes
[ADR 0020](../../docs/adr/0020-greeter-stays-stock-themed.md).
The copy-paste recovery and host-only checks are in
[Greeter recovery and host verification](../../docs/greeter-recovery.md).

## Agent skills

`setup-skills` uses the `skills` CLI as the owner of the global skill store.
Re-running it synchronizes the declared set. Add upstream skills to the
appropriate install block; add repository-owned skills to
`github.com/Zihad550/skills` before listing them here.

Update skills by re-running `setup-skills`, as `df-update-daily` does on profiles
other than `arch-workstation` before it
syncs devvm's settings store (see "devvm"). Inside a shell-layer VM, run
`bash /opt/dotfiles/setup/devvm/setup-skills` instead. Avoid
`skills update -g`: it reinstalls without `--agent`, so each updated skill is
linked into every detected agent. That includes `~/.claude/skills`, which
duplicates skills the Claude plugin already ships (e.g. mattpocock's).

It also installs the Claude Code mods in `portable/claude/.claude/mods` (a local
marketplace named `dotfiles-mods`) when `claude` is on `PATH`. Claude Code reads
them in place, so edits need only `/reload-plugins`. `stow-ai` links the local
marketplace at `~/.claude/mods`. The installed mods are `drafts` (draft previews)
and `lazy-diff` (Git review and file staging via `/lazy-diff`).

