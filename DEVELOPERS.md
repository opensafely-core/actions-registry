# Notes for developers

## Setup
Set up a local development environment with:

```
just devenv
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

Deployment uses `dokku` and requires the environment variables defined in `dotenv-sample`.
It is deployed to our `dokku1` instance (see [Dokku Deployment](https://bennettinstitute-team-manual.pages.dev/tools-systems/dokku/)).

## Updating the database

As the `dokku` user on dokku1, run:

    $ dokku enter actions-registry

This starts a bash session connected to the docker container running the application.
You can now run any Django management command, including:

    $ ./manage.py fetch_action opensafely-actions [repo-name]

This fetches metadata about the given action from GitHub.
