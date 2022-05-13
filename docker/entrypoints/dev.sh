#!/bin/bash

set -euo pipefail

./manage.py migrate
./manage.py ensure_groups
./manage.py collectstatic --no-input --clear | grep -v '^Deleting '
./manage.py ensure_superuser
INCLUDE_PRIVATE=t ./manage.py populate_reports
./manage.py createcachetable

exec "$@"
