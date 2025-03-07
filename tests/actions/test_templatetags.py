import re
from datetime import datetime, timezone

from actions.models import Action
from actions.templatetags import resolve_links


def test_resolve_image_links():
    action = Action.objects.create(
        org="opensafely-actions",
        repo_name="test-action",
    )
    version = action.versions.create(
        tag="v1.0",
        committed_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )

    img1_html = 'Here is image 1\n<a href="image_1.png"><img src="image_1.png" alt="Image 1"></a>'
    img2_html = 'Here is image 2\n<a href="https://site.com/image_2.png"><img src="https://site.com/image_2.png" alt="Image 2"></a>'
    readme = resolve_links.resolve_image_links(f"{img1_html}\n{img2_html}", version)

    # Relative path should be replaced with full URL
    assert '"image_1.png"' not in readme
    img1_url = r"https://github\.com/opensafely-actions/test-action/blob/v1\.0/image_1\.png\?raw=true"
    assert len(re.findall(img1_url, readme)) == 2

    # Full URL should not be replaced
    img2_url = r"https://site\.com/image_2\.png"
    assert len(re.findall(img2_url, readme)) == 2
