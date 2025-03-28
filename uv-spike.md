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


- At the time of writing (2025-03-28), `osgithub`'s last release was 4 days ago. We can use it
to test `uv`'s `--exclude-newer` flag and how packages can get updated by just commands.

```sh
(actions-registry) alice@lunapiena:~/code/actions-registry$ uv add -r requirements.prod.in --exclude-newer 2025-03-21
Resolved 39 packages in 1.23s
Installed 37 packages in 153ms
 + asgiref==3.8.1
 + attrs==25.3.0
 + beautifulsoup4==4.13.3
...
 + whitenoise==6.9.0
 ```

Proceeding to run `uv` commands without the `--exclude-newer` flag will update `osgithub` and other packages.
Note that the below also shows that removing `bs4` removes `soupsieve` automatically.
```sh
(actions-registry) alice@lunapiena:~/code/actions-registry$ uv remove bs4
Ignoring existing lockfile due to removal of timestamp cutoff: `2025-03-22T00:00:00Z`
Resolved 36 packages in 1.14s
Uninstalled 7 packages in 6ms
Installed 4 packages in 5ms
 - beautifulsoup4==4.13.3
 - bs4==0.0.2
 - cattrs==24.1.2
 + cattrs==24.1.3
 - osgithub==0.3.5
 + osgithub==0.4.0
 - python-dotenv==1.0.1
 + python-dotenv==1.1.0
 - soupsieve==2.6
...
 ```

 
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
