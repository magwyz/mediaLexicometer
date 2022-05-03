#!/bin/sh

tmux new -d -s dvb_cnews_bfmtv dvbv5-zap --adapter 0 -r -p --all-pids -c ~/channels_v5.conf "cnews(ntn)"
tmux new -d -s process_cnews_bfmtv \; send-keys "source ../venv/bin/activate" Enter "python liveSpeechToText.py --adapter-drv /dev/dvb/adapter0/dvr0 cnews bfmtv c8" Enter

