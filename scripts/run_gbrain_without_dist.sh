#!/usr/bin/env bash
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "usage: scripts/run_gbrain_without_dist.sh <gbrain command...>" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
HIDDEN="$ROOT/.dist-gbrain-hidden"
moved=false

restore_dist() {
  if [[ "$moved" == true && -d "$HIDDEN" ]]; then
    mv "$HIDDEN" "$DIST"
  fi
}
trap restore_dist EXIT INT TERM

if [[ -e "$HIDDEN" ]]; then
  echo "refusing GBrain run: temporary path already exists: $HIDDEN" >&2
  exit 1
fi
if [[ -d "$DIST" ]]; then
  mv "$DIST" "$HIDDEN"
  moved=true
fi

cd "$ROOT"
"$@"
