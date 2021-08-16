# list available commands
default:
    @just --list

# Set up local dev environment
dev_setup:
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

# run the test suite. Optional args are passed to pytest
test ARGS="":
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    python manage.py collectstatic --no-input
    pytest --cov=. {{ ARGS }}

# runs the format (black), sort (isort) and lint (flake8) check but does not change any files
check:
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    black --check .
    isort --check-only --diff .
    flake8

# fix formatting and import sort ordering
fix:
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    black .
    isort .

# compile and update python dependencies.  <target> specifies an environment to update (dev/prod).
update TARGET="prod":
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    echo "Updating and installing requirements"
    pip-compile --generate-hashes --output-file=requirements.{{ TARGET }}.txt requirements.{{ TARGET }}.in
    pip install -r requirements.{{ TARGET }}.txt

# configure the local dev env
dev-config:
	cp dotenv-sample .env

# install all JS dependencies
npm-install: check-fnm
    fnm use
    npm ci

# build frontend assets
npm-build:
    npm run build

check-fnm:
    #!/usr/bin/env bash
    if ! which fnm >/dev/null; then
        echo >&2 "You must install fnm. See https://github.com/Schniz/fnm."
        exit 1
    fi

# Gather frontend assets and static files
collectstatic:
    ./manage.py collectstatic --no-input --clear | grep -v '^Deleting '

# run the dev server
run:
    python manage.py runserver localhost:8000
