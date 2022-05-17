#!/bin/bash

set -euo pipefail

./manage.py migrate
./manage.py ensure_groups
./manage.py createcachetable

exec gunicorn output_explorer.wsgi --config=gunicorn.conf.py
