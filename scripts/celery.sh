#!/bin/sh

tmux new -d -s celery \; send-keys "source ../venv/bin/activate" Enter " celery -A liveSpeechToText_celery worker -c 4" Enter

