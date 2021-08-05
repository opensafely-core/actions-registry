# Notes for developers

## Setup

Set up a local development environment with:

```
just dev_setup
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
