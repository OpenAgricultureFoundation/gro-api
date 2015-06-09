#!/usr/bin/env bash

# Parse Options
verbose=false
while getopts "vlrdp" OPTION; do
    case $OPTION in
        v) verbose=true
            ;;
        l) SERVER_TYPE="leaf"
            ;;
        r) SERVER_TYPE="root"
            ;;
        d) SERVER_MODE="development"
            ;;
        p) SERVER_MODE="production"
    esac
done

$verbose && [ -n "$SERVER_TYPE" ] && echo "Selected $SERVER_TYPE server type"
$verbose && [ -n "$SERVER_MODE" ] && echo "Selected $SERVER_MODE server mode"

# Select the node type if one hasn't already been selected
if [ -z "$SERVER_TYPE" ]; then
    PS3="What type of server do you want to run? > "
    select SERVER_TYPE in leaf root; do
        case "$SERVER_TYPE" in
            leaf)
                $verbose && echo "You selected leaf"
                break
                ;;
            root)
                $verbose && echo "You selected root"
                break
                ;;
        esac
    done
fi

# Select a server mode if one hasn't alread been selected
if [ -z "$SERVER_MODE" ]; then
    PS3="What mode should the server run in? > "
    select SERVER_MODE in development production ; do
        case $SERVER_MODE in
            development)
                $verbose && echo "You selected development"
                break
                ;;
            production)
                $verbose && echo "You selected production"
                break
                ;;
        esac
    done
fi

$verbose && echo "Changing to script directory"
cd ${0%/*}

if [ ! -d "./env" ]; then
    $verbose && echo "Creating virtual environment"
    virtualenv -p python3 --system-site-packages env
    $verbose && echo "Activating virtual environment"
    source env/bin/activate
    echo "Installing project dependencies"
    pip install -r requirements.txt
fi

rm -f uwsgi/enabled/*
echo "source env/bin/activate" > .env
echo "export CITYFARM_API_ROOT=$(pwd -P)" >> .env
echo "export CITYFARM_API_SERVER_TYPE=$SERVER_TYPE" >> .env
echo "export CITYFARM_API_SERVER_MODE=$SERVER_MODE" >> .env

case $SERVER_MODE in
    development)
        ln -s ../available/main_dev.ini uwsgi/enabled
        echo "export CITYFARM_API_HTTP_PORT=8000" >> .env
        case $SERVER_TYPE in
            leaf)
                ln -s ../available/control_dev.ini uwsgi/enabled
                echo "export CITYFARM_API_HTTP_CONTROL_PORT=8001" >> .env
                echo "export CITYFARM_API_MASTER_FIFO=$(pwd -P)/fifo" >> .env
                echo "export DJANGO_SETTINGS_MODULE=cityfarm_api.settings.leaf_dev" >> .env
                ;;
            root)
                echo "export DJANGO_SETTINGS_MODULE=cityfarm_api.settings.root_dev" >> .env
                ;;
        esac
        ;;
    production)
        ln -s ../available/main_prod.ini uwsgi/enabled
        # TODO: Define CITYFARM_API_PORT or alternative for nginx deployment
        case $SERVER_TYPE in
            leaf)
                ln -s ../available/control_prod.ini uwsgi/enabled
                # TODO: Define CITYFARM_API_CONTROL_PORT or alternative for nginx deployment
                echo "export CITYFARM_API_MASTER_FIFO=/etc/cityfarm_api_fifo" >> .env
                echo "export DJANGO_SETTINGS_MODULE=cityfarm_api.settings.leaf_prod" >> .env
                ;;
            root)
                echo "export DJANGO_SETTINGS_MODULE=cityfarm_api.settings.root_prod" >> .env
                ;;
        esac
        ;;
esac
echo "Wrote configuration to ./.env file. To use it, run \"source .env\""
