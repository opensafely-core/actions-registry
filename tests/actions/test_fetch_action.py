import json

import pytest
import responses
from django.core.management import CommandError, call_command

from actions.models import Action


@pytest.mark.django_db
def test_bad_organisation():
    with pytest.raises(CommandError, match="outside our allowed list"):
        call_command("fetch_action", "opensafely-core", "test-action")


@responses.activate
@pytest.mark.django_db
def test_missing_repo():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/opensafely-actions/test-action",
        status=404,
        body=json.dumps({"message": "Not Found"}),
    )
    with pytest.raises(CommandError, match="Repo not found"):
        call_command("fetch_action", "opensafely-actions", "test-action")


@responses.activate
@pytest.mark.django_db
def test_create():
    set_up_responses()
    call_command("fetch_action", "opensafely-actions", "test-action")
    verify_action()


@responses.activate
@pytest.mark.django_db
def test_update():
    a = Action.objects.create(
        org="opensafely-actions",
        repo_name="test-action",
        about="An outdated description",
    )
    a.versions.create(
        tag="v1.0",
        committed_at="2021-08-01 12:34:56+00:00",
        readme="old README",
    )

    set_up_responses()
    call_command("fetch_action", "opensafely-actions", "test-action")
    verify_action()


def set_up_responses():
    """Configure fake GitHub API responses for a dummy repo.

    The repo at opensafely-actions/test-action has two tags: v1.0 and v2.0.
    """

    sha1 = "1" * 40
    sha2 = "2" * 40

    responses.add(
        responses.GET,
        "https://api.github.com/repos/opensafely-actions/test-action",
        status=200,
        body=json.dumps({"name": "test-action", "description": "A brief description"}),
    )
    responses.add(
        responses.GET,
        "https://api.github.com/repos/opensafely-actions/test-action/tags",
        status=200,
        body=json.dumps(
            [
                {"name": "v1.0", "commit": {"sha": sha1}},
                {"name": "v2.0", "commit": {"sha": sha2}},
            ]
        ),
    )
    responses.add(
        responses.GET,
        "https://api.github.com/repos/opensafely-actions/test-action/readme?ref=v1.0",
        status=200,
        body='<div id="readme" class="md" data-path="README.md"><article class="markdown-body entry-content container-lg" itemprop="text"><h1>README 1</h1></article></div>',
    )
    responses.add(
        responses.GET,
        "https://api.github.com/repos/opensafely-actions/test-action/readme?ref=v2.0",
        status=200,
        body='<div id="readme" class="md" data-path="README.md"><article class="markdown-body entry-content container-lg" itemprop="text"><h1>README 2</h1></article></div>',
    )
    responses.add(
        responses.GET,
        f"https://api.github.com/repos/opensafely-actions/test-action/git/commits/{sha1}",
        status=200,
        body=json.dumps(
            {
                "sha": sha1,
                "author": {
                    "name": "Some User",
                    "email": "some-user@users.noreply.github.com",
                    "date": "2021-08-01T12:34:56Z",
                },
                "committer": {
                    "name": "GitHub",
                    "email": "noreply@github.com",
                    "date": "2021-08-01T12:34:56Z",
                },
            }
        ),
    )
    responses.add(
        responses.GET,
        f"https://api.github.com/repos/opensafely-actions/test-action/git/commits/{sha2}",
        status=200,
        body=json.dumps(
            {
                "sha": sha2,
                "author": {
                    "name": "Some Other User",
                    "email": "some-other-user@users.noreply.github.com",
                    "date": "2021-08-02T12:34:56Z",
                },
                "committer": {
                    "name": "GitHub",
                    "email": "noreply@github.com",
                    "date": "2021-08-02T12:34:56Z",
                },
            }
        ),
    )


def verify_action():
    """Verify that Action exists with properties matching those returned by the API."""

    a = Action.objects.get()
    assert a.org == "opensafely-actions"
    assert a.repo_name == "test-action"
    assert a.about == "A brief description"
    assert a.versions.count() == 2
    v1, v2 = a.versions.order_by("committed_at")
    assert v1.tag == "v1.0"
    assert str(v1.committed_at) == "2021-08-01 12:34:56+00:00"
    assert "README 1" in v1.readme
    assert v2.tag == "v2.0"
    assert "README 2" in v2.readme
    assert str(v2.committed_at) == "2021-08-02 12:34:56+00:00"
