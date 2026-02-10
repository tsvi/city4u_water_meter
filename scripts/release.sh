#!/bin/sh
# Release script that bumps version and optionally pushes to git

# Check if dry-run flag is present
case "$*" in
  *-n*|*--dry-run*)
    # Dry-run mode: only bump version, don't push
    bump-my-version bump "$@"
    ;;
  *)
    # Normal mode: bump version and push
    bump-my-version bump "$@" && git push && git push --tags
    ;;
esac
