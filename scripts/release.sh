#!/bin/sh
# Release script: bumps version and pushes to git
# In dry-run mode (-n/--dry-run), bump-my-version won't modify files, so git push does nothing
bump-my-version bump "$@" && git push && git push --tags
