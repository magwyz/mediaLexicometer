#!/bin/sh

tmux new -d -s dvb1 dvbv5-zap --adapter 1 -r -p --all-pids -c channels_v5.conf "franceinfo (GR1 A)"
tmux new -d -s process1 \; send-keys "source ../venv/bin/activate" Enter "python liveSpeechToText.py --adapter-drv /dev/dvb/adapter1/dvr0 franceinfo" Enter
