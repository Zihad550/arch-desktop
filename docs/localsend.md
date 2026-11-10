# LocalSend sharing

LocalSend sharing is available on `arch-workstation`. Apply it using the
steps in [the workstation guide](../setup/arch-workstation/README.md).
Receiving is opened on demand; LocalSend does not start at login.

Setup allows incoming TCP and UDP on port 53317 from any source, matching
Omarchy. This also applies on public networks while LocalSend is listening.

## Desktop behavior

Share appears in the Launcher's `?` provider list. `Super+Alt+S` opens it
directly; `Super+Ctrl+S` keeps its existing Suspend action. The four actions
are also searchable in the main Launcher.

Clipboard sharing sends text as a temporary `.txt` file. Omarchy does not
detect clipboard images or give them an image filename; its untyped capture
can write binary data into that `.txt` file. This port requests text explicitly
and reports empty or unsupported clipboard content. Temporary clipboard files
remain for system cleanup after a successful launch because LocalSend may hand
the transfer to an existing process.

File and folder actions use the desktop portal chooser. Cancellation does
nothing. Chooser and launch failures produce an error notification. Paths stay
separate arguments, including filenames with spaces or newlines. Nautilus
sharing supports local paths and uses the same helper.

Setup preserves LocalSend preferences. Runtime sharing integrations are gated
on `DOTFILES_PROFILE=arch-workstation`.

## Upstream reference

Ported from Omarchy commit `9c5482c58dbe4974de337450754885083c91eada`.
The upstream license is retained at
`setup/arch-workstation/localsend/LICENSE.omarchy`.

- `resources/omarchy/bin/omarchy-menu-share`: clipboard capture, file/folder
  selection, and detached sending.
- `resources/omarchy/default/omarchy/omarchy-menu.jsonc`: four Share actions.
- `resources/omarchy/default/hypr/bindings/utilities.lua`: Share shortcut.
- `resources/omarchy/default/hypr/apps/localsend.lua`: window rules.
- `resources/omarchy/default/nautilus-python/extensions/localsend.py`:
  Nautilus sharing.
- `resources/omarchy/install/config/firewall.sh`: incoming port allowances.
