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
