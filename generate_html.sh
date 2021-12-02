#!/usr/bin/env bash

set -eu

# Move in repo folder
SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
pushd "${SCRIPT_PATH}" > /dev/null


venv/bin/python generate_html.py


# Back to  original path
popd > /dev/null
