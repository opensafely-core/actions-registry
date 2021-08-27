# Notes for developers

## Setup
Set up local config:
```
just dev_config
```

Set up a local development environment with:

```
just dev_setup
just npm-install
just npm-build
```

## Update the local project staticfiles and migrations
```
just collectstatic
just migrate
```

## Running locally

Start a development server with:

```
just run
```

## Tests

Run the tests with:

```
just test <args>
```

Any args are passed to pytest.

## Deployment

Deployment should happen automatically when a branch is merged into `main` on GitHub.

To deploy manually:

```
# Add a remote
$ git remote add dokku dokku@dokku2:

# Push the main branch to dokku
$ git push dokku main
```

## Updating the database

As the `dokku` user on dokku2, run:

    $ dokku enter actions-registry

This starts a bash session connected to the docker container running the application.
You can now run any Django management command, including:

    $ ./manage.py fetch_action opensafely-actions [repo-name]

This fetches metadata about the given action from GitHub.
