# Herdr desktop app

Migration from `portable/herdr/.config/herdr/config.toml` for the Arch workstation.
The old TUI config and its helpers remain available for existing sessions.

Run from this checkout on the workstation:

```sh
bash setup/arch-workstation/setup-herdr-app-config
# With the desktop app running:
herdr-app do layout.switch --name dotfiles
herdr-app status
```

The installer copies `keys.json`, `settings.json`, and the personal `dotfiles`
layout into `${HERDR_APP_HOME:-~/.config/herdr-app}`. Each run first backs up
previous copies in a `.dotfiles-backup.*` directory there. These files replace
existing personal keys/settings in full; they are not merged. Other layouts,
mods, and runtime state stay in place. Subsequent edits here need another run
of the installer. Shipped layouts and mods are referenced, never overwritten.

The configuration was checked against the upstream
[configuration guide](https://github.com/herdrdev/herdr-app/blob/0ac92e4e9d5dea2097375c26e6a0cb194a75c2f0/defaults/AGENTS.md),
[key loader](https://github.com/herdrdev/herdr-app/blob/0ac92e4e9d5dea2097375c26e6a0cb194a75c2f0/src/keys.rs),
and [commands](https://github.com/herdrdev/herdr-app/blob/0ac92e4e9d5dea2097375c26e6a0cb194a75c2f0/docs/commands.md).
It has not been loaded in a running app here. Check `herdr-app status` and any
`keys.error`, `settings.error`, or `layout.error` on the workstation, especially
if its installed version differs. Try splits, navigation, and the sidebar
before closing real work. The reserved Ctrl+Alt+Shift+Escape resets the layout
and keys to the app defaults if needed.

## Keys

Press Ctrl+Space, release it, then press the next key. The app's GPUI key
loader accepts space-separated sequences (`ctrl-space t`); no TUI `prefix`
setting is needed. Ctrl+Space is consequently reserved for these sequences.
The keys file starts with Linux app defaults, removes bare Ctrl+1–9 and
Alt+1–9, and adds the migrated bindings. Terminal copy, paste, search, app
zoom, and the command palette retain their app defaults.

| After Ctrl+Space | Action |
|---|---|
| `t`, `r` | New / rename tab |
| Shift+L, `n`, `i` | Next tab |
| Shift+H, `o` | Previous tab |
| `1`–`9` | Select tab |
| `h`, `j`, `k`, `l` | Focus pane left / down / up / right |
| `c`, `z` | Close / zoom pane |
| `v` | Split right |
| `s`, `-` | Split down |
| `x`, Ctrl+J | Swap pane down |
| Ctrl+H, Ctrl+K, Ctrl+L | Swap pane left / up / right |
| Ctrl+T, Shift+R, Ctrl+W | New / rename / close space |
| Shift+K, Ctrl+O | Previous space |
| Shift+J | Next space |
| Ctrl+1–9 | Select space |
| `g`, Shift+S | Picker for tabs, spaces, and agents |
| Alt+N, Alt+P | Next / previous agent |
| `?`, Ctrl+S, `b` | Help / settings / toggle sidebar |
| `d`, Ctrl+D | Close the window; core terminals keep running |

Space closing uses the app's confirmation dialog. `c` uses native `pane.close`;
the old global `confirm_close` preference has no app setting. Closing a final
pane/tab can close its space. The old Ctrl+Q session-kill binding is deliberately
absent: closing the desktop window leaves core terminals alive.

## Settings and layout

Sound stays enabled and terminal clipboard writes are allowed. Following the
focused terminal's directory and opening unnamed tabs are native defaults.
The personal layout uses the shipped main layout structure with the sidebar
visible, pane gaps/padding between cards removed, square pane frames, and the
shipped pane header (which includes agent information).

These TOML preferences have no direct app setting and are **not migrated**:

| Old preference | App behavior / remaining work |
|---|---|
| `theme.name = "terminal"`, `auto_switch = false` | A desktop app has no host terminal palette to inherit. Theme/appearance remain app defaults; choose one in Settings. |
| `mouse_capture = true` | Terminal applications receive mouse events natively; Shift selects text. |
| `copy_on_select = true` | No equivalent preference; use Ctrl+Shift+C. |
| `confirm_close = true` | Native space/final-tab confirmation; no global pane-close setting. |
| `agent_panel_sort = "spaces"`, `status_indicators = "dots"`, sidebar `rows` | Shipped sidebar mods control ordering, status marks, and row contents. |
| `scrollback_limit_bytes = 50000000` | Terminal storage belongs to herdr-core; no equivalent in app settings. |
| `ui.toast.delivery = "system"` | The app uses its shipped toast UI; system delivery needs a custom toast mod. |
| `onboarding = false` | Welcome/onboarding state belongs to the app's runtime files. |

## Bindings still needing app extensions

These old shortcuts stay unbound rather than invoking TUI helpers against the
wrong application:

| After Ctrl+Space | Old action / reason |
|---|---|
| Shift+P | Rename pane; no native pane rename command. |
| Ctrl+A | Last pane; no native focus-history command. |
| Tab, Shift+Tab | Cycle panes; no native cyclic pane command. |
| Ctrl+R | Resize mode; use the app's draggable split dividers. |
| Alt+1–9 | Agent by index; native `agent.focus` requires a terminal ID. |
| `[` | Copy mode; the app supports selection and Ctrl+Shift+F search. |
| `e` | Edit scrollback; no native external-editor command. |
| Alt+R | Reload config; app files reload automatically. |
| `w` | Close pane while preserving an empty final tab; native close may close the space. |
| Ctrl+Q | Kill the old persistent session; the app/core have a different lifecycle. |
| `,` | Toggle system notifications and sound; the old helper edits TUI TOML. Use Settings → Alerts for sound. |
| `p` | Floating scratch shell; requires a terminal overlay mod. |
| Ctrl+N | Worktrunk checkout beside the project; the old helper calls the TUI CLI. |
| Ctrl+P | Open worktree; use the shipped space/worktree menu. |

The old bare `h/j/k/l` and Shift+J/K navigate-mode bindings have no matching
mode in the app and are omitted so terminal typing works normally. Disabled
old bindings (`close_tab`, `new_worktree`, `open_notification_target`) add no
shortcuts. New/open worktrees remain available through the app's menus, using
its own directory convention until a Worktrunk integration is added.
