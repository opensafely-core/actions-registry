#!/bin/bash
set -euo pipefail

./manage.py migrate
./manage.py createcachetable

exec "$@"
