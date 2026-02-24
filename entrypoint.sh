#!/bin/sh
set -e

: "${PORT:=80}"
sed -i "s/listen 80;/listen ${PORT};/" /etc/nginx/conf.d/default.conf
# Start backend in background (port 8080)
python main.py &

exec nginx -g "daemon off;"
