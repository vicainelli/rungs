#!/bin/sh
# Copy the generated opencode agents and the orchestrate skill into $XDG_CONFIG_HOME/opencode.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
dest="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"

install_file() {
  target="$2"
  mkdir -p "$(dirname "$target")"
  if [ -e "$target" ] && ! cmp -s "$1" "$target"; then
    cp "$target" "$target.bak"
    echo "backed up $target -> $target.bak"
  fi
  cp "$1" "$target"
  echo "installed $target"
}

for f in "$root"/opencode/agents/*.md; do
  [ -e "$f" ] || { echo "no agents in $root/opencode/agents; run build.py first" >&2; exit 1; }
  install_file "$f" "$dest/agents/$(basename "$f")"
done
install_file "$root/skills/orchestrate/SKILL.md" "$dest/skills/orchestrate/SKILL.md"
