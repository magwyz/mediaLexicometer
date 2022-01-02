#!/bin/sh

tmux new -d -s dvb_lci dvbv5-zap --adapter 2 -r -p --all-pids -c ~/channels_v5.conf "LCI(CNH)"
tmux new -d -s process_lci \; send-keys "source ../venv/bin/activate" Enter "python liveSpeechToText.py --adapter-drv /dev/dvb/adapter2/dvr0 lci" Enter

