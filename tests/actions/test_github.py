import json
from os import environ

import pytest
from furl import furl

from actions.github import GithubAPIException, GithubClient, GithubRepo

from .conftest import remove_cache_file_if_exists


def register_uri(httpretty, path, status=200, body=None):
    url = furl("https://api.github.com")
    url.path.segments += [*path.split("/")]
    httpretty.register_uri(
        httpretty.GET,
        url.url,
        status=status,
        body=json.dumps(body or ""),
        match_querystring=True,
    )


def test_github_client_get_repo(httpretty):
    # Mock the github request
    register_uri(httpretty, "repos/test/foo", body={"name": "foo", "description": ""})
    client = GithubClient()
    repo = client.get_repo("test", "foo")
    assert repo.repo_path_segments == ["repos", "test", "foo"]


def test_github_client_token(reset_environment_after_test):
    """Authorization headers is set based on environment variable"""
    environ["GITHUB_TOKEN"] = "test"
    client = GithubClient()
    assert client.headers["Authorization"] == "token test"

    del environ["GITHUB_TOKEN"]
    client = GithubClient()
    assert "Authorization" not in client.headers


def test_github_client_get_repo_not_found(httpretty):
    # Mock the github request
    register_uri(httpretty, "repos/test/bar", status=404, body={"message": "Not found"})
    client = GithubClient()
    with pytest.raises(GithubAPIException, match="Not found"):
        client.get_repo("test", "bar")


@pytest.mark.parametrize("use_cache", [True, False])
def test_github_client_get_repo_with_cache(httpretty, use_cache):
    client = GithubClient(use_cache=use_cache)

    # set up mock request with valid response and call it
    register_uri(
        httpretty, "repos/test/test-cache", body={"name": "foo", "description": ""}
    )
    client.get_repo("test", "test-cache")

    # re-mock the repos request to a 404, should raise an exception if called directly
    register_uri(
        httpretty, "repos/test/test-cache", status=404, body={"message": "Not found"}
    )

    if use_cache:
        # No exception raised because the first response was cached
        client.get_repo("test", "test-cache")
    else:
        # Exception raised because the repos endpoint was fetched again
        with pytest.raises(GithubAPIException, match="Not found"):
            client.get_repo("test", "test-cache")


def test_github_repo_get_commit(httpretty):
    sha = "1" * 40
    commit_body = {
        "author": {"name": "Donald Duck"},
        "committer": {"date": "2021-03-01T10:00:00Z"},
    }
    register_uri(
        httpretty, f"repos/test/foo/git/commits/{sha}", status=200, body=commit_body
    )
    repo = GithubRepo(client=GithubClient(use_cache=False), owner="test", name="foo")
    assert repo.get_commit(sha) == {
        "author": "Donald Duck",
        "date": "2021-03-01T10:00:00Z",
    }


def test_github_repo_get_contributors(httpretty):
    contribs = [{"login": "octocat"}, {"login": "octodog"}]
    register_uri(httpretty, "repos/test/foo/contributors", status=200, body=contribs)
    repo = GithubRepo(client=GithubClient(use_cache=False), owner="test", name="foo")
    assert repo.get_contributors() == ["octocat", "octodog"]


@pytest.mark.parametrize(
    "use_cache,num_requests",
    [
        (True, 1),
        (False, 2),
    ],
)
def test_github_repo_get_topics(httpretty, use_cache, num_requests):
    register_uri(
        httpretty,
        "repos/test/foo",
        status=200,
        body={"name": "foo", "description": "a description", "topics": ["bar", "baz"]},
    )
    repo = GithubClient(use_cache=use_cache).get_repo("test", "foo")
    assert repo.get_topics() == ["bar", "baz"]
    assert len(httpretty.latest_requests()) == num_requests


def test_github_repo_get_tags(httpretty):
    sha1 = "1" * 40
    sha2 = "2" * 40
    tags = [
        {"name": "v1.0", "commit": {"sha": sha1}},
        {"name": "v2.0", "commit": {"sha": sha2}},
    ]
    register_uri(httpretty, "repos/test/foo/tags", status=200, body=tags)
    repo = GithubRepo(client=GithubClient(use_cache=False), owner="test", name="foo")
    assert repo.get_tags() == [
        {"tag_name": "v1.0", "sha": sha1},
        {"tag_name": "v2.0", "sha": sha2},
    ]


def test_github_repo_get_readme(httpretty):
    repo = GithubRepo(client=GithubClient(use_cache=False), owner="test", name="foo")
    readme_content = b"<div id='readme'><h1>Foo</h1><p>A README.</p></div>"
    httpretty.register_uri(
        httpretty.GET,
        "https://api.github.com/repos/test/foo/readme?ref=main",
        status=200,
        body=readme_content,
        match_querystring=True,
    )
    readme_content = repo.get_readme(tag="main")
    assert readme_content == "<div id='readme'><h1>Foo</h1><p>A README.</p></div>"


def test_github_repo_details(httpretty):
    register_uri(
        httpretty,
        "repos/test/foo",
        status=200,
        body={"name": "foo", "description": "A test repo"},
    )
    # If the repo is instantiated with an "about", the endpoint isn't called
    repo = GithubRepo(
        client=GithubClient(use_cache=False),
        owner="test",
        name="foo",
        about="A different description",
    )
    details = repo.get_repo_details()
    assert details == {"name": "foo", "about": "A different description"}
    assert httpretty.latest_requests() == []

    # instantiate with no "about" arg, need to fetch it for the details
    repo1 = GithubRepo(client=GithubClient(use_cache=False), owner="test", name="foo")
    details = repo1.get_repo_details()
    assert details == {"name": "foo", "about": "A test repo"}
    latest_requests = httpretty.latest_requests()
    assert len(latest_requests) == 1
    assert latest_requests[0].url == "https://api.github.com/repos/test/foo"


@pytest.mark.integration
def test_integration(reset_environment_after_test):
    """Test repo methods with a real github repo"""
    # make sure we start with a fresh cache
    remove_cache_file_if_exists()
    client = GithubClient(use_cache=True)
    # Set up a real repo
    repo = client.get_repo("opensafely", "output-explorer-test-repo")

    # Fetch README
    readme = repo.get_readme(tag="master")
    assert readme.startswith("<div")
    assert "This is a test repo for use by output-explorer's tests." in readme

    # Fetch details
    details = repo.get_repo_details()
    assert details == {
        "name": "output-explorer-test-repo",
        "about": "A test repo for output-explorer's tests",
    }

    # Fetch tags
    tagged_sha = "7a6f60e8e74b9c93a9c6322b3151ee437fa4be61"
    tags = repo.get_tags()
    assert len(tags) >= 1
    assert {"tag_name": "test-tag", "sha": tagged_sha} in tags

    # get commit details
    commit = repo.get_commit(sha=tagged_sha)
    assert commit == {"author": "Ben Butler-Cole", "date": "2021-06-02T10:52:37Z"}
