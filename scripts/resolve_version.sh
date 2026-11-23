#!/usr/bin/env bash
set -euo pipefail
MODE="${1:-latest}"
if [[ "$MODE" == "latest" ]]; then
  # Official repeater release tags only, not companion or dev.
  REMOTE='https://github.com/meshcore-dev/MeshCore.git'
  TAG="$(git ls-remote --refs --tags "$REMOTE" 'refs/tags/repeater-v*' \
      | sed -n 's|.*refs/tags/||p' \
      | grep -E '^repeater-v[0-9]+\.[0-9]+\.[0-9]+$' \
      | sort -V | tail -n 1)"
  test -n "$TAG" || { echo 'Cannot determine latest official repeater tag' >&2; exit 1; }
else
  if [[ ! "$MODE" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Invalid version: $MODE; use latest or e.g. 1.18.0" >&2; exit 1
  fi
  TAG="repeater-v${MODE}"
  git ls-remote --exit-code --refs --tags https://github.com/meshcore-dev/MeshCore.git "refs/tags/${TAG}" >/dev/null || {
    echo "Official repeater tag ${TAG} does not exist" >&2; exit 1;
  }
fi
printf 'Selected official tag: %s\n' "$TAG"
if [[ -n "${GITHUB_OUTPUT:-}" ]]; then echo "tag=$TAG" >> "$GITHUB_OUTPUT"; fi
