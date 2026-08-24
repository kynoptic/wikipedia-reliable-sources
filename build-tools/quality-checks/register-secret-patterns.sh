#!/usr/bin/env bash
# Register this repo's git-secrets patterns.
#
# git-secrets stores patterns in .git/config, which is not cloned. Run this once
# per clone, per machine. The pre-commit scan refuses to run until you do.
set -euo pipefail

command -v git-secrets >/dev/null 2>&1 || {
  echo "git-secrets is not installed. On macOS: brew install git-secrets" >&2
  exit 1
}

git config --unset-all secrets.patterns 2>/dev/null || true
git config --unset-all secrets.allowed 2>/dev/null || true
git config --unset-all secrets.providers 2>/dev/null || true

git secrets --register-aws >/dev/null

# Added through git config rather than `git secrets --add`, which reads the
# leading dashes as option flags. The literal is split across two lines so this
# file does not match the very pattern it registers and block its own commit.
header_start='BEGIN'
git config --add secrets.patterns "${header_start}.*PRIVATE KEY-----"

git secrets --add 'ghp_[a-zA-Z0-9]{36}' >/dev/null
git secrets --add 'gho_[a-zA-Z0-9]{36}' >/dev/null
git secrets --add 'glpat-[a-zA-Z0-9_-]{20,}' >/dev/null

# op:// URIs are pointers to a secret, not the secret, and are the documented
# house pattern — so they are deliberately not a detection pattern here.

# This script spells out the patterns it registers, and .gitallowed spells out the
# patterns it exempts, so both match themselves. Exempt them here rather than in
# .gitallowed, which git-secrets fails to read when the repo path contains spaces.
git secrets --add --allowed 'register-secret-patterns\.sh' >/dev/null
git secrets --add --allowed '^\.gitallowed:' >/dev/null

git secrets --add --allowed '\.example$' >/dev/null
git secrets --add --allowed '\.example\..*$' >/dev/null
git secrets --add --allowed 'YOUR_[A-Z_]+_HERE' >/dev/null
git secrets --add --allowed '<[A-Z_]+>' >/dev/null
git secrets --add --allowed 'REPLACE_ME' >/dev/null

echo "Registered $(git config --get-all secrets.patterns | wc -l | tr -d ' ') patterns."
