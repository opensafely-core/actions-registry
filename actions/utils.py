from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


def resolve_urls(html, base_urls, attributes):
    soup = BeautifulSoup(html, "html.parser")

    def resolve(base_url, attribute):
        for element in soup.find_all(lambda element: element.has_attr(attribute)):
            url = element.get(attribute)
            if not urlparse(url).netloc:  # is relative
                element[attribute] = urljoin(base_url, url)

    for base_url, attribute in zip(base_urls, attributes):
        resolve(base_url, attribute)

    return str(soup)
