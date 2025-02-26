from datetime import datetime, timezone

import pytest

from actions.models import Action, Version


@pytest.fixture
def action():
    return Action.objects.create(
        org="opensafely-actions",
        repo_name="test-action",
        about="Testing action",
    )


def create_version(action_, tag, readme=None):
    return Version.objects.create(
        action=action_,
        tag=tag,
        committed_at=datetime.now(timezone.utc),
        readme=readme or f"Version {tag}",
    )


def test_get_latest_version(action):
    # Create a version and check get_latest_version() get this
    create_version(action, "v1.0", "first version")
    latest_version = action.get_latest_version()
    assert latest_version.tag == "v1.0"
    assert latest_version.readme == "first version"

    # Create a second version and check get_latest_version() get this more up to date version
    create_version(action, "v1.1", "second version")
    latest_version = action.get_latest_version()
    assert latest_version.tag == "v1.1"
    assert latest_version.readme == "second version"


def test_str(action):
    version = create_version(action, "v1.0", "first version")

    assert str(action) == "test-action"
    assert str(version) == "test-action/v1.0"
