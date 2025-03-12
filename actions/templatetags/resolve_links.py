import re
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from django import template


register = template.Library()


def time_function(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start} seconds")
        return result

    return wrapper


@time_function
def replace_relative_urls_regex(readme, base_url):
    # Resolve relative links in link tags
    link_tag_pattern = r'(<a.*?href=")((?![^"]*(http|\.com|\.uk|\.net))[^"]*")'
    readme = re.sub(link_tag_pattern, rf"\1{base_url}\2", readme)

    # Resolve relative links in img tags (raw=true is needed to display images)
    img_tag_pattern = r'(<img .*?src=")((?![^"]*(http|\.com|\.uk|\.net))[^"]*)"'
    readme = re.sub(img_tag_pattern, rf'\1{base_url}\2?raw=true"', readme)
    return readme


@time_function
def replace_relative_urls_soup(readme, base_url):
    def is_relative_url(url):
        return re.search(r"http|\.com|\.uk|\.net", url) is None

    soup = BeautifulSoup(readme, "html.parser")
    for link_tag in soup.find_all("a"):
        href = link_tag.get("href")
        if href and is_relative_url(href):
            link_tag["href"] = urljoin(base_url, href)

    for img_tag in soup.find_all("img"):
        src = img_tag.get("src")
        if src and is_relative_url(src):
            img_tag["src"] = urljoin(base_url, src) + "?raw=true"

    return str(soup)


@register.filter
def resolve_relative_links(readme, version):
    base_url = urljoin(
        version.action.get_github_url(),
        f"blob/{version.tag}/",
    )
    return replace_relative_urls_soup(readme, base_url)
