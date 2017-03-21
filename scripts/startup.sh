#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/

set -o allexport
source env-init.sh

uwsgi --http "${DEFAULT_LISTENER_HOST}":"${DEFAULT_LISTENER_PORT}" --http-keepalive --add-header "Connection: keep-alive" --pyargv "--debug" --module qube.src.api.app --callable app --no-site --pythonpath=/usr/local/lib/python3.5 --pythonpath=/usr/local/lib/python3.5/site-packages --processes "${DEFAULT_PROCESS_COUNT}" --enable-threads 2>&1 > nohup.out
