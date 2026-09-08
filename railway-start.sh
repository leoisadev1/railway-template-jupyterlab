#!/bin/bash
set -euo pipefail

if [ -z "${JUPYTER_TOKEN:-}" ]; then
  printf '%s\n' 'JUPYTER_TOKEN is required; refusing to disable authentication.' >&2
  exit 1
fi

if [ "$(id -u)" = 0 ]; then
  printf '%s\n' 'Jupyter must run as jovyan through the inherited image entrypoint.' >&2
  exit 1
fi

# Keep the token out of process arguments and startup command logs.
exec start-notebook.py --config=/etc/jupyter/railway_server_config.py
