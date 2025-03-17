import pytest

from actions import utils


@pytest.mark.parametrize(
    "url,base_url,abs_url",
    [
        ("", "https://example.com", "https://example.com"),
        ("image.jpg", "https://example.com", "https://example.com/image.jpg"),
        ("./image.jpg", "https://example.com", "https://example.com/image.jpg"),
        ("../image.jpg", "https://example.com", "https://example.com/image.jpg"),
        (
            "https://example.com/image.jpg",
            "https://example.com",
            "https://example.com/image.jpg",
        ),
    ],
)
def test_resolve_urls(url, base_url, abs_url):
    resolved_html = utils.resolve_urls(f'<img src="{url}"/>', [base_url], ["src"])
    assert resolved_html == f'<img src="{abs_url}"/>'
