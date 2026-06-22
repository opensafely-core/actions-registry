"""A tool for interacting with GitHub repos.

This module provides a wrapper around the GitHub API, for interaction with repos and
repo contents.
Optionally uses requests caching to avoid repeated calls to the API.

  Typical usage example:

  client = GithubClient(token='my-github-token')
  repo = client.get_repo('my-github-user', 'my-repo')
"""

import json
from os import environ

import requests
import requests_cache
from furl import furl


class GithubAPIException(Exception):
    pass


class GithubClient:
    """
    A connection to the Github API
    Optionally uses request caching

    Attributes:
        user_agent (str): set from GITHUB_USER_AGENT environment variable; a string to
        identify the application
        base_url (str): the base github api url ('https://api.github.com')
        use_cache (bool): whether to use request caching; defaults to False
        token (str): GitHub token. Optional; required to access private repos and avoid
        anonymous rate-limiting
        expire_after (int): For cached requests, set a global expiry for the session (default = -1; never expires)
        urls_expire_after (dict): Set expiry on specific url patterns (falls back to `expire_after` if no match found), e.g.
            urls_expire_after = {
                '*/pulls': 60,  # expire requests to get pull requests after 60 secs
                '*/branches': 60 * 5, # expire requests to get branches after 5 mins
                '*/commits': 30,  # expire requests to get commits after 30 secs
            }
    """

    user_agent = environ.get("GITHUB_USER_AGENT", "")
    base_url = "https://api.github.com"

    def __init__(
        self, use_cache=False, token=None, expire_after=-1, urls_expire_after=None
    ):
        """Inits GithubClient, sets headers with token if provided and initialises session"""
        token = token or environ.get("GITHUB_TOKEN", None)
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": self.user_agent,
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
        if use_cache:
            self.session = requests_cache.CachedSession(
                backend="sqlite",
                cache_name=environ.get("REQUESTS_CACHE_NAME", "http_cache"),
                expire_after=expire_after,
                urls_expire_after=urls_expire_after,
            )
        else:
            self.session = requests.Session()

    def get(self, path_segments, headers, **add_args):
        """
        Builds and calls a url from the base and path segments

        Args:
            path_segments (list of str): segments of path after the base url
            headers: headers to pass to the request
            **add_args: any querystring args to be added (k=v pairs)

        Returns: Response
        """
        f = furl(self.base_url)
        f.path.segments += path_segments
        if add_args:
            f.add(add_args)
        return self.session.get(f.url, headers=headers)

    def get_json(self, path_segments, **add_args):
        """
        Builds and calls a url from the base and path segments

        Args:
            path_segments (list of str): segments of path after the base url
            **add_args: any querystring args to be added (k=v pairs)

        Returns: json

        Raises:
            GithubAPIException: other api errors
        """
        response = self.get(path_segments, self.headers, **add_args)

        # Report some expected errors
        if response.status_code == 403 and "errors" not in response.json():
            raise GithubAPIException(json.dumps(response.json()))

        if response.status_code == 404:
            raise GithubAPIException(response.json()["message"])

        # raise any other unexpected status
        response.raise_for_status()
        response_json = response.json()
        return response_json

    def get_repo(self, owner, name):
        """
        Ensure a repo exists

        Args:
            owner (str): repo owner
            name (str): repo name

        Returns:
            GithubRepo
        """
        repo_path_seqments = ["repos", owner, name]
        # call it to raise exceptions in case it doesn't exist
        repo_response = self.get_json(repo_path_seqments)
        return GithubRepo(self, owner, name, about=repo_response["description"])


class GithubRepo:
    """
    Interacts with a Github Repo

    Attributes:
        client (a GithubClient)
        owner (str): Repo owner
        name (str): Repo name
        about (str): Repo description
        repo_path_segments (list): base path segments for this repo, generated from owner and name
    """

    def __init__(self, client, owner, name, about=None):
        self.client = client
        self.owner = owner
        self.name = name
        self.about = about
        self.repo_path_segments = ["repos", owner, name]
        self._url = None

    def get_commit(self, sha):
        """
        Gets details of a specific commit

        Args:
            sha (str): commit sha

        Returns:
            Dict: Details of commit, with keys of 'author' and 'date'
        """
        path_segments = [*self.repo_path_segments, "git", "commits", sha]
        content = self.client.get_json(path_segments)
        return {
            "author": content["author"]["name"],
            "date": content["committer"]["date"],
        }

    def get_contributors(self):
        """
        Gets contributors to the repo

        Returns:
            List of strings, each representing a contributor's login
        """
        path_segments = [*self.repo_path_segments, "contributors"]
        content = self.client.get_json(path_segments)
        contrib_list = [contrib["login"] for contrib in content]
        return contrib_list

    def get_tags(self):
        """
        Gets a list of tags associated with a repo

        Returns:
            List of Dicts (1 per tag), with keys 'tag_name' and 'sha'
        """
        path_segments = [*self.repo_path_segments, "tags"]
        content = self.client.get_json(path_segments)
        simple_tag_list = [
            {"tag_name": tag["name"], "sha": tag["commit"]["sha"]} for tag in content
        ]
        return simple_tag_list

    def get_topics(self):
        """
        Gets the repo's topics.

        If the repo's name and about are also being fetched from GitHub,
        consider setting `use_cache` to True in the GithubClient to avoid
        duplicate calls to the repo endpoint.

        Returns:
            list[str]: list of topics
        """
        content = self.client.get_json(self.repo_path_segments)
        return content["topics"]

    def get_readme(self, tag="main"):
        """
        Fetches the README.md of repo

        Args:
            tag (str): tag that you want the readme for.

        Returns:
            str: HTML from readme (at ROOT)
        """
        path_segments = [*self.repo_path_segments, "readme"]
        headers = {
            **self.client.headers,
            "Accept": "application/vnd.github.v3.html+json",
        }
        response = self.client.get(path_segments, headers, ref=tag)
        return response.content.decode("utf-8")

    def get_repo_details(self):
        """
        Fetches the About and Name of the repo

        Returns:
            dict: 2 key dictionary with about and name as keys
        """
        if self.about is None:
            response = self.client.get_json(self.repo_path_segments)
            self.about = response["description"]
        return {"name": self.name, "about": self.about}
