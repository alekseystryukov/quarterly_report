#!/usr/bin/env bash


screen -dmS celery_worker bash -c "celery -A quarterly_report  worker -l info"
screen -dmS celery_flower bash -c "celery -A quarterly_report flower --port=5555"