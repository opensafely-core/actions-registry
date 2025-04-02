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


## How can we use `uv` to manage our dependencies?

These are loose notes instead of crafted, organsied sections.

### The `uv` lockfile and how `uv` uses `pyproject.toml`

What is the `uv` lockfile?
From the [uv docs](https://docs.astral.sh/uv/concepts/projects/layout/#the-lockfile):

> `uv.lock` is a human-readable TOML file but is managed by uv and should not be edited manually.

> This file should be checked into version control, allowing for consistent and reproducible installations across machines.

>Unlike the pyproject.toml, which is used to specify the broad requirements of your project, the lockfile contains the exact resolved versions that are installed in the project environment.

We can manually edit the `pyproject.toml` file instead of the `uv.lock` file.
`uv` uses sections in `pyproject.toml` to manage dependencies.
It will aim to reflect any changes made to `pyproject.toml` in the `uv.lock` file (Command: `uv lock`).
Then, it will sync the environment with the  `uv.lock` (Command: `uv sync`).

The behaviour of `uv sync` is altered by flags:
- Running `uv sync` without the `--locked` flag implicitly runs `uv lock`:
`uv` will update both the lockfile and the environment to match `pyproject.toml`.
- Running `uv sync` with the `--locked` flag will sync the environment with the lockfile, but before doing so,
it will run a check on the lockfile and error if it is outdated relative to `pyproject.toml`.
- Running `uv sync` with the `--frozen` flag will update the environment with the lockfile as the source of truth (rather than `pyproject.toml`).

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

It seems like we are a bit stuck here.
We have a couple of options:
1. We can spontaneously review the changelog of `cattrs`, `typing-extensions`, `url-normalize` and `virtualenv`.
This is clearly not great - `url-normalize` updated from 1.4.3 to 2.2.0, that doesn't seem like a trivial review.

2. We can try to set a new timestamp cutoff, since we know `osgithub` was updated on March 24.
```sh
actions-registryalice@lunapiena:~/code/actions-registry$ uv sync --exclude-newer "2025-03-24"
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
This works, but that is because `cattrs` etc. all happened to have been updated after March 24.
If `url-normalize` had been updated on March 23 (instead of March 30), we would have been forced to review its changelog.

3. We can remove the timestamp cutoff from the lockfile, and run `uv sync` again.
First revert the change in constraint and revert the lockfile and environment:
```sh
actions-registryalice@lunapiena:~/code/actions-registry$ uv add "osgithub>=0.3.5" --exclude-newer "2025-03-22T15:00:00Z"
Ignoring existing lockfile due to addition of timestamp cutoff: `2025-03-22T15:00:00Z`
Resolved 25 packages in 19ms
Uninstalled 4 packages in 4ms
Installed 4 packages in 5ms
 - cattrs==24.1.3
 + cattrs==24.1.2
 - osgithub==0.4.0
 + osgithub==0.3.5
 - typing-extensions==4.13.0
 + typing-extensions==4.12.2
 - url-normalize==2.2.0
 + url-normalize==1.4.3
 ```

Then, manually delete the timestamp cutoff from the lockfile.
This time, `uv` will not ignore the lockfile.
It will respect that the package versions in the lockfile already fit the constraints in `pyproject.toml`, except for one:
```sh
actions-registryalice@lunapiena:~/code/actions-registry$ uv add "osgithub>=0.4.0"
Resolved 25 packages in 12ms
Uninstalled 1 package in 0.81ms
Installed 1 package in 4ms
 - osgithub==0.3.5
 + osgithub==0.4.0
```

This achieves what we want, but is a fiddly solution.
As a reminder, the recommendation of the `uv` docs is to not edit the lockfile manually:

> `uv.lock` is a human-readable TOML file but is managed by uv and should not be edited manually.

But this seems to be the only sane option to only update the package we want to update, and not the others.

### Aligning timestamp cutoffs
The above scenario is a bit extreme, since we are trying to update a package to a release that is after the existing timestamp
cutoff in the lockfile without affecting the other packages.

What if we are in a situation where we're happy to respect the existing timestamp cutoff? Then, the situation is straightforward.
We would need to read off the timestamp cutoff from the lockfile, and pass it to the `uv` command.
```sh
actions-registryalice@lunapiena:~/code/actions-registry$ uv add bs4 --exclude-newer "2025-03-22T15:00:00Z"
Resolved 28 packages in 126ms
Prepared 3 packages in 66ms
Installed 3 packages in 9ms
 + beautifulsoup4==4.13.3
 + bs4==0.0.2
 + soupsieve==2.6
```

We see that since the `--exclude-newer` value matches the one in the lockfile, the lockfile is not ignored.
**In other words, to avoid undesired updates, the `uv` command must be run with the same timestamp cutoff as the one in the lockfile.**

It is only when the above is impossible (e.g. the scenario above where we want to update `osgithub` to a release that is newer than the timestamp cutoff in the lockfile) that things become tricky.

In general, we should write `just` recipes that will run `uv` commands with the same timestamp cutoff as the one in the lockfile.

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

Things are trickier for the commands that actually manage dependencies.
(i.e. those that aim to alter `pyproject.toml` and the lockfile.)

#### Approach 1: Set `UV_EXCLUDE_NEWER` for all `uv` commands
Assume a timestamp cutoff is committed to the lockfile.
If we set `UV_EXCLUDE_NEWER` to the timestamp we read from the lockfile:
```sh
LOCKFILE_TIMESTAMP=$(grep -n exclude-newer uv.lock | cut -d'=' -f2 | cut -d'"' -f2)
export UV_EXCLUDE_NEWER=$LOCKFILE_TIMESTAMP
```
then all `uv` commands would see the environment variable and the lockfile will not be ignored.

So, maybe we can set `UV_EXCLUDE_NEWER` in the justfile, and then run `uv` commands exclusively via `just`.

Commands like `update-dependencies` should of course, be setting a new timestamp cutoff and writing it to the lockfile:
```sh
update-dependencies *args: virtualenv
    #!/usr/bin/env bash
    set -euo pipefail

    UV_EXCLUDE_NEWER=$(date -d '-7 days' +"%Y-%m-%dT%H:%M:%SZ") uv sync
```

Would this mean wrapping all `uv` commands in `just`? `just add`, `just sync`, `just remove` etc.?

### Approach 2: Only set `UV_EXCLUDE_NEWER` for `uv sync`
Instead of wrapping all `uv` commands in `just`, we could dictate that changes to project dependencies be made
via directly editing the `pyproject.toml` file followed by running a just command that wraps `uv sync`.
(i.e., we don't wrap `uv add` or `uv remove` in `just`.)

```sh
sync *args: virtualenv
    #!/usr/bin/env bash
    set -euo pipefail

    # Sync environment and lockfile with pyproject.toml
    # Resolves dependencies using existing lockfile timestamp cutoff if available; override via setting UV_EXCLUDE_NEWER
    LOCKFILE_TIMESTAMP=$(grep -n exclude-newer uv.lock | cut -d'=' -f2 | cut -d'"' -f2) || (uv sync {{ args }}; exit 0)
    UV_EXCLUDE_NEWER=${UV_EXCLUDE_NEWER:-$LOCKFILE_TIMESTAMP} uv sync {{ args }}
```

This is much like the pip-tools based approach of editing the `requirements.in` file and running `pip-compile` to update the `requirements.txt` file.
Here, we don't set `UV_EXCLUDE_NEWER` globally in the justfile, but only for this recipe.

Similar to Approach 1, an `update-dependencies` recipe would be setting a new timestamp cutoff and writing it to the lockfile.

What should we call the just command? `sync`? `resolve-dependencies`? `requirements`?

### What if we need to disrespect the lockfile timestamp?
For both approaches 1 and 2, we need to figure out how to handle the case where we need to update a package to a version that is newer than the timestamp cutoff in the lockfile. (E.g. the `osgithub` example above.)

It is probably hard to avoid having to manually manipulate the lockfile timestamp.
We probably want to write a set of instructions, or create a `just` command specifically for that scenario.
