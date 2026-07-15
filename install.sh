#!/usr/bin/env bash
# Athena installer — symlinks the skills into ~/.claude/skills/ so Claude Code auto-loads them
# in every project. Idempotent + reversible. Run once per machine after cloning.
#
#   ./install.sh              install (symlink skills → ~/.claude/skills/)
#   ./install.sh --uninstall  remove those symlinks (leaves the repo untouched)
set -euo pipefail

ATHENA="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST"

skills() { for d in "$ATHENA/skills"/*/; do [ -f "$d/SKILL.md" ] && basename "$d"; done; }

if [ "${1:-}" = "--uninstall" ]; then
  for s in $(skills); do
    link="$DEST/$s"
    if [ -L "$link" ]; then rm "$link"; echo "removed  $link"; fi
  done
  echo "Uninstalled. (Skills remain in $ATHENA/skills/)"
  exit 0
fi

for s in $(skills); do
  link="$DEST/$s"
  if [ -e "$link" ] && [ ! -L "$link" ]; then
    echo "SKIP  $link already exists and is NOT a symlink — move it aside first." >&2
    continue
  fi
  ln -sfn "$ATHENA/skills/$s" "$link"
  echo "linked  ~/.claude/skills/$s -> $ATHENA/skills/$s"
done

echo
echo "Done. Verify:  make validate"
echo "Then in Claude, the skills auto-trigger in any project; or /guardian-agent-foundations."
