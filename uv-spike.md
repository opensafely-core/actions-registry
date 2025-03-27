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