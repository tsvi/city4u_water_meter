#!/bin/sh
# Release script that bumps version and pushes to git
# Note: If you use -n or --dry-run, bump-my-version won't modify files,
# so git push will just report "everything up-to-date"

bump-my-version bump "$@" && git push && git push --tags
