# Notes during the spike

## Chat with Simon
These are rough bullet points that are in no particular order.

- For this spike let's aim to remove requirements.in/requirements.txt and use uv to manage dependencies.
This means not using `uv pip`, but `uv add` etc. instead  to manage dependencies.

- Since we would like to use `uv` to manage dependencies, we have no use for `pip`.
We can remove it from the `virtualenv` setup, but this means there is a chance of a dev
accidentally calling the system pip in activated virtual environments (as there won't be
a pip in the venv path). We should do something to prevent this.

- We should have commands like `just add` etc. to add dependencies, which wrap around `uv add`, but
respect the cooldown time in our dependencies policy. If we want to bypass the cooldown, we can use `uv add`
straight from the command line instead of via the just command.

- We should be committing `uv.lock`. See https://docs.astral.sh/uv/concepts/projects/layout/#the-lockfile

- At some point we would need to configure docker-related things. Simon shared this article:
https://hynek.me/articles/docker-uv/


## Other notes

- If we want to implement the cooldown time, we can do so via an environment variable
or a parameter to uv commands.
In the former case, we can add the environment variable to the justfile:
```sh
export UV_EXCLUDE_NEWER := `date -d '-7 days' +"%Y-%m-%dT%H:%M:%SZ"`
```
See https://docs.astral.sh/uv/configuration/environment/#uv_exclude_newer.


## Implementation notes

### `just virtualenv` recipe
This recipe assumes that `DEFAULT_PYTHON` in the justfile and the contents of `.python-version` are in sync.

As before, the recipe respects the `PYTHON_VERSION` environment variable, if set.

The recipe will look for the specified python version. If not found, `uv` will install its managed version.
The default preference is: `uv`-managed python when found > system python > newly install a `uv`-managed python.
To alter the preference, use the [--python-preference](https://docs.astral.sh/uv/reference/settings/#python-preference) flag.

For deployment, we should prefer the ubuntu system python over `uv`-managed python,
as the latter statically links the `openssl` library which is not ideal for security reasons.
(based on discussions with Simon; to be discussed in the tech catchup).
