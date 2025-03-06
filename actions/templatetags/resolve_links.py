import re

from django import template


register = template.Library()


@register.filter
def resolve_image_links(readme, version):
    url_template = "{github_url}blob/{tag}/{filename}?raw=true"

    pattern = re.compile(r'<img src="((?!.*?(http|\.com|\.uk|\.net)).*?)"')

    for filename, _ in pattern.findall(readme):
        url = url_template.format(
            github_url=version.action.get_github_url(),
            tag=version.tag,
            filename=filename,
        )
        # Replace the relative path with the full URL throughout the readme,
        # not just the img src attribute
        readme = readme.replace(filename, url)
    return readme
