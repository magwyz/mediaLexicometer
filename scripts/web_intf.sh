#!/bin/sh

tmux new -d -s web \; send-keys "source ../venv/bin/activate" Enter "python manage.py runserver 0.0.0.0:8000" Enter

