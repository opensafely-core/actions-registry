import re
from urllib.parse import urljoin

from django import template


register = template.Library()


@register.filter
def resolve_relative_links(readme, version):
    base_url = urljoin(
        version.action.get_github_url(),
        f"blob/{version.tag}/",
    )

    # Resolve relative links in link tags
    link_tag_pattern = r'(<a href=")((?!.*?(http|\.com|\.uk|\.net)).*?")'
    readme = re.sub(link_tag_pattern, rf"\1{base_url}\2", readme)

    # Resolve relative links in img tags (raw=true is needed to display images)
    img_tag_pattern = r'(<img src=")((?!.*?(http|\.com|\.uk|\.net)).*?)"'
    readme = re.sub(img_tag_pattern, rf'\1{base_url}\2?raw=true"', readme)
    return readme
