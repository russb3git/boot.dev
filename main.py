"""
This module provides functions to crawl a website starting from a base URL,
extracting relevant data from each page, and following links to other pages
within the same domain. The extracted data includes the page heading,
first paragraph, outgoing links, and image URLs.
"""
import sys

from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup, Tag


def normalize_url(url: str) -> str:
    """
    Normalize a URL by parsing it and reconstructing it in a standard format.

    :param url: The URL to be normalized.
    :return: A normalized URL string.
    """

    response = urlparse(url)
    netloc = response.netloc.lower()  # domain
    path = response.path.lower().rstrip('/')  # subdomain

    new_url = f'{netloc}{path}'
    return new_url


def get_heading_from_html(html: str) -> str:
    """
    Extracts the heading from the given HTML content.

    :param html: The HTML content to parse.
    :return: The text of the first <h1> tag found in the HTML, or an empty string if no <h1> tag is present.
    """
    soup = BeautifulSoup(html, 'html.parser')

    h_tag = soup.find('h1')
    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""


def get_first_paragraph_from_html(html: str) -> str:
    """
    Extracts the first paragraph from the given HTML content.
    :param html: The HTML content to parse.
    :return: The text of the first <p> tag found in the <main> tag, or if no <main> tag is present, the first <p> tag in the HTML. Returns an empty string if no <p> tag is found.
    """
    soup = BeautifulSoup(html, 'html.parser')

    main_tag = soup.find('main')
    if isinstance(main_tag, Tag):
        p_tag = main_tag.find('p')
    else:
        p_tag = soup.find('p')

    return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""


def get_urls_from_html(html: str, base_url) -> list[str]:
    """
    Extracts all URLs from the given HTML content and converts them to
    absolute URLs based on the provided base URL.
    :param html: The HTML content to parse.
    :param base_url: The base URL to resolve relative URLs against.
    :return: A list of absolute URLs extracted from the HTML content.
    """
    soup = BeautifulSoup(html, 'html.parser')

    url_list = []

    href_tags = soup.find_all('a')
    for href_tag in href_tags:
        if isinstance(href_tag, Tag):
            href = href_tag.get("href")
            if href:
                absolute_url = urljoin(base_url, href_tag.get('href'))
                url_list.append(absolute_url)

    return url_list


def get_images_from_html(html: str, base_url) -> list[str]:
    """
    Extracts all image URLs from the given HTML content and converts them to
    absolute URLs based on the provided base URL.

    :param html: The HTML content to parse.
    :param base_url: The base URL to resolve relative image URLs against.
    :return: A list of absolute image URLs extracted from the HTML content.
    """

    soup = BeautifulSoup(html, 'html.parser')

    image_list = []

    href_tags = soup.find_all('img')
    for href_tag in href_tags:
        if isinstance(href_tag, Tag):
            img_tag = href_tag.get('src')
            if img_tag:
                absolute_url = urljoin(base_url, img_tag)
                image_list.append(absolute_url)

    return image_list


def extract_page_data(html: str, page_url: str):
    """
    Extracts the heading, first paragraph, URLs, and image URLs from the given
    HTML content.

    :param html: The HTML string to parse.
    :param page_url: The absolute URL of the page to resolve relative URLs
        against.
    :return: A dictionary containing the keys with keys: url, heading,
        first_paragraph, outgoing_links, image_urls.
    """

    heading = get_heading_from_html(html)
    first_paragraph = get_first_paragraph_from_html(html)
    outgoing_links = get_urls_from_html(html, page_url)
    image_urls = get_images_from_html(html, page_url)

    return {'url': page_url,
            'heading': heading,
            'first_paragraph': first_paragraph,
            'outgoing_links': outgoing_links,
            'image_urls': image_urls

            }


def get_html(url):
    """
    Fetches the HTML content of the given URL.
    :param url: The URL to fetch.
    :return: The HTML content as a string if the request is successful,
    otherwise None.
    """

    response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    if response.status_code >= 400:
        raise Exception(f'Error level code {response.status_code}')

    if not response.headers.get('content-type').startswith("text/html"):
        raise Exception(f'Header not text/html:'
                        f' {response.headers.get("content-type")}')

    if response.status_code != 200:
        raise Exception(f'Error level code {response.status_code}')

    return response.text


def crawl_page(base_url: str, current_url: str | None = None,
               page_data: dict | None = None) -> dict | None:
    """
    Crawls a web page starting from the base URL, extracting relevant data and
    following links to other pages.

    :param base_url: The root URL of the website we're crawling.
    :param current_url: The current URL being crawled.
    :param page_data: Stores all the rich data we've extracted from each
        page, keyed by normalized URL. This function should continue to pass the
        same dictionary to itself.
    :return: A dictionary containing the extracted data from all crawled pages,
        keyed by normalized URL.
    """

    current_url = base_url if current_url is None else urljoin(base_url,
                                                               current_url)
    # print(f'This is current_url: {current_url}')

    page_data = {} if page_data is None else page_data
    # print(f'This is page_data: {page_data}')

    if urlparse(current_url).netloc != urlparse(base_url).netloc:
        return None

    normalized_url = normalize_url(current_url)
    # print(f'This is normalized_url: {normalized_url}')

    if normalized_url in page_data.keys():
        return None

    # print(f'This is the base_url argument passed into get_html({
    # current_url})')
    html = get_html(current_url)
    # print(f'This is html: {html}')

    extracted_page_data = extract_page_data(html, normalized_url)
    # print(f'This is extracted page: {extracted_page_data}')

    page_data[normalized_url] = extracted_page_data

    response = get_urls_from_html(html, normalized_url)
    # print(f'This is response: {response}')

    for resp in response:
        # print(f'This is resp: {resp}')
        crawl_page(base_url, resp, page_data)

    return page_data


def main():
    """
    The main function of the web crawler. It checks for command-line arguments,
    initiates the crawling process, and prints the results.
    :return: None
    """
    if len(sys.argv) < 2:
        print('no website provided')
        sys.exit(1)

    if len(sys.argv) > 2:
        print('too many arguments provided')
        sys.exit(1)

    base_url = sys.argv[1]

    print(f'starting crawl of: {base_url}')
    data = crawl_page(base_url)
    # print(f'***** This is the crawled data from main(): {crawl_page(
    # base_url)}')

    if data:
        print(f'The number of pages crawled: {len(data)}')
        for k, v in data.items():
            print(f'{k}: {v['url']}')


if __name__ == "__main__":
    main()
