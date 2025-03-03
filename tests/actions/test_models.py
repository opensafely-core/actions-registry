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


def test_get_latest_version(action):
    # Create a version and check get_latest_version() get this
    Version.objects.create(
        action=action,
        tag="v1.0",
        committed_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        readme="first version",
    )
    latest_version = action.get_latest_version()
    assert latest_version.tag == "v1.0"
    assert latest_version.readme == "first version"

    # Create a second version and check get_latest_version() get this more up to date version
    Version.objects.create(
        action=action,
        tag="v1.1",
        committed_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        readme="second version",
    )
    latest_version = action.get_latest_version()
    assert latest_version.tag == "v1.1"
    assert latest_version.readme == "second version"


def test_str(action):
    version = action.versions.create(
        tag="v1.0",
        committed_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        readme="first version",
    )

    assert str(action) == "test-action"
    assert str(version) == "test-action/v1.0"
