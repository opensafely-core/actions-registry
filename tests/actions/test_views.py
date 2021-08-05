import pytest

from actions.models import Action


@pytest.mark.django_db
def test_index(client):
    a1 = Action.objects.create(
        org="opensafely-actions",
        repo_name="test-action-1",
        about="Testing action",
    )
    a1.versions.create(
        tag="v1.0",
        date="2021-08-01 12:34:56+00:00",
        readme="first version",
    )
    a1.versions.create(
        tag="v1.1",
        date="2021-08-02 12:34:56+00:00",
        readme="second version",
    )

    a2 = Action.objects.create(
        org="opensafely-actions",
        repo_name="test-action-2",
        about="Testing action",
    )
    a2.versions.create(
        tag="v1.0",
        date="2021-08-03 12:34:56+00:00",
        readme="first version",
    )
    a2.versions.create(
        tag="v1.1",
        date="2021-08-04 12:34:56+00:00",
        readme="second version",
    )

    rsp = client.get("/")
    assert rsp.status_code == 200


@pytest.mark.django_db
def test_detail(client):
    a = Action.objects.create(
        org="opensafely-actions",
        repo_name="test action",
        about="Testing action",
    )
    a.versions.create(
        tag="v1.0",
        date="2021-08-01 12:34:56+00:00",
        readme="first version",
    )
    a.versions.create(
        tag="v1.1",
        date="2021-08-02 12:34:56+00:00",
        readme="second version",
    )

    rsp = client.get(f"/{a.id}/")
    assert rsp.status_code == 200
