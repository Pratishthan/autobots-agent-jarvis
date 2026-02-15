#!/bin/bash

source .venv/bin/activate
source .env

python -m uvicorn autobots_devtools_shared_lib.common.servers.fileserver.app:app \
    --reload \
    --host 0.0.0.0 \
    --port ${FILE_SERVER_PORT:-9002} 2>&1 | tee -a logs/file_server.log
