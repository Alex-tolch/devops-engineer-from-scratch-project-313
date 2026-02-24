#!/bin/sh
set -e
# Start backend in background (port 8080)
python main.py &
# Nginx in foreground (port 80)
exec nginx -g "daemon off;"
