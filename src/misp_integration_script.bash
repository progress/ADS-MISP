#!/bin/bash

function usage {
    cat << EOF >&2
usage: misp.sh <options>

Required:
  --misp_server       MISP server URL
  --misp_api_key      MISP API key
  --misp_tag          MISP events tag
  --misp_ids          MISP to IDS flag
  --misp_distribution Who will be able to see this event once it becomes published. 0 - Your organization only, 1 - This community only, 2 - Connected communities, 3 - All communities, 4 - Sharing group, 5 - Inherit Event
  --flowmon_filters   FLOWMON filter name (separated with ,)
  --flowmon_user      FLOWMON username
  --flowmon_pass      FLOWMON password

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
    /data/components/ads-blacklist-updater/venv/bin/python3 /home/flowmon/misp/main.py --options $OPTIONS  --data $DATA64
done
