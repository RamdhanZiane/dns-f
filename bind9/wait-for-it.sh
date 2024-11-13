#!/usr/bin/env bash
# wait-for-it.sh is a script to wait for a service to be ready
# Source: https://github.com/vishnubob/wait-for-it/blob/master/wait-for-it.sh

set -e

TIMEOUT=15
QUIET=0

usage()
{
    echo "Usage: wait-for-it.sh host:port [-t timeout] [-- command]"
    exit 1
}

host=""
port=""
cmd=""

while [[ $# -gt 0 ]]
do
    case "$1" in
        *:* )
        host=$(echo $1 | cut -d: -f1)
        port=$(echo $1 | cut -d: -f2)
        shift 1
        ;;
        -t)
        TIMEOUT="$2"
        shift 2
        ;;
        --)
        shift
        cmd="$@"
        break
        ;;
        *)
        echo "Unknown argument: $1"
        usage
        ;;
    esac
done

if [[ -z "$host" || -z "$port" ]]; then
    echo "Error: host and port must be specified"
    usage
fi

start_ts=$(date +%s)

while :
do
    if nc -z "$host" "$port"; then
        if [[ $QUIET -ne 1 ]]; then
            echo "Service $host:$port is available after $(( $(date +%s) - start_ts )) seconds"
        fi
        break
    fi

    if [[ $(( $(date +%s) - start_ts )) -ge $TIMEOUT ]]; then
        echo "Timeout after $TIMEOUT seconds waiting for $host:$port"
        exit 1
    fi

    sleep 1
done

if [[ -n "$cmd" ]]; then
    exec $cmd
fi
