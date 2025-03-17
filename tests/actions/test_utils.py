import pytest

from actions import utils


@pytest.mark.parametrize(
    "url,base_url,abs_url",
    [
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
    html = f'<img src="{url}"/>'

    resolved_html = utils.resolve_urls(html, [base_url], ["src"])

    expected_html = f'<img src="{abs_url}"/>'
    assert resolved_html == expected_html
