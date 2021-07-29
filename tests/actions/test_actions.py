from datetime import datetime

import pytest
from django.utils import timezone

from actions.models import Action, Version


@pytest.mark.django_db
def test_get_latest_version():
    # Create an action
    action = Action(
        name="test action",
        org="opensafely-actions",
        repo_name="test action",
        about="Testing action",
    )
    action.save()

    # Create a version and check get_latest_version() get this
    version = Version(
        action=action,
        tag="v1.0",
        date=datetime.now(timezone.utc),
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
        date=datetime.now(timezone.utc),
        readme="second version",
    )
    version2.save()
    latest_version = action.get_latest_version()
    assert latest_version.tag == "v1.1"
    assert latest_version.readme == "second version"