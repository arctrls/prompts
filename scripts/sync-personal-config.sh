#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_SOURCE="$SCRIPT_DIR/codex"
AGENTS_SOURCE="$SCRIPT_DIR/agents"
CODEX_HOME="$HOME/.codex"
AGENTS_HOME="$HOME/.agents"

DRY_RUN=0
MODE="to-home" # to-home | from-home

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/sync-personal-config.sh [--from-home] [--dry-run] [--to-home]

Options:
  --from-home   Sync runtime home files into this repo (home -> repo)
  --to-home     Sync repo files into home (repo -> home, default)
  --dry-run     Show what would be synced without writing files
  --help        Show this help

This script manages declarative assets for:
  - ~/.codex/config.toml, ~/.codex/prompts, ~/.codex/skills
  - ~/.agents/skills

It intentionally ignores ~/.omx (runtime state, logs, and sessions).
USAGE

  exit 0
}

copy_file() {
  local source_path=$1
  local target_path=$2
  local label=$3

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "[dry-run] $label: ${source_path} -> ${target_path}"
    return
  fi

  if [[ ! -f "$source_path" ]]; then
    echo "[skip] $label: source missing: ${source_path}"
    return
  fi

  mkdir -p "$(dirname "$target_path")"
  cp -f "$source_path" "$target_path"
}

sync_full_dir() {
  local source_dir=$1
  local target_dir=$2
  local label=$3

  if [[ $DRY_RUN -eq 1 ]]; then
    if command -v rsync >/dev/null 2>&1; then
      rsync --delete --out-format='  %n' --dry-run -a "$source_dir" "$target_dir"
    else
      find "$source_dir" -type f -print0 | xargs -0 -I{} printf '  %s\n' "{}"
    fi
    return
  fi

  mkdir -p "$target_dir"
  if command -v rsync >/dev/null 2>&1; then
    rsync --delete -a "$source_dir" "$target_dir"
  else
    rsync_available=false
    find "$source_dir" -type f -print0 | while IFS= read -r -d '' file; do
      rel="${file#${source_dir}}"
      cp -f "$file" "$target_dir/$rel"
    done
  fi
}

sync_markdown_dir() {
  local source_dir=$1
  local target_dir=$2
  local include_dotfile=$3
  local label=$4

  if [[ ! -d "$source_dir" ]]; then
    echo "[skip] $label: source missing: ${source_dir}"
    return
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    if command -v rsync >/dev/null 2>&1; then
      if [[ "$include_dotfile" == "true" ]]; then
        rsync --delete --include='*/' --include='*.md' --include='.codex-system-skills.marker' --exclude='*' --out-format='  %n' --dry-run -a "$source_dir" "$target_dir"
      else
        rsync --delete --include='*/' --include='*.md' --exclude='*' --out-format='  %n' --dry-run -a "$source_dir" "$target_dir"
      fi
    else
      find "$source_dir" -type f \( -name '*.md' -o -name '.codex-system-skills.marker' \) -print
    fi
    return
  fi

  mkdir -p "$target_dir"
  if [[ "$include_dotfile" == "true" ]]; then
    rsync --delete --include='*/' --include='*.md' --include='.codex-system-skills.marker' --exclude='*' -a "$source_dir" "$target_dir"
  else
    rsync --delete --include='*/' --include='*.md' --exclude='*' -a "$source_dir" "$target_dir"
  fi
}

sync_codex_to_home() {
  copy_file "$CODEX_SOURCE/config.toml" "$CODEX_HOME/config.toml" "codex config.toml"
  sync_full_dir "$CODEX_SOURCE/prompts/" "$CODEX_HOME/prompts/" "codex prompts"
  sync_full_dir "$CODEX_SOURCE/skills/" "$CODEX_HOME/skills/" "codex skills"
}

sync_agents_to_home() {
  sync_full_dir "$AGENTS_SOURCE/skills/" "$AGENTS_HOME/skills/" "agent skills"
}

sync_codex_from_home() {
  copy_file "$CODEX_HOME/config.toml" "$CODEX_SOURCE/config.toml" "codex config.toml"
  sync_markdown_dir "$CODEX_HOME/prompts/" "$CODEX_SOURCE/prompts/" false "codex prompts"
  sync_markdown_dir "$CODEX_HOME/skills/" "$CODEX_SOURCE/skills/" true "codex skills"
}

sync_agents_from_home() {
  sync_markdown_dir "$AGENTS_HOME/skills/" "$AGENTS_SOURCE/skills/" false "agent skills"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --from-home)
      MODE="from-home"
      ;;
    --to-home)
      MODE="to-home"
      ;;
    --dry-run)
      DRY_RUN=1
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
  shift

done

if [[ "$MODE" == "to-home" ]]; then
  sync_codex_to_home
  sync_agents_to_home
else
  sync_codex_from_home
  sync_agents_from_home
fi
