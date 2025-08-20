# Summary of the spike

## Scope
- For the spike, we will use `uv`'s primary interface to manage dependencies.
Use of `uv pip` to replace `pip` is out of scope, as is the preservation of the
`requirements.in` and `requirements.txt` files.

- We will focus on preserving the API provided by the existing `just` recipes of:
    - `virtualenv`
    - `requirements-dev`
    - `requirements-prod`
    - `devenv`
    - `prodenv`
    - `upgrade`
    - `update-dependencies`,
but switch their implementation to `uv`.

- While we won't modify the existing API,
we will note down any cases where modifying the API would be sensible.

- Following `uv`'s [documentation](https://docs.astral.sh/uv/concepts/projects/layout/#the-lockfile),
we will not consider manual manipulation of the `uv.lock` file.

## The `pyproject.toml` and `uv.lock` files

- `uv` uses sections in `pyproject.toml` to manage dependencies. The file can be manually edited.
    - Prod dependencies are listed in the project's `[dependencies]` section.
    - Dev dependencies are listed in the project's `[dependency-groups]` section, under the `dev` group.

- The `uv.lock` file is `uv`'s lockfile.
From the [uv docs](https://docs.astral.sh/uv/concepts/projects/layout/#the-lockfile):

> `uv.lock` is a human-readable TOML file but is managed by uv and should not be edited manually.

> This file should be checked into version control, allowing for consistent and reproducible installations across machines.

>Unlike the pyproject.toml, which is used to specify the broad requirements of your project, the lockfile contains the exact resolved versions that are installed in the project environment.

## The `uv` commands for managing dependencies
We are interested in the following commands:

- `uv venv`: Create a virtual environment.

- `uv lock`: Resolves project dependencies into lockfile.
    - With an existing uv.lock file, previously locked versions of packages will be preferred[^1].
    - Passing `--upgrade` will update the lockfile with the latest versions of all packages.
    - Passing `--upgrade-package` will update the lockfile with the latest version of a specific package.

- `uv sync`: Installs a subset of packages in the lockfile into the environment.
    - Implicitly runs `uv lock`, unless `--locked` or `--frozen` are passed.
    - Passing `--locked` will run a check on the lockfile and error if it is outdated.
    - Passing `--frozen` will update the environment according to the lockfile without checking if it is up to date.

- `uv add`: Adds a package to `pyproject.toml`, then runs `uv sync` (e.g. `uv add osgithub`).
    - The latest version of the package is added as a constraint unless `--frozen` is passed.
    - The `--dev` flag can be used to add a package to the dev dependencies.
    - A textfile can be passed to add multiple packages at once (e.g. `uv add -r requirements.dev.in --dev`).
    - Not used in the final `just` recipes as it does not match the existing API.

- `uv remove`: Removes a package from `pyproject.toml`, then runs `uv sync` (e.g. `uv remove black --dev`).
    - The `--dev` flag can be used to remove a package from the dev dependencies.
    - Not used in the final `just` recipes as it does not match the existing API.

## Reproducing the existing `just` recipes with `uv` commands

|`just` recipe|Definition|`uv` command wrapped|
|-------------|-----|--------------------|
|`virtualenv`|Create a virtual envrionment|`uv venv`|
|`requirements-dev`|Update the lockfile if dev dependencies in source file has changed|`uv lock`|
|`requirements-prod`|Update the lockfile if prod dependencies in source file has changed|`uv lock`|
|`upgrade`|Update the lockfile with the latest versions of all prod/dev packages, or a specific prod/dev dependency|`uv lock --upgrade` or `uv lock --upgrade-package`|
|`update-dependencies`|Update the lockfile with the latest versions of all packages|`uv lock --upgrade`|
|`devenv`|Install dev and prod dependencies into the environment|`uv sync --frozen --dev`|
|`prodenv`|Install prod dependencies into the environment|`uv sync --frozen`|

Owing to the fact that `uv lock` does not support only resolving a subset of dependencies, it is not possible to
exactly reproduce the recipes that only resolve prod but not dev dependencies.

The `requirements-dev` and `requirements-prod` recipes under `uv` implementation are identical in behaviour.

Running `upgrade 'prod'` or `upgrade 'dev'` or `upgrade '*'` where `*` is any string are all equivalent;
all dependencies are updated to the latest versions.

## Proposed API changes
- Replace `requirements-dev` and `requirements-prod` with `requirements`.
- Remove the positional argument from `upgrade`.

## Implementing a cooldown period for upgrading dependencies

### Setting the timestamp cutoff
- A global timestamp cutoff can be set via the `--exclude-newer` flag or the
`UV_EXCLUDE_NEWER` environment variable. The global timestamp cutoff is applied to all packages.

- A package-specific timestamp cutoff can be set via the `--exclude-newer-package` flag (new in version 0.8.4). Multiple packages can be specified.

- A package's version must be older than the global cutoff or its specific cutoff (whichever applies)
to be considered for installation, note that it does not need to be the latest version.

- `uv` commands work as aforementioned provided that the timestamp cutoff for the command
and in the lockfile match, i.e. previously locked versions of packages will be preferred.

### Removing or amending the timestamp cutoff
- Amending any of the cutoffs (global or package-specific) will cause `uv` to ignore the existing lockfile.

- Dependencies are resolved against the new timestamp cutoff(s), or lack thereof.
Therefore, all available upgrades will be triggered.

- Therefore, unless the desire is to update all dependencies, the timestamp cutoff(s) for a
`uv` command should be set to the one(s) in the lockfile. We try to do this in the `just` recipes.

### Implmenting the cooldown period in `just` recipes

|`just` recipe|Default timestamp cutoff value|Can be overridden?|
|-------------|------------------------------|------------------|
|`virtualenv`|Not set|N/A|
|`requirements-dev`|Lockfile timestamp(s)|Only the global cutoff, via setting `UV_EXCLUDE_NEWER`|
|`requirements-prod`|Lockfile timestamp(s)|Only the global cutoff, via setting `UV_EXCLUDE_NEWER`|
|`upgrade`|Lockfile timestamp(s)|Yes - for the global cutoff, set `UV_EXCLUDE_NEWER`, for the target package for the upgrade, pass the `package-date` argument|
|`update-dependencies`|Lockfile timestamp(s) or as specified by "date" parameter|Only the global cutoff, via setting `UV_EXCLUDE_NEWER`[^2]|
|`devenv`|(Lockfile timestamp(s))|No, as this command just syncs the lockfile and environment|
|`prodenv`|(Lockfile timestamp(s))|No, as this command just syncs the lockfile and environment|

- Most `just` recipes will set the timestamp cutoff to the one(s) in the lockfile.
- Some recipes allow the global timestamp cutoff to be overridden via the `UV_EXCLUDE_NEWER` environment variable.
- The `upgrade` recipe allows a package-specific timestamp cutoff to be set via the `package-date` argument.
(e.g. `just upgrade prod osgithub now`).
- The `update-dependencies` recipe allows the timestamp cutoff to be renewed via the "date" parameter
(e.g. `just update-dependencies '7 days ago'`).


### Limitations of implementing the cooldown period via `uv`
- All commands except `devenv` and `prodenv`:
    - Pinning a package via setting a package-specific timestamp cutoff earlier than the global timestamp
    is not supported. Pinning must be done via a version constraint in the `pyproject.toml` file
    (e.g. `osgithub<=0.3.5`).
- `update-dependencies`:
    - If a date set via the `date` parameter is earlier than the global lockfile timestamp,
    the global lockfile timestamp will be used instead. This is to prevent accidental downgrades.
    - If a date set via the `date` parameter is earlier than a given package-specific timestamp cutoff,
    the package-specific timestamp cutoff will be retained. Again, this is to prevent accidental downgrades.
    - Currently there is no way of downgrading via `update-dependencies`, deliberate or not.
### CI
- In 6d751fa, I have copied what's done for [r-docker](https://github.com/opensafely-core/r-docker/commit/b3fd60830e221d84a2f70038a4374c89ae812b75),
and add astral's `setup-uv` action as a job in the workflow.
- To follow good practice, the action is pinned to a specific commit SHA.

### Dockerfile
- To set up the Dockerfile to use `uv`, we need to change the `builder`
and `actions-registry-dev` images to use `uv` instead of `pip`.
- We can copy the `uv` executable from astral's `uv` image from the container registry.
- (Possibly we would want to pin a SHA for this as well?)
- We would need to set some environment variables,
e.g. setting `UV_PYTHON_DOWNLOADS=never` ensures that we only use the system Python.

# Notes during the spike

These are here to provide a bit more extra context - stop here if you want to.

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


## How can we use `uv` to manage our dependencies?

These are loose notes instead of crafted, organsied sections.

### Adding / removing / altering constraints of dependencies
There are two ways to add, remove or alter the constraints of dependencies:
1. Edit the `pyproject.toml` file directly and run `uv sync` to update the lockfile and the environment.
2. Use the `uv` commands (the effects of `sync` are implicit):
- To add a dependency, use `uv add <package>`.
- To remove a dependency, use `uv remove <package>`.
- To alter a dependency, use `uv add` with a string containing the constraint (e.g. `uv add "httpx>0.1.0"`).

### Differentiating between dev and prod dependencies
To differentiate between dev and prod dependencies, we can use the `--dev` flag in combination with `uv add` and `uv remove`.
The next section will show this in action.

### Example usage: behaviour with no timestamp cutoff
As we shall see later, having a timestamp cutoff for resolving dependencies is important to us, but also complicates things.
This section first discusses the behaviour of `uv` commands when no timestamp cutoff is set, via an example.

Suppose we run the following on March 22:
```bash
uv add osgithub
uv add pre-commit --dev
```

The `pyproject.toml` will gain the following sections:
```toml
...
dependencies = [
    "osgithub>=0.3.5",
]
...
[dependency-groups]
dev = [
    "pre-commit>=4.2.0",
]
...
```

We notice that `uv` has added constraints for us that correspond to the latest versions of the packages at the time of running the command.

No packages that `osgithub` or `pre-commit` depend on are added to the `pyproject.toml` file - these are captured in the lockfile.
The lockfile will detail the `osgithub` and `pre-commit` packages, and their dependencies.
If you take a look at the version numbers, you will see that they are the latest versions at the time of running the command.

Suppose some time passes and the date is now April 1.
The latest version of `osgithub` is now 0.4.0; it was released on March 24.
Incidentally, `urlnormalize`, which `pre-commit` depends on, has a new version 20.30.0, which was released on March 31.

We want to make an update to the code that requires `osgithub` to be version 0.4.0 or higher.
We are confident about this move, since `osgithub` 0.4.0 is a dependency that we wrote and maintain.
We don't care about `virtualenv` for now, so we don't want to update it (and shouldn't, according to our policy of only
updating dependencies to releases that are at least a week old).

We can edit the constraint in the `pyproject.toml` file to be:
```toml
dependencies = [
    "osgithub>=0.4.0",
]
```
Then we run `uv sync` to update the lockfile and the environment.
`uv` will update the lockfile and environment to match the new constraint.
```sh
actions-registryalice@lunapiena:~/code/actions-registry$ uv sync
Resolved 25 packages in 20ms
Uninstalled 1 package in 0.68ms
Installed 1 package in 2ms
 - osgithub==0.3.5
 + osgithub==0.4.0
 ```
(Again, one could have run `uv add osgithub>=0.4.0` to edit the `pyproject.toml` file and sync in one step.)

We see that `virtualenv` was not updated despite the fact that a new version was released.
This is expected. From the [`uv` docs](https://docs.astral.sh/uv/concepts/projects/sync/#upgrading-locked-package-versions):
>With an existing uv.lock file, uv will prefer the previously locked versions of packages when running uv sync and uv lock.
>Package versions will only change if the project's dependency constraints exclude the previous, locked version.

In fact, to upgrade `virtualenv` (and other packages with new versions), we would need to explictly run `uv sync` with the `upgrade` flag:
```sh
actions-registryalice@lunapiena:~/code/actions-registry$ uv sync --upgrade
Resolved 25 packages in 109ms
Prepared 4 packages in 0.65ms
Uninstalled 4 packages in 5ms
Installed 4 packages in 7ms
 - cattrs==24.1.2
 + cattrs==24.1.3
 - typing-extensions==4.12.2
 + typing-extensions==4.13.0
 - url-normalize==1.4.3
 + url-normalize==2.2.0
 - virtualenv==20.29.3
 + virtualenv==20.30.0
```
There is also an `--upgrade-package` flag that can be used to only upgrade a specific package.

Under this default behaviour, if we have a weekly automated action to upgrade dependencies,
we can lean on that weekly update and usually won't be running `uv sync --upgrade` manually.

We'd focus on adding/removing/altering constraints for packages that are relevant to the current work, in this case, `osgithub`.
We would commit the `uv.lock` file (with only `osgithub` upgraded) to our working branch.

Another dev that checks out this branch can run `uv sync --frozen` to get their environment in sync with the lockfile.

### Behaviour with timestamp cutoff

**Note: The key takeaway is that `uv` ignores a lockfile if the lockfile's timestamp cutoff is different from what it receives in the command. This might lead to undesired behaviour.**

`uv` allows us to set a timestamp cutoff via the `--exclude-newer` flag, or the equivalent `UV_EXCLUDE_NEWER` environment variable.
From the [`uv` docs](https://docs.astral.sh/uv/reference/settings/#exclude-newer), the flag instructs to:

> Limit candidate packages to those that were uploaded prior to the given date.

So, suppose one runs the following on April 1:
```bash
uv add osgithub --exclude-newer "2025-03-22T15:00:00Z"
uv add pre-commit --dev --exclude-newer "2025-03-22T15:00:00Z"
```

We'd end up with the same `pyproject.toml` as before, with `osgithub>=0.3.5` and `pre-commit>=4.2.0`.

In the `uv.lock` file, we'd have `osgithub==0.3.5` and `pre-commit==4.2.0`. (And `virtualenv==20.29.3`.)
But, there will be a section in the lockfile that looks like this:
```toml
[options]
exclude-newer = "2025-03-22T15:00:00Z"
```

**We see that the timestamp cutoff is now written into the lockfile.**

Suppose we realise that we need to update `osgithub` to 0.4.0.
But we don't want to update `virtualenv`.

We edit the the constraint in the `pyproject.toml` file:
```toml
dependencies = [
    "osgithub>=0.4.0",
]
```

And run `uv sync`:
```sh
actions-registryalice@lunapiena:~/code/actions-registry$ uv sync
Ignoring existing lockfile due to removal of timestamp cutoff: `2025-03-22T15:00:00Z`
Resolved 25 packages in 14ms
Uninstalled 5 packages in 9ms
Installed 5 packages in 9ms
 - cattrs==24.1.2
 + cattrs==24.1.3
 - osgithub==0.3.5
 + osgithub==0.4.0
 - typing-extensions==4.12.2
 + typing-extensions==4.13.0
 - url-normalize==1.4.3
 + url-normalize==2.2.0
 - virtualenv==20.29.3
 + virtualenv==20.30.0
 ```

We see that `uv` ignores the lockfile because we removed the timestamp cutoff.
It behaves as if there is no lockfile, and therefore goes for the latest versions of all packages that fit
the constraints in `pyproject.toml`.
The new `uv.lock` file will not have any timestamp cutoff.

Note that if we try syncing again with the timestamp cutoff, we will get an error:
```sh
actions-registryalice@lunapiena:~/code/actions-registry$ uv sync --exclude-newer "2025-03-22T15:00:00Z"
Ignoring existing lockfile due to addition of timestamp cutoff: `2025-03-22T15:00:00Z`
  × No solution found when resolving dependencies:
  ╰─▶ Because only osgithub<0.4.0 is available and your project depends on osgithub>=0.4.0, we can conclude that your project's requirements are unsatisfiable.
```

We are presented with two options:

1.  We can try to set a new global timestamp cutoff, since we know `osgithub` was updated on March 24.
```sh
(actions-registry) alice@lunapiena:~/code/actions-registry$ uv sync --exclude-newer "2025-03-24"
Ignoring existing lockfile due to addition of timestamp cutoff: `2025-03-25T00:00:00Z`
Resolved 25 packages in 14ms
Uninstalled 4 packages in 11ms
Installed 4 packages in 14ms
 - cattrs==24.1.3
 + cattrs==24.1.2
 - typing-extensions==4.13.0
 + typing-extensions==4.12.2
 - url-normalize==2.2.0
 + url-normalize==1.4.3
 - virtualenv==20.30.0
 + virtualenv==20.29.3
```
i.e. we update some other packages alongside updating `osgithub`.

2. We can retain the original global timestamp cutoff and set a separate timestamp cutoff for `osgithub`.
This uses the `exclude-newer-package` flag newly available in `uv 0.8.4`[^3].

The command would look like this:
```sh
uv sync --exclude-newer "2025-03-22T15:00:00Z" --exclude-newer-package osgithub="2025-03-31T00:00:00Z"
```

Running it then updates `osgithub` only:
```sh
(actions-registry) alice@lunapiena:~/code/actions-registry$ uv sync --exclude-newer "2025-03-22T15:00:00Z"  --exclude-newer-package osgithub="2025-03-31T00:00:00Z"
Ignoring existing lockfile due to change in timestamp cutoff: `global: 2025-03-22T15:00:00Z` vs. `global: 2025-03-22T15:00:00Z, osgithub: 2025-03-31T00:00:00Z`
Resolved 65 packages in 13ms
Uninstalled 1 package in 0.24ms
Installed 1 package in 3ms
 - osgithub==0.3.5
 + osgithub==0.4.0
 ```

 and both the global timestamp cutoff and the package-specific timestamp cutoffs have been written to the lockfile:

```toml
[options]
exclude-newer = "2025-03-22T15:00:00Z"

[options.exclude-newer-package]
osgithub = "2025-03-31T00:00:00Z"
```

Note that the lockfile is still "ignored" in the sense that resolution still
occurs - we just get to keep the existing timestamp cutoff for the other packages.

### Aligning timestamp cutoffs
In the above scenario, we are trying to update a package to a release that is after the existing timestamp
cutoff in the lockfile without affecting the other packages.

What if we are in a situation where we're happy to respect the existing timestamp cutoff, and just need to add a new package?
Then, we would need to read off the timestamp cutoff from the lockfile, and pass it to the `uv` command.
```sh
actions-registryalice@lunapiena:~/code/actions-registry$ uv add bs4 --exclude-newer "2025-03-22T15:00:00Z"
Resolved 28 packages in 126ms
Prepared 3 packages in 66ms
Installed 3 packages in 9ms
 + beautifulsoup4==4.13.3
 + bs4==0.0.2
 + soupsieve==2.6
```

We see that since the `--exclude-newer` value matches the global timestamp cutoff in the lockfile, the lockfile is not ignored.
**In other words, to avoid undesired updates, the `uv` command must be run with the same timestamp cutoff as the one in the lockfile.**

The same applies to the package-specific timestamp cutoffs.
We would need to read the cutoffs from the lockfile and pass them via `--exclude-newer-package` to the `uv` command.

In general, we should write `just` recipes that will run `uv` commands with the same timestamp cutoff(s) as the one in the lockfile.

It should also be noted that if we would be committing lockfiles with a timestamps to branches, we should pay attention to use the `--frozen` flag
when we checkout the branch and want to sync the environment with the lockfile.

The `--frozen` flag ensures that all we do is sync the environment with the lockfile:
```sh
actions-registryalice@lunapiena:~/code/actions-registry$ uv sync --frozen
Installed 3 packages in 7ms
 + beautifulsoup4==4.13.3
 + bs4==0.0.2
 + soupsieve==2.6
```

If the `--frozen` flag is not set, `uv` will ignore the lockfile, throw the timestamp out,
and start resolving dependencies from the `pyproject.toml` file. It will be upgrading packages to the latest versions, as seen before.

So, any `just` recipes we write for syncing the venv should ensure that the `--frozen` flag is set appropriately.

The overarching conclusion I'm drawing is that if we are to use `uv` to manage dependencies and take advantage of the `--exclude-newer` flag
to implement our dependency updates policy,
we need to do so in a way that ensures that the lockfile is never accidentally ignored when running `uv` commands,
and we should craft our `just` recipes accordingly.

### How can we make sure the lockfile is never accidentally ignored?

For recipes like `devenv` and `prodenv`,
we should make sure that the command being run is `uv sync --frozen` and not `uv sync`,
since we are only wanting to sync the environment with the lockfile.

Things are trickier for the commands that actually call `uv lock`.
We need to take care that we use the lockfile timestamp.
Currently, `grep` is used to read off the global timestamp cutoff,
and `sed` is used to read off the package-specific timestamp cutoffs.
I might iterate on the specific implementation when time comes.

[^1]: See the [`uv` docs](https://docs.astral.sh/uv/concepts/projects/sync/#upgrading-locked-package-versions)
[^2]: Although it is probably much better to use the `date` parameter to set the timestamp cutoff
[^3]: https://github.com/astral-sh/uv/releases/tag/0.8.4
