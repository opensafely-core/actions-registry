# Notes for developers

## Setup

Set up a local development environment with:

```sh
just devenv
just npm-install
just npm-build
```

## Update the local project staticfiles and migrations

```sh
just collectstatic
just migrate
```

## Running locally

Start a development server with:

```sh
just run
```

## Tests

Run the tests with:

```sh
just test <args>
```

Any args are passed to pytest.

## Deployment

Deployment uses `dokku` and requires the environment variables defined in `dotenv-sample`.
It is deployed to our `dokku3` instance (see [Dokku Deployment](https://bennett.wiki/tools-systems/dokku/)).

## Adding a new action

To add a new action, first edit `actions/management/commands/fetch_action.py`.

Then, as the `dokku` user on dokku3, run:

```sh
dokku enter actions-registry
```

This starts a bash session connected to the docker container running the application.
Finally, run:

```sh
python manage.py fetch_action
```

This fetches metadata about all actions from GitHub.

## Updating the GitHub token

1. Log into the _opensafely-readonly_ GitHub account (the credentials are in Bitwarden)
1. Go to _Settings_ / _Developer settings_ / _Personal access tokens_ / [_Tokens (classic)_](https://github.com/settings/tokens)
1. Click on _actions-registry-token_
1. Click on _Regenerate token_
1. Set the expiry to 90 days
1. Copy the new token
1. ssh into `dokku3.ebmdatalab.net`
1. Run `dokku config:set actions-registry GITHUB_TOKEN=<the new token>`
