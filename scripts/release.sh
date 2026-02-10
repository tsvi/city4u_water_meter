#!/bin/sh
# Release script that bumps version and optionally pushes to git

# Check if dry-run flag is present
case "$*" in
  *-n*|*--dry-run*)
    # Dry-run mode: preview changes only, don't modify files or push
    # The -n or --dry-run flag tells bump-my-version to show what would change without modifying any files
    bump-my-version bump "$@"
    ;;
  *)
    # Normal mode: bump version, commit, tag, and push
    bump-my-version bump "$@" && git push && git push --tags
    ;;
esac
