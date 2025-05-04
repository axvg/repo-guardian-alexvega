#!/usr/bin/env bash

# SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(git rev-parse --show-toplevel)
CLI_ROOT="${REPO_ROOT}/src/guardian/cli.py"

# echo "running install-hook.sh"
# bash "${SCRIPT_DIR}/install-hook.sh"

echo "🔍 scanning repo in $REPO_ROOT..."
python "${CLI_ROOT}" scan "$REPO_ROOT"
echo "🔍 scanning repo ok!!"

# echo "🔄 Building DAG..."
# python "${CLI_ROOT}" build-dag "$REPO_ROOT"
# echo "🔄 Building DAG ok!!"