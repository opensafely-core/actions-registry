import ast
import json
from base64 import b64decode

import requests
from environs import Env
from furl import furl


env = Env()


class GithubAPIException(Exception):
    ...


class GithubClient:
    """
    A connection to the Github API
    """

    user_agent = "OpenSAFELY Actions"
    base_url = "https://api.github.com"

    def __init__(self):
        token = env.str("GITHUB_TOKEN", None)
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": self.user_agent,
        }
        if token:
            self.headers["Authorization"] = f"token {env.str('GITHUB_TOKEN')}"

        self.session = requests.Session()

    def _get_json(self, path_segments, **add_args):
        """
        Builds and calls a url from the base and path segments
        Returns the response as json
        """
        f = furl(self.base_url)
        f.path.segments += path_segments
        if add_args:
            f.add(add_args)
        response = self.session.get(f.url, headers=self.headers)

        # Report some expected errors
        if response.status_code == 403:
            errors = response.json().get("errors")
            if errors:
                for error in errors:
                    if error["code"] == "too_large":
                        raise GithubAPIException("Error: File too large")
            else:
                raise GithubAPIException(json.dumps(response.json()))
        elif response.status_code == 404:
            raise GithubAPIException(response.json()["message"])
        # raise any other unexpected status
        response.raise_for_status()
        response_json = response.json()
        return response_json

    def get_repo(self, owner_and_repo):
        """
        Ensure a repo exists and return a GithubRepo
        """
        owner, repo = owner_and_repo.split("/")
        repo_path_seqments = ["repos", owner, repo]
        # call it to raise exceptions in case it doesn't exist
        self._get_json(repo_path_seqments)
        return GithubRepo(self, owner, repo)


class GithubRepo:
    """
    Fetch contents of a Github Repo
    """

    def __init__(self, client, owner, name, url=None, api_url=None):
        self.client = client
        self._owner = owner
        self._name = name
        self.repo_path_segments = ["repos", owner, name]
        self._url = url
        self._api_url = api_url

    @property
    def url(self):
        if self._url is None:
            self._url = f"https://github.com/{self._owner}/{self._name}"
        return self._url

    @property
    def api_url(self):
        if self._api_url is None:
            self._api_url = f"https://api.github.com/repos/{self._owner}/{self._name}"
        return self._api_url

    def get_contents(self, path, ref):
        """
        Fetch the contents of a path and ref (branch/commit/tag)

        Returns a single GithubContentFile if the path is a single file, or a list
        of GithubContentFiles if the path is a folder
        """
        path_segments = [*self.repo_path_segments, "contents", path]
        contents = self.client._get_json(path_segments, ref=ref)

        return GithubContentFile.from_json(contents)

    def get_readme(self, tag="main"):
        """
        Fetches the README.md of repo

        Args:
            tag (str): tag that you want the readme for.

        Returns:
            str: HTML from readme (at ROOT)
        """
        response = requests.get(
            url=self.api_url + "/readme",
            headers={"Accept": "application/vnd.github.v3.html+json"},
            params={"ref": tag},
        )
        decoded_response = response.content.decode("utf-8")
        return decoded_response

    def get_repo_details(self):
        """
        Fetches the About and Name of the repo

        Returns:
            dict: 2 key dictionary with about and name as keys
        """
        response = requests.get(url=self.api_url)

        contents = response.json()

        description = contents["description"]
        name = contents["name"]

        return {"name": name, "about": description}

    def get_tags(self):
        """
        Gets a list of tags associated with a repo

        Returns:
            List of Dicts (1 per tag).
        """
        response = requests.get(
            url=self.api_url + "/tags",
            headers={"Accept": "application/vnd.github.v3.json"},
        )
        decoded_response = response.content.decode()
        full_tag_list = ast.literal_eval(decoded_response)

        simple_tag_list = []
        for tag in full_tag_list:
            tag_dict = {"tag_name": tag["name"], "sha": tag["commit"]["sha"]}
            simple_tag_list.append(tag_dict)

        return simple_tag_list

    def get_commit(self, sha):
        """
        Get details of a specific commit

        Returns:
            Dict: Details of commit
        """
        response = requests.get(
            url=f"{self.api_url}/git/commits/{sha}",
            headers={"Accept": "application/vnd.github.v3.json"},
        )
        contents = response.json()
        return {
            "author": contents["author"]["name"],
            "date": contents["committer"]["date"][0:9],
        }


class GithubContentFile:
    """Holds information about a single file in a repo"""

    def __init__(self, name, last_updated, content, sha):
        self.name = name
        self.last_updated = last_updated
        self.content = content
        self.sha = sha

    @classmethod
    def from_json(cls, json_input):
        return cls(
            name=json_input.get("name"),
            content=json_input.get("content"),
            last_updated=json_input.get("last_updated"),
            sha=json_input["sha"],
        )

    @property
    def decoded_content(self):
        # self.content may be None when /contents has returned a list of files
        if self.content:
            return b64decode(self.content).decode("utf-8")
