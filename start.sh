#!/usr/bin/env bash
set -euo pipefail

exec gunicorn --bind 0.0.0.0:${PORT:-3050} --workers 2 --threads 4 --timeout 120 "databiqs-website:app"
