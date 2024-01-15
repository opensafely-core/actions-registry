from datetime import datetime, timezone

from actions.models import Action, Version


def test_get_latest_version():
    # Create an action
    action = Action(
        org="opensafely-actions",
        repo_name="test-action",
        about="Testing action",
    )
    action.save()

    # Create a version and check get_latest_version() get this
    version = Version(
        action=action,
        tag="v1.0",
        committed_at=datetime.now(timezone.utc),
        readme="first version",
    )
    version.save()
    latest_version = action.get_latest_version()
    assert latest_version.tag == "v1.0"
    assert latest_version.readme == "first version"

    # Create a second version and check get_latest_version() get this more up to date version
    version2 = Version(
        action=action,
        tag="v1.1",
        committed_at=datetime.now(timezone.utc),
        readme="second version",
    )
    version2.save()
    latest_version = action.get_latest_version()
    assert latest_version.tag == "v1.1"
    assert latest_version.readme == "second version"


def test_str():
    action = Action.objects.create(
        org="opensafely-actions",
        repo_name="test-action",
        about="Testing action",
    )
    version = action.versions.create(
        tag="v1.0",
        committed_at=datetime.now(timezone.utc),
        readme="first version",
    )

    assert str(action) == "test-action"
    assert str(version) == "test-action/v1.0"
