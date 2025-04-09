## Recipe readmes

### `just virtualenv` recipe
This recipe assumes that `DEFAULT_PYTHON` in the justfile and the contents of `.python-version` are in sync.

As before, the recipe respects the `PYTHON_VERSION` environment variable, if set.

The recipe will look for the specified python version. If not found, `uv` will install its managed version.
The default preference is: `uv`-managed python when found > system python > newly install a `uv`-managed python.
To alter the preference, use the [--python-preference](https://docs.astral.sh/uv/reference/settings/#python-preference) flag.

For deployment, we should prefer the ubuntu system python over `uv`-managed python,
as the latter statically links the `openssl` library which is not ideal for security reasons.
(based on discussions with Simon; to be discussed in the tech catchup).

#### Limitations
- Deadsnakes is still needed in production if dynamic linking is required.

#### Cooldown period implementation
N/A: No cooldown period is set for the python version.

### `just requirements-prod` and `just requirements-dev` recipes
Update the `uv.lock` file if dependencies in `pyproject.toml` have changed.

The behaviour of `requirements-dev` has not changed: both `dev` and `prod` dependencies are resolved and locked.

The `requirements-prod` recipe previously only locked `prod` dependencies, but now it also locks `dev` dependencies.
(i.e. now, `requirements-prod` is equivalent to `requirements-dev`.)

This is because `uv` does not support only locking certain groups of dependencies.
(i.e. the `uv lock` command does not support locking `--group` or `--no-group` flags.)

#### Limitations
- Cannot only lock `prod` dependencies.
- (COOLDOWN ONLY:) Cannot define new timestamp or remove timestamp without triggering all available upgrades.

#### Cooldown period implementation details
- If a new dependency is added to `pyproject.toml`, running `just requirements-prod` or
`just requirements-dev` will fetch the latest compatible version of the dependency, as
defined by the `UV_EXCLUDE_NEWER` timestamp.
a. If `UV_EXCLUDE_NEWER` is not provided or provided as an empty string, it is set to the
current lockfile's `exclude-newer` timestamp.
b. If `UV_EXCLUDE_NEWER` is not provided or provided as an empty string, 
**and** the lockfile does not contain an `exclude-newer` timestamp, no timestamp cutoff is used.
(i.e., the recipe will not attempt to implement the cooldown period.)
c. If `UV_EXCLUDE_NEWER` is provided as a timestamp, it will be used as the new
timestamp cutoff and written into the lockfile. All dependencies will be updated to
the latest compatible version inline with the new timestamp cutoff.

The behaviour for (b) can be changed by tampering with the lockfile, but we are not going
to do that.

### `just prodenv` recipe
Install production dependencies into the virtual environment.
Remove any installed `dev` dependencies from the virtual environment.
The dependencies are specified by the `uv.lock` file.

#### Limitations
- N/A (Always respects lockfile)

#### Cooldown period implementation
- This recipe cannot change the dependencies in the lockfile (or their versions),
so it is agnostic to the cooldown period.

### `just devenv` recipe
Install production and development dependencies into the virtual environment.
The dependencies are specified by the `uv.lock` file.

#### Limitations
- Prod and dev dependencies are to be installed in one go.

#### Cooldown period implementation
- This recipe cannot change the dependencies in the lockfile (or their versions),
so it is agnostic to the cooldown period.

### `just upgrade` recipe
Upgrade all dependencies, or a specific dependency.
The "env" argument has no effect on the command.

#### Limitations
- Cannot upgrade only prod or only dev dependencies.
- (COOLDOWN ONLY:) Must stick to the `exclude-newer` timestamp (or lack thereof) in the lockfile.
To change the timestamp, must use `just update-dependencies` instead, which will upgrade all dependencies.

#### Cooldown period implementation
- This recipe updates all dependencies or a specific dependency to the latest compatible
version inline with the `exclude-newer` timestamp in the lockfile.
Unlike the recipes above, it is not possible to specify an alternative timestamp cutoff via setting `UV_EXCLUDE_NEWER`.
- This is because setting `UV_EXCLUDE_NEWER` to anything other than the current
lockfile timestamp is **incompatible with attempting a single-package upgrade**.
- If there is no timestamp in the lockfile, no timestamp cutoff is used.
(i.e., the recipe will not attempt to implement the cooldown period.)

### `just update-dependencies` recipe
Upgrade all dependencies.

#### Limitations
- Unwanted upgrades must be prevented by separately pinning them in `pyproject.toml`.
- (COOLDOWN ONLY:) To prevent accidental downgrades / incompatabilities, downgrades are not allowed.

#### Cooldown period implementation
- This recipe updates all dependencies to their latest compatible versions, as
defined by the `UV_EXCLUDE_NEWER` timestamp. By default, this is the `exclude-newer`
timestamp in the lockfile.
- If `UV_EXCLUDE_NEWER` is set to a timestamp, it will be used as the new timestamp cutoff
and written into the lockfile.
- If the `date` parameter is passed, a new timestamp cutoff is calculated and will be
written into the lockfile. (Example usage: `just update-dependencies "7 days ago"`.)
- If both `UV_EXCLUDE_NEWER` and the `date` parameter are passed, `UV_EXCLUDE_NEWER` will
have precedence.
- If the lockfile timestamp is newer than a user-specified timestamp (via `UV_EXCLUDE_NEWER` or the `date` parameter), the lockfile timestamp will have precedence.
(E.g., on April 8th, if the lockfile timestamp is set to April 7th, and the user runs `just update-dependencies "7 days ago"`, April 7th will be used as the cutoff rather than April 1st.)
