#!/bin/bash
source ~/codechecker/venv/bin/activate
if [ "$1" != "i" ] && [ "$1" != "incremental" ]; then
    rm -rf /tmp/cctmp 2&> /dev/null
    rm -rf /tmp/codefixer 2&> /dev/null
fi
echo Starting CodeChecker server...
CodeChecker server -w /tmp/cctmp > /dev/null &
CC_PID=$!
rm -f config.ini
ln -s configTrain.ini config.ini
sleep 10s
echo Starting script...
python3 buildTestDB.py $1
echo Finished
kill -15 $CC_PID