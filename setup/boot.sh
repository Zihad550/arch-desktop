#!/usr/bin/env bash

# Entrypoint for first-time setup.
#   ./boot.sh             pick a target from a menu
#   ./boot.sh <target>    run it directly (e.g. arch-workstation, arch-devbox)
#   ./boot.sh --help      list targets

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Setup directories that have an init entrypoint.
targets() {
   local init
   for init in "$SCRIPT_DIR"/*/init; do
      basename "$(dirname "$init")"
   done
}

list_targets() {
   echo "Available targets:"
   targets | sed 's/^/  - /'
}

dispatch() {
   local target="$1"
   local dir="$SCRIPT_DIR/$target"

   if [[ "$target" == */* || ! -f "$dir/init" ]]; then
      echo "Error: '$target' is not a setup target" >&2
      list_targets
      exit 1
   fi

   export ARCH_DESKTOP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
   DOTFILES_DIR="$("$SCRIPT_DIR/common/ensure-dotfiles")"
   export DOTFILES_DIR
export PATH="$ARCH_DESKTOP_DIR/bin:$ARCH_DESKTOP_DIR/bin/voxtype:$DOTFILES_DIR/bin:$PATH"
   "$DOTFILES_DIR/setup/common/check-machine-profile" "$target"
   echo "Running: $dir/init"
   exec "$dir/init"
}

menu() {
   local options name
   mapfile -t options < <(targets)
   PS3="Setup to run (number): "
   select name in "${options[@]}"; do
      [[ -n "$name" ]] && dispatch "$name"
      echo "Pick a number from 1 to ${#options[@]}." >&2
   done
   exit 1 # stdin closed without a choice
}

case "${1:-}" in
   -h | --help)
      list_targets
      ;;
   "")
      # From /dev/tty, so the menu also works when this script is piped in.
      if ! { : </dev/tty; } 2>/dev/null; then
         echo "No terminal for the menu; pass a target:" >&2
         list_targets
         exit 1
      fi
      menu </dev/tty
      ;;
   *)
      dispatch "$1"
      ;;
esac
