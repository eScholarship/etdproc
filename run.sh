#! /bin/bash

set -o pipefail
set -o errtrace
set -o nounset
set -o errexit


DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR

### Log file
NOW="$(date +"%Y-%m-%d")"
echo $NOW

echo $DIR/logs/etd_$NOW.log
LOG_NAME=$DIR/logs/etd_$NOW.log
# ensure the Python environment is set up correctly
set +u
source /apps/eschol/.etdenv/bin/activate
set -u

# clear up the temp directory from last run
rm -rf /apps/eschol/apache/htdocs/etdprocTmp/*

# run the processor
python controller.py &> $LOG_NAME

