#!/bin/sh
# Copy the generated Codex agent profiles into $CODEX_HOME/agents.
set -eu

src="$(cd "$(dirname "$0")/../codex" && pwd)"
dest="${CODEX_HOME:-$HOME/.codex}/agents"
mkdir -p "$dest"

for f in "$src"/*.toml; do
  [ -e "$f" ] || { echo "no profiles in $src; run build.py first" >&2; exit 1; }
  target="$dest/$(basename "$f")"
  if [ -e "$target" ] && ! cmp -s "$f" "$target"; then
    cp "$target" "$target.bak"
    echo "backed up $target -> $target.bak"
  fi
  cp "$f" "$target"
  echo "installed $target"
done
