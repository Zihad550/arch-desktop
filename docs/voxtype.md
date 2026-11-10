# Voxtype integration

Voxtype provides dictation on `arch-workstation` and `arch-devbox`. Each
machine records from its own microphone and inserts text into its own
Hyprland session. The bar shows recording and transcription state; left-click
opens `voxtype configure`, and right-click opens the local configuration.

## Configuration

Starter defaults select Parakeet with `parakeet-tdt-0.6b-v3`, with media pausing
and audible feedback disabled. Super+S and Super+Ctrl+X toggle recording.

Setup detaches configs previously symlinked into the repo and seeds a missing
config from the tracked defaults. Existing regular local configs, downloaded
models, and backend choices are preserved. A config still symlinked to tracked
defaults receives changes on pull before setup detaches it. Edit local settings through
`voxtype configure`; setup reruns do not migrate them to new defaults.

The installer enables ONNX for Parakeet. For Whisper, a new installation may
try Vulkan when an ICD is installed; setup falls back to CPU if the GPU switch
or service startup fails. Actual transcription still needs a microphone check.
Other engines are not supported by this installer.

After restarting the user service, setup waits up to 30 seconds for
`voxtype status` to report `idle`; systemd can report an active service before
model initialization finishes. Setup removes the runtime state file before
restarting so an old `idle` cannot satisfy that check. Disabled state reporting
fails setup because recording controls and the bar depend on it. Package,
model-download, backend-switch, service, and readiness failures fail the setup
step so it can be retried. Readiness failures follow the same Whisper CPU
recovery policy as service-start failures.

The integration adapts Omarchy's installer, recording bindings, configuration
controls, and status follower at
[commit 65c0f330](https://github.com/basecamp/omarchy/tree/65c0f330), with this
repository's Quickshell bar module. Installer CLI behavior was checked against
Voxtype 1.1.0 and its [model setup source](https://github.com/peteonrails/voxtype/blob/6d2fc6ddbf791ac00d6a54dc002664010c16b100/src/setup/mod.rs)
and [service setup source](https://github.com/peteonrails/voxtype/blob/6d2fc6ddbf791ac00d6a54dc002664010c16b100/src/setup/systemd.rs).

## Existing-machine rollout

After transferring or pulling these repo changes, run the following as your normal user in a terminal inside each machine's Hyprland session. Both Arch profiles use the same commands. Their existing setup must already have configured the Omarchy package repository.

```sh
cd ~/arch-desktop
bash setup/common/setup-voxtype
hyprctl reload
df-qs-restart dotfiles
systemctl --user status voxtype.service --no-pager
```

If `voxtype-bin` is unavailable to pacman, refresh the repo configuration and package databases first:

```sh
bash setup/arch-workstation/setup-omarchy-repos
sudo pacman -Syu
bash setup/common/setup-voxtype
```

Do not run the entire profile installer just to add dictation. No remote microphone transport is configured.

## Modifier suppression during output

Super+S stops recording on key press, so Super can still be held when Voxtype starts typing. Hyprland merges modifiers across keyboards, so a typed `h` would fire the SUPER+H bind and move focus out of the text field. The seed config's `pre_output_command` enters the `voxtype_suppress` submap, which has no Super binds, and `post_output_command` resets it. Press F12 to leave the submap if Voxtype dies mid-output. In Lua-config mode `hyprctl dispatch` evaluates Lua, so the hooks dispatch `hl.dsp.submap(...)`. The upstream `voxtype setup compositor hyprland` integration is not used: it writes hyprlang config and a recording submap that would swallow the Super+S stop key.

Existing local configs are not rewritten. Add both hook lines under `[output]` by hand.

## Check recording

1. Focus a text field, press and release Super+S to start recording, say a short sentence, then press Super+S again to stop. Confirm the text appears and the recording/transcription indicator returns to idle. Repeat in a browser text field while holding Super after the stop press; the field must keep focus and `hyprctl submap` must report `default` afterwards.
2. Press Super+Space and confirm the launcher opens immediately. Holding the shortcut must not start dictation.
3. Start and stop another recording with Super+Ctrl+X. Confirm Super+Ctrl+V still opens clipboard history.
4. Play media and record again. With the starter defaults, media keeps playing during recording and audible feedback is off.
5. While the indicator is visible, left-click it to open `voxtype configure`; right-click to edit the local config. Configuration is also always available from a terminal through `voxtype configure`.
6. Rerun the standalone installer. Confirm local settings and downloaded models remain intact.

For startup or transcription failures, inspect `journalctl --user -u voxtype.service -n 100 --no-pager`. For Whisper only, to select CPU explicitly:

```sh
sudo voxtype setup gpu --disable
voxtype setup systemd
systemctl --user restart voxtype.service
```
