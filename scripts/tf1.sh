#!/bin/sh

tmux new -d -s dvb_tf1 dvbv5-zap --adapter 3 -r -p --all-pids -c ~/channels_v5.conf "TF1(SMR6)"
tmux new -d -s process_tf1 \; send-keys "source ../venv/bin/activate" Enter "python liveSpeechToText.py --adapter-drv /dev/dvb/adapter3/dvr0 tf1 lcp" Enter

