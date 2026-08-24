#!/usr/bin/env bash
# Pre-commit secret scan.
#
# git-secrets keeps its patterns in .git/config, which is not cloned. A fresh
# checkout therefore runs the scan against an empty pattern set, matches nothing,
# and reports success — the one failure mode a secret gate must not have. Refuse
# loudly instead, so an unconfigured clone is visible rather than silently open.
set -euo pipefail

if [ "$(git config --get-all secrets.patterns 2>/dev/null | wc -l | tr -d ' ')" -eq 0 ]; then
  echo "No git-secrets patterns are registered in this clone." >&2
  echo "The scan would pass every commit. Register them with:" >&2
  echo "    ./build-tools/quality-checks/register-secret-patterns.sh" >&2
  exit 1
fi

exec git secrets --pre_commit_hook -- "$@"
