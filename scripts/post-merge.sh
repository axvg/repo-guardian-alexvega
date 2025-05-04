#!/usr/bin/env bash

REPO_ROOT=$(git rev-parse --show-toplevel)
echo "Running post-merge script..."
echo "in... $REPO_ROOT"

LAST_TAG=$(git describe --tags --abbrev=0) || { echo "No tags found, skipping release creation"; exit 1; }
echo "Last tag: $LAST_TAG"

echo "🔄 Building DAG..."
python "${REPO_ROOT}/src/guardian/cli.py" build-dag "$REPO_ROOT"
echo "🔄 Building DAG ok!!"


if command -v gh &> /dev/null
then
    echo "🔄 Creating release..."
    if [ -z "$LAST_TAG" ]; then
        echo "No tags found!! skipping release creation"
        exit 1
    fi
    gh release create "$LAST_TAG" --title "$LAST_TAG" --notes "Release $LAST_TAG" --generate-notes --draft --prerelease
    echo "🔄 Release created!!"
else
    echo "gh CLI not found! skipping release creation"
    exit 1
fi