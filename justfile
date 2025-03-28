# just has no idiom for setting a default value for an environment variable
# so we shell out, as we need VIRTUAL_ENV in the justfile environment
export VIRTUAL_ENV  := `echo ${VIRTUAL_ENV:-.venv}`

export BIN := VIRTUAL_ENV + if os_family() == "unix" { "/bin" } else { "/Scripts" }
export PIP := BIN + if os_family() == "unix" { "/python -m pip" } else { "/python.exe -m pip" }
# enforce our chosen pip compile flags
export COMPILE := BIN + "/pip-compile --allow-unsafe --generate-hashes"

export DEFAULT_PYTHON := if os_family() == "unix" { `cat .python-version` } else { "python" }

export UV_EXCLUDE_NEWER := `echo ${UV_EXCLUDE_NEWER:-$(date -d '-7 days' +"%Y-%m-%dT%H:00:00Z")}`

# list available commands
default:
    @just --list


# clean up temporary files
clean:
    rm -rf .venv


# ensure valid virtualenv
virtualenv *args:
    #!/usr/bin/env bash
    set -euo pipefail

    # Allow users to specify python version in .env
    PYTHON_VERSION=${PYTHON_VERSION:-$DEFAULT_PYTHON}

    # Create venv; installs `uv`-managed python if python interpreter not found
    test -d $VIRTUAL_ENV || uv venv --python $PYTHON_VERSION {{ args }}

    # Block accidentally usage of system pip by placing an executable at .venv/bin/pip
    echo 'echo "pip is not installed: use uv pip for a pip-like interface."' > .venv/bin/pip
    chmod +x .venv/bin/pip

# Dependency management using `uv`; respects UV_EXCLUDE_NEWER

sync *args: virtualenv
    #!/usr/bin/env bash
    set -euo pipefail

    uv sync {{ args }}

add *args: virtualenv
    #!/usr/bin/env bash
    set -euo pipefail

    uv add {{ args }}

remove *args: virtualenv
    #!/usr/bin/env bash
    set -euo pipefail

    uv remove {{ args }} || uv remove --dev {{ args }}

_compile src dst *args: virtualenv
    #!/usr/bin/env bash
    set -euo pipefail

    # exit if src file is older than dst file (-nt = 'newer than', but we negate with || to avoid error exit code)
    test "${FORCE:-}" = "true" -o {{ src }} -nt {{ dst }} || exit 0
    $BIN/pip-compile --allow-unsafe --generate-hashes --output-file={{ dst }} {{ src }} {{ args }}


# update requirements.prod.txt if requirements.prod.in has changed
requirements-prod *args:
    {{ just_executable() }} _compile requirements.prod.in requirements.prod.txt {{ args }}


# update requirements.dev.txt if requirements.dev.in has changed
requirements-dev *args: requirements-prod
    {{ just_executable() }} _compile requirements.dev.in requirements.dev.txt {{ args }}


# ensure prod requirements installed and up to date
prodenv: requirements-prod
    #!/usr/bin/env bash
    set -euo pipefail

    # exit if .txt file has not changed since we installed them (-nt == "newer than', but we negate with || to avoid error exit code)
    test requirements.prod.txt -nt $VIRTUAL_ENV/.prod || exit 0

    $PIP install -r requirements.prod.txt
    touch $VIRTUAL_ENV/.prod


_env:
    #!/usr/bin/env bash
    set -euo pipefail

    test -f .env || cp dotenv-sample .env


# && dependencies are run after the recipe has run. Needs just>=0.9.9. This is
# a killer feature over Makefiles.
#
# ensure dev requirements installed and up to date
devenv: _env prodenv requirements-dev && install-precommit
    #!/usr/bin/env bash
    set -euo pipefail

    # exit if .txt file has not changed since we installed them (-nt == "newer than', but we negate with || to avoid error exit code)
    test requirements.dev.txt -nt $VIRTUAL_ENV/.dev || exit 0

    $PIP install -r requirements.dev.txt
    touch $VIRTUAL_ENV/.dev


# ensure precommit is installed
install-precommit:
    #!/usr/bin/env bash
    set -euo pipefail

    BASE_DIR=$(git rev-parse --show-toplevel)
    test -f $BASE_DIR/.git/hooks/pre-commit || $BIN/pre-commit install


# upgrade dev or prod dependencies (specify package to upgrade single package, all by default)
upgrade env package="": virtualenv
    #!/usr/bin/env bash
    set -euo pipefail

    opts="--upgrade"
    test -z "{{ package }}" || opts="--upgrade-package {{ package }}"
    FORCE=true {{ just_executable() }} requirements-{{ env }} $opts


# update (upgrade) prod and dev dependencies
update-dependencies: (upgrade 'prod') (upgrade 'dev')


# *ARGS is variadic, 0 or more. This allows us to do `just test -k match`, for example.
# Run the tests
test *ARGS: devenv
    $BIN/python manage.py collectstatic --no-input
    $BIN/python -m pytest --cov=. --cov-report html --cov-report term-missing:skip-covered {{ ARGS }}


format *args=".": devenv
    $BIN/ruff format --check {{ args }}

lint *args=".": devenv
    $BIN/ruff check --output-format=full {{ args }}

# runs the various dev checks but does not change any files
check: format lint


# fix formatting and import sort ordering
fix: devenv
    $BIN/ruff check --fix .
    $BIN/ruff format .


check-fnm:
    #!/usr/bin/env bash
    set -euo pipefail

    if ! which fnm >/dev/null; then
        echo >&2 "You must install fnm. See https://github.com/Schniz/fnm."
        exit 1
    fi

# install all JS dependencies
npm-install: check-fnm
    fnm use
    npm ci


# build frontend assets
npm-build:
    npm run build


# Gather frontend assets and static files
collectstatic: devenv
    $BIN/python manage.py collectstatic --no-input --clear | grep -v '^Deleting '

# run migrations
migrate: devenv
    $BIN/python manage.py migrate

# run the dev server
run: devenv
    $BIN/python manage.py runserver localhost:8000


# build docker image env=dev|prod
docker-build env="dev": _env
    {{ just_executable() }} docker/build {{ env }}


# run tests in docker container
docker-test *args="": _env
    {{ just_executable() }} docker/test {{ args }}


# run dev server in docker container
docker-serve: _env
    {{ just_executable() }} docker/serve


# run cmd in dev docker continer
docker-run *args="bash": _env
    {{ just_executable() }} docker/run {{ args }}


# exec command in an existing dev docker container
docker-exec *args="bash": _env
    {{ just_executable() }} docker/exec {{ args }}
