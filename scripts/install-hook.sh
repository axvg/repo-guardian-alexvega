#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
echo "Installing Git hooks..."
echo "in... $SCRIPT_DIR"

REPO_ROOT=$(git rev-parse --show-toplevel)
HOOKS_DIR="${REPO_ROOT}/.git/hooks"

echo "🔄 Installing post-merge hook..."
echo "in... $HOOKS_DIR"

echo "Hooks in ${HOOKS_DIR}:"
ls -l "${HOOKS_DIR}"


if [ -f "${HOOKS_DIR}/post-merge" ]; then
    echo "post-merge hook already exists. Skipping installation."
    echo "and its content is:"
    cat "${HOOKS_DIR}/post-merge" | head -n 10 
else
    cp "${SCRIPT_DIR}/post-merge.sh" "${HOOKS_DIR}/post-merge"
    chmod +x "${HOOKS_DIR}/post-merge"
    echo "post-merge hook installed successfully."
fi

