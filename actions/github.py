import requests
from furl import furl


class GithubAPIException(Exception):
    ...


class GithubClient:
    """
    A connection to the Github API
    """

    user_agent = "OpenSAFELY Actions"
    base_url = "https://api.github.com"

    def __init__(self):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": self.user_agent,
        }
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
        if response.status_code == 404:
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

    def __init__(self, client, owner, name):
        self.client = client
        self._owner = owner
        self._name = name
        self.repo_path_segments = ["repos", owner, name]

    @property
    def api_url(self):
        return f"https://api.github.com/repos/{self._owner}/{self._name}"

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
            List of Dicts (1 per tag), with keys 'tag_name' and 'sha'
        """
        response = requests.get(
            url=self.api_url + "/tags",
            headers={"Accept": "application/vnd.github.v3.json"},
        )
        content = response.json()

        simple_tag_list = []
        for tag in content:
            tag_dict = {"tag_name": tag["name"], "sha": tag["commit"]["sha"]}
            simple_tag_list.append(tag_dict)

        return simple_tag_list

    def get_commit(self, sha):
        """
        Get details of a specific commit

        Returns:
            Dict: Details of commit, with keys of 'author' and 'date'
        """
        response = requests.get(
            url=f"{self.api_url}/git/commits/{sha}",
            headers={"Accept": "application/vnd.github.v3.json"},
        )
        contents = response.json()

        return {
            "author": contents["author"]["name"],
            "date": contents["committer"]["date"],
        }
