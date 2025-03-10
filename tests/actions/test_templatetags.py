from datetime import datetime, timezone

import pytest

import actions.templatetags.resolve_links as resolve_links
from actions.models import Action


@pytest.fixture
def version():
    action = Action.objects.create(
        org="opensafely-actions",
        repo_name="test-action",
    )
    return action.versions.create(
        tag="v1.0",
        committed_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


def test_resolve_relative_links_with_text_links(version):
    html = (
        'Here is link 1\n<a href="link_1.md">Link 1</a>\n'
        'Here is link 2\n<a href="https://site.com">Link 2</a>'
    )
    readme = resolve_links.resolve_relative_links(html, version)

    assert readme == (
        "Here is link 1\n"
        '<a href="https://github.com/opensafely-actions/test-action/blob/v1.0/link_1.md">Link 1</a>\n'
        "Here is link 2\n"
        '<a href="https://site.com">Link 2</a>'
    )


def test_resolve_relative_links_with_image_links(version):
    html = (
        "Here is image 1\n"
        '<a href="image_1.png">'
        '<img src="image_1.png" alt="Image 1"></a>\n'
        "Here is image 2\n"
        '<a href="https://site.com/image_2.png">'
        '<img src="https://site.com/image_2.png" alt="Image 2"></a>'
    )
    readme = resolve_links.resolve_relative_links(html, version)

    assert readme == (
        "Here is image 1\n"
        '<a href="https://github.com/opensafely-actions/test-action/blob/v1.0/image_1.png">'
        '<img src="https://github.com/opensafely-actions/test-action/blob/v1.0/image_1.png?raw=true" '
        'alt="Image 1"></a>\n'
        "Here is image 2\n"
        '<a href="https://site.com/image_2.png">'
        '<img src="https://site.com/image_2.png" alt="Image 2"></a>'
    )
