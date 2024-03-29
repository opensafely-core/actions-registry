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
It is deployed to our `dokku3` instance (see [Dokku Deployment](https://bennettinstitute-team-manual.pages.dev/tools-systems/dokku/)).

## Adding a new action

To add a new action, first edit `actions/jobs/daily/fetch_action.py`.

Then, as the `dokku` user on dokku3, run:

    $ dokku enter actions-registry

This starts a bash session connected to the docker container running the application.
Finally, run:

    $ python manage.py runjob actions fetch_action

This fetches metadata about all actions from GitHub.

## Updating the GitHub token

1. Log into the *opensafely-readonly* GitHub account (the credentials are in Bitwarden)
1. Go to *Settings* / *Developer settings* / *Personal access tokens* / [*Tokens (classic)*](https://github.com/settings/tokens)
1. Click on *actions-registry-token*
1. Click on *Regenerate token*
1. Set the expiry to 90 days
1. Copy the new token
1. ssh into `dokku3.ebmdatalab.net`
1. Run `dokku config:set actions-registry GITHUB_TOKEN=<the new token>`
