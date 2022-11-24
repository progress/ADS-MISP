#!/bin/bash

function usage {
    cat << EOF >&2
usage: misp.sh <options>

Required:
  --misp_server   MISP server URL
  --misp_api_key  MISP API key
  --source        Source of the sightings

EOF
    exit
}

OPTIONS="{\"version\":1"
while [[ $# -gt 0 ]]; do
    NAME=`echo $1 | sed 's/^-*//g'`
    OPTIONS+=$",\"$NAME\":"$"\"$2\""
    shift 2
done
OPTIONS+="}"

IFS=$'\t'
while read line
do
    DATA=""
    for WORD in $line
    do
        DATA+="${WORD}"$'<delimiter>'
    done
    DATA64=$(echo $DATA | base64 --wrap=0)
    /data/components/ads-blacklist-updater/venv/bin/python3 /home/flowmon/misp/sightings.py --options $OPTIONS --data $DATA64
done
