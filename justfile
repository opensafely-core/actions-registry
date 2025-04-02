# just has no idiom for setting a default value for an environment variable
# so we shell out, as we need VIRTUAL_ENV in the justfile environment
export VIRTUAL_ENV  := `echo ${VIRTUAL_ENV:-.venv}`

export BIN := VIRTUAL_ENV + if os_family() == "unix" { "/bin" } else { "/Scripts" }
export PIP := BIN + if os_family() == "unix" { "/python -m pip" } else { "/python.exe -m pip" }
# enforce our chosen pip compile flags
export COMPILE := BIN + "/pip-compile --allow-unsafe --generate-hashes"

export DEFAULT_PYTHON := if os_family() == "unix" { `cat .python-version` } else { "python" }


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


# update `uv.lock` if dependencies in `pyproject.toml` have changed
requirements *args: virtualenv
    #!/usr/bin/env bash
    set -euo pipefail

    # Determine timestamp cutoff for resolving dependencies
    # Use existing lockfile timestamp cutoff if present
    # If (unexpectedly) no timestamp is found, set a new timestamp equal to one week ago
    TIMESTAMP=$(grep -n exclude-newer uv.lock | cut -d'=' -f2 | cut -d'"' -f2) || TIMESTAMP=$(date -d '-7 days' +"%Y-%m-%dT%H:%M:%SZ")

    # Run `uv lock` with the timestamp; override by setting UV_EXCLUDE_NEWER
    UV_EXCLUDE_NEWER=${UV_EXCLUDE_NEWER:-$TIMESTAMP} uv lock {{ args }}


# Install prod dependencies into environment
prodenv: requirements
    #!/usr/bin/env bash
    set -euo pipefail

    uv sync --frozen --no-dev


_env:
    #!/usr/bin/env bash
    set -euo pipefail

    test -f .env || cp dotenv-sample .env


# && dependencies are run after the recipe has run. Needs just>=0.9.9. This is
# a killer feature over Makefiles.
#
# Install dev and prod dependencies into environment
devenv: _env requirements && install-precommit
    #!/usr/bin/env bash
    set -euo pipefail

    uv sync --frozen


# ensure precommit is installed
install-precommit:
    #!/usr/bin/env bash
    set -euo pipefail

    BASE_DIR=$(git rev-parse --show-toplevel)
    test -f $BASE_DIR/.git/hooks/pre-commit || $BIN/pre-commit install

# upgrade dependencies (specify package to upgrade single package, all by default)
# when resolving dependencies, exclude releases newer than `UV_EXCLUDE_NEWER` (default: 7 days ago)
upgrade package="": virtualenv
    #!/usr/bin/env bash
    set -euo pipefail

    UV_EXCLUDE_NEWER=${UV_EXCLUDE_NEWER:-$(date -d '-7 days' +"%Y-%m-%dT%H:%M:%SZ")}
    touch -d "$UV_EXCLUDE_NEWER" $VIRTUAL_ENV/.target

    LOCKFILE_TIMESTAMP=$(grep -n exclude-newer uv.lock | cut -d'=' -f2 | cut -d'"' -f2) || LOCKFILE_TIMESTAMP=""
    if [ -z $LOCKFILE_TIMESTAMP ]; then
        echo "Lockfile will be ignored due to no existing timestamp."
        echo "To respect the lockfile, do not run this recipe; directly run uv sync with UV_EXCLUDE_NEWER unset."
    else
        touch -d "$LOCKFILE_TIMESTAMP" $VIRTUAL_ENV/.existing

        if [ $VIRTUAL_ENV/.existing -nt $VIRTUAL_ENV/.target ]; then
            echo "The lockfile timestamp is newer than the target cutoff. Using the lockfile timestamp."
            UV_EXCLUDE_NEWER=$(grep -n exclude-newer uv.lock | cut -d'=' -f2 | cut -d'"' -f2)
        else
            # Write the new timestamp to the lockfile, or else `uv` will disregard it
            sed -i "s|^exclude-newer = .*|exclude-newer = \"$UV_EXCLUDE_NEWER\"|" uv.lock
        fi
    fi

    echo "UV_EXCLUDE_NEWER set to $UV_EXCLUDE_NEWER."

    opts="--upgrade"
    test -z "{{ package }}" || opts="--upgrade-package {{ package }}"
    uv sync --exclude-newer $UV_EXCLUDE_NEWER $opts

# update (upgrade) prod and dev dependencies
update-dependencies: upgrade

# update `pyproject.toml` that the project's minimum required version of a given package is its current latest one
# "latest" is defined using the value of `UV_EXCLUDE_NEWER` (default: 7 days ago)
require-latest package: virtualenv (upgrade package)
    #!/usr/bin/env bash
    set -euo pipefail

    VERSION=$(uv pip show {{ package }} | grep -n Version: | cut -d' ' -f2)
    echo "Adding constraint {{ package }}>=${VERSION}"
    uv add "{{ package }}>=${VERSION}" --exclude-newer $(grep -n exclude-newer uv.lock | cut -d'=' -f2 | cut -d'"' -f2)

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
