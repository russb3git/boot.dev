from urllib.parse import urlparse


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
