Notes during the spike

- Since we would like to use `uv` to manage dependencies, we have no use for `pip`.
We can remove it from the `virtualenv` setup, but this means there is a chance of a dev
accidentally calling the system pip in activated virtual environments (as there won't be
a pip in the venv path). We should do something to prevent this. (Discussion with Simon)


- If we want to implement the cooldown time, we can do so via an environment variable
or a parameter to uv commands.
In the former case, we can add the environment variable to the justfile:
```sh
export UV_EXCLUDE_NEWER := `date -d '-7 days' +"%Y-%m-%dT%H:%M:%SZ"`
```
