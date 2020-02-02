#!/bin/bash
cd $CODEFIXER_PATH
exec < /dev/tty
python3 hook.py
exec <&-
exit $?