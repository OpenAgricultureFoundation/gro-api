#!/usr/bin/env bash

HELP="usage: $0 [options]
Options:
-v  : Run in verbose mode
-l  : Configure the API instance as a leaf server (This is the default)
-r  : Configure the API instance as a root server
-d  : Configure the API instance in development mode
-p  : Configure the API instance in production mode (This is the default)
-h  : Print this help message"

VERBOSE=false
SERVER_TYPE=leaf
SERVER_MODE=production

while getopts "vlrdph" OPTION; do
    case $OPTION in
        v) VERBOSE=true ;;
        l) SERVER_TYPE=leaf ;;
        r) SERVER_TYPE=root ;;
        d) SERVER_MODE=development ;;
        p) SERVER_MODE=production ;;
        h) echo "$HELP"; exit 0 ;;
    esac
done

$VERBOSE && [ -n "$SERVER_TYPE" ] && echo "Selected $SERVER_TYPE server type"
$VERBOSE && [ -n "$SERVER_MODE" ] && echo "Selected $SERVER_MODE server mode"

$VERBOSE && echo "Changing to script directory"
cd ${0%/*}

if [ ! -d "./env" ]; then
    $VERBOSE && echo "Creating virtual environment"
    virtualenv -p python3 --system-site-packages env
    $VERBOSE && echo "Activating virtual environment"
    source env/bin/activate
    echo "Installing project dependencies"
    pip install -r requirements.txt
fi

echo "source env/bin/activate" > .env
echo "export CITYFARM_API_ROOT=$(pwd -P)" >> .env
echo "export CITYFARM_API_SERVER_TYPE=$SERVER_TYPE" >> .env
echo "export CITYFARM_API_SERVER_MODE=$SERVER_MODE" >> .env
echo "export DJANGO_SETTINGS_MODULE=cityfarm_api.settings" >> .env
case $SERVER_MODE in
    development)
        echo "export UWSGI_PROCESSES=1" >> .env
        echo "export UWSGI_MASTER_FIFO=$(pwd -P)/fifo" >> .env
        echo "export UWSGI_HTTP=127.0.0.1:8000" >> .env
        ;;
    production)
        echo "export UWSGI_PROCESSES=4" >> .env
        echo "export UWSGI_MASTER_FIFO=/etc/cityfarm_api_fifo" >> .env
        echo "export UWSGI_HTTP=0.0.0.0:80" >> .env
esac

echo "Wrote configuration to ./.env file. To use it, run \"source .env\""
