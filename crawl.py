from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag


def normalize_url(url) -> str:
    """
    Normalize a URL by parsing it and reconstructing it in a standard format.

    :param url: The URL to be normalized.
    :return: A normalized URL string.
    """

    response = urlparse(url)
    netloc = response.netloc.lower() # domain
    path = response.path.lower().rstrip('/') # subdomain
    # scheme = response.scheme.lower() # HTTP or HTTPS

    new_url = f'{netloc}{path}'
    return new_url


def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    h_tag = soup.find('h1')
    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    main_tag = soup.find('main')
    if isinstance(main_tag, Tag):
        p_tag = main_tag.find('p')
    else:
        p_tag = soup.find('p')

    return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""