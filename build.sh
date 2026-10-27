#!/bin/bash

# This script is the Netlify build command.
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/0.13.1/install.sh | env UV_UNMANAGED_INSTALL="$HOME/.local/bin" sh
    export PATH="$HOME/.local/bin:$PATH"
fi

uv sync --locked --no-dev
uv run --locked --no-dev lektor --project sps20 build -f scss --output-path build
