#!/bin/bash

python vbox_init.py
celery -A Vbox worker -l info -P eventlet > logs/celery.log 2>&1 &
celery -A Vbox beat -l info > logs/celery_beat.log 2>&1 &