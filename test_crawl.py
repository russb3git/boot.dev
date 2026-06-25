import unittest
from web_scraper import get_urls_from_html, get_first_paragraph_from_html, \
    get_heading_from_html, get_images_from_html, normalize_url, \
    extract_page_data


class TestCrawl(unittest.TestCase):

    def test_normalize_url(self):
        self.assertEqual(normalize_url('https://www.boot.dev/blog/path'),
                         'www.boot.dev/blog/path')

    def test_normalize_url_with_slash(self):
        self.assertEqual(normalize_url("https://example.com/path/"),
                         "example.com/path")

    def test_normalize_url_without_slash(self):
        self.assertEqual(normalize_url("http://example.com"), "example.com")

    def test_normalize_url_with_slashes(self):
        self.assertEqual(normalize_url("http://example.com/path//"),
                         "example.com/path")

    def test_get_heading_from_html_basic(self):
        input_body = '<html><body><h1>Test Title</h1></body></html>'
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_blank(self):
        input_body = ''
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_invalid(self):
        input_body = '<html><body><h1></h1></body></html>'
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = '''<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_invalid(self) -> None:
        input_body = '<html><body><p></p></body></html>'
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_urls_from_html(self):
        self.assertEqual(get_urls_from_html(
                '<html><body><a '
                'href="https://crawler-test.com"><span>Boot.dev</span></a'
                '></body></html>',
                "https://crawler-test.com"), ["https://crawler-test.com"])

    def test_get_urls_from_html_with_blank_url(self):
        self.assertEqual(get_urls_from_html(
                '<html></html>', "https://crawler-test.com"),
                [])

    def test_get_urls_from_html_absolute_and_relative_url(self):
        input_url = "https://crawler-test.com"
        input_body = ('<html><body><a href="https://example.com">Example</a><a '
                      'href="/about">About</a></body></html>')
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://example.com", "https://crawler-test.com/about"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = ('<html><body><img src="/logo.png" '
                      'alt="Logo"></body></html>')
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute_and_relative_url(self):
        input_url = "https://crawler-test.com"
        input_body = ('<html><body><img src="https://example.com/image.jpg" '
                      'alt="Example Image"><img src="/logo.png" '
                      'alt="Logo"></body></html>')
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://example.com/image.jpg",
                    "https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_blank_html(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = '''<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"]
            }
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
