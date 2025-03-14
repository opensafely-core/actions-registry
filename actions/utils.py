from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


def resolve_relative_urls_to_absolute(html, base_url, tag, attribute):
    soup = BeautifulSoup(html, "html.parser")
    for element in soup.find_all(tag):
        url = element.get(attribute)
        if url and not urlparse(url).netloc:  # is relative
            element[attribute] = urljoin(base_url, url)
    return str(soup)
