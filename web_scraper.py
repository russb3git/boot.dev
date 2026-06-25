"""
This module provides functions to crawl a website starting from a base URL,
extracting relevant data from each page, and following links to other pages
within the same domain. The extracted data includes the page heading,
first paragraph, outgoing links, and image URLs.
"""
import asyncio
import sys
import json
from urllib.parse import urlparse, urljoin

import aiohttp
from bs4 import BeautifulSoup, Tag


class AsyncCrawler:
    """
    A class to crawl a website asynchronously, starting from a base URL,
    extracting relevant data from each page, and following links to other
    pages within the same domain.
    """

    def __init__(self, base_url: str, max_concurrency: int, max_pages: int):
        """
        Initializes the AsyncCrawler with a base URL.

        Args:
            base_url (str): The root URL of the website to crawl.
            max_concurrency (int): The maximum number of concurrent
            max_pages (int): The maximum number of pages to crawl.
        """
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.page_data = {}
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = None
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        """
        Adds a page visit to the page_data dictionary if the normalized URL
        is not already present.

        :param normalized_url: The normalized URL of the page to add.
        :return: True if the page was added, False if it was already present.
        """

        async with self.lock:

            if self.should_stop:
                return False

            real_page_count = sum(
                    1 for v in self.page_data.values() if isinstance(v, dict))
            if real_page_count >= self.max_pages:
                self.should_stop = True
                print('Reached maximum number of pages to crawl')
                for task in self.all_tasks:
                    task.cancel()
                return False

            if normalized_url in self.page_data.keys():
                return False
            else:
                self.page_data[normalized_url] = True
                return True

    async def get_html(self, url):
        """
        Fetches the HTML content of the given URL.
        :param url: The URL to fetch.
        :return: The HTML content as a string if the request is successful,
        otherwise None.
        """

        async with self.session.get(url) as response:
            if response.status >= 400:
                print(f'Error level code {response.status}')
                return None

            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type.lower():
                print(f'Header not text/html:'
                      f' {response.headers.get("content-type")}')
                return None

            if response.status != 200:
                print(f'Error level code {response.status}')
                return None

            return await response.text()

    async def crawl_page(self, current_url: str | None = None) -> dict | None:
        """
        Crawls a web page starting from the base URL, extracting relevant
        data and
        following links to other pages.

        :param current_url: The current URL being crawled.
        :return: A dictionary containing the extracted data from all crawled
            pages, keyed by normalized URL.
        """

        if self.should_stop:
            return None

        task = asyncio.current_task()
        self.all_tasks.add(task)

        try:
            current_url = self.base_url if current_url is None else urljoin(
                    self.base_url, current_url)

            if urlparse(current_url).netloc != urlparse(self.base_url).netloc:
                return None

            normalized_url = normalize_url(current_url)

            if not await self.add_page_visit(normalized_url):
                return None

            tasks = []

            async with self.semaphore:
                html = await self.get_html(current_url)

                extracted_page_data = extract_page_data(html, normalized_url)

                async with self.lock:
                    self.page_data[normalized_url] = extracted_page_data

                response = get_urls_from_html(html, normalized_url)

            for resp in response:
                new_task = asyncio.create_task(self.crawl_page(resp))
                tasks.append(new_task)
                self.all_tasks.add(new_task)
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            finally:
                for t in tasks:
                    self.all_tasks.discard(t)

        finally:
            self.all_tasks.discard(task)

        return self.page_data

    async def crawl(self) -> dict:
        """
        Starts the crawling process from the base URL and returns the extracted
        data from the base URL pages.
        
        :return: A dictionary containing the extracted data from all crawled
        pages, keyed by normalized URL.
        """

        try:
            await self.crawl_page(self.base_url)
        except asyncio.CancelledError:
            print('Crawling was cancelled.')
        return self.page_data


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
    :return: The text of the first <h1> tag found in the HTML, or an empty
    string if no <h1> tag is present.
    """
    soup = BeautifulSoup(html, 'html.parser')

    h_tag = soup.find('h1')
    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""


def get_first_paragraph_from_html(html: str) -> str:
    """
    Extracts the first paragraph from the given HTML content.
    :param html: The HTML content to parse.
    :return: The text of the first <p> tag found in the <main> tag, or if no
    <main> tag is present, the first <p> tag in the HTML. Returns an empty
    string if no <p> tag is found.
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


async def crawl_site_async(base_url: str, max_concurrency: int,
                           max_pages: int) -> dict:

    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        data = await crawler.crawl()

        return data


def write_json_report(page_data, filename=r"./report.json"):
    """
    Writes the given page data to a JSON file.
    
    :param page_data: A dictionary containing the keys with keys: url, heading,
        first_paragraph, outgoing_links, image_urls. 
    :param filename: The name of the file to write to. 
    :return: None
    """

    real_page_data = dict(
            (k, v) for k, v in page_data.items() if isinstance(v, dict))

    sorted_data = sorted(real_page_data.values(), key=lambda p: p["url"])

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, indent=2)


async def main():
    """
    The main function of the web crawler. It checks for command-line arguments,
    initiates the crawling process, and prints the results.
    :return: None
    """

    if len(sys.argv) < 4:
        print('too few arguments provided')
        sys.exit(1)

    if len(sys.argv) > 4:
        print('too many arguments provided')
        sys.exit(1)

    base_url = sys.argv[1]
    max_concurrency = int(sys.argv[2])
    max_pages = int(sys.argv[3])

    print(f'starting crawl of: {base_url} with max concurrency: '
          f'{max_concurrency} max pages: {max_pages}')

    page_data = await crawl_site_async(base_url, max_concurrency, max_pages)
    # print(f'***** This is the crawled data from main(): {crawl_page(
    # base_url)}')

    write_json_report(page_data)


if __name__ == "__main__":
    asyncio.run(main())
