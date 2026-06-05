#!/usr/bin/env bash
# Install the content-repurposer skills into your Claude Code skills directory.
# Default target: ~/.claude/skills/
# Pass an explicit target dir as $1 to override (e.g. ./install.sh ~/my/skills).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS=(linkedin-write twitter-write newsletter-write github-page-write medium-write substack-write repurpose-all)

TARGET="${1:-${HOME}/.claude/skills}"

echo "Repo:    ${REPO_ROOT}"
echo "Target:  ${TARGET}"
echo

mkdir -p "${TARGET}"

for skill in "${SKILLS[@]}"; do
  src="${REPO_ROOT}/skills/${skill}"
  dst="${TARGET}/${skill}"
  if [[ ! -d "${src}" ]]; then
    echo "skip ${skill} (not found at ${src})"
    continue
  fi
  ln -sfn "${src}" "${dst}"
  echo "linked  ${dst} -> ${src}"
done

echo
echo "Done. Restart your Claude Code session to load the skills."
echo "Then invoke any of: ${SKILLS[*]}"
