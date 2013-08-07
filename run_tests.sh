#!/usr/bin/env bash
export PYTHONPATH=$(dirname $0):${PYTHONPATH}
export DJANGO_SETTINGS_MODULE='test_project.settings'
python $(dirname $0)/manage.py test debreach
