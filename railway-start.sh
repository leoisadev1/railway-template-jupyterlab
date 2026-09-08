#!/bin/bash
set -euo pipefail

if [ -z "${JUPYTER_TOKEN:-}" ]; then
  printf '%s\n' 'JUPYTER_TOKEN is required; refusing to disable authentication.' >&2
  exit 1
fi

# Keep the token out of process arguments and startup command logs.
cmd=(start-notebook.py --config=/etc/jupyter/railway_server_config.py)
if [ "$(id -u)" = 0 ]; then
  if [ "${NB_UID:-1000}" = 0 ] || [ "${NB_USER:-jovyan}" = root ]; then
    printf '%s\n' 'Jupyter must run as an unprivileged user.' >&2
    exit 1
  fi
  # Railway start-command overrides can bypass the image entrypoint.
  unset _START_SH_EXECUTED
  exec start.sh "${cmd[@]}"
fi

exec "${cmd[@]}"
