import unittest
from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html

class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        self.assertEqual(normalize_url('https://www.boot.dev/blog/path'), 'www.boot.dev/blog/path')
    def test_normalize_url_with_slash(self):
        self.assertEqual(normalize_url("https://example.com/path/"), "example.com/path")
    def test_normalize_url_without_slash(self):
        self.assertEqual(normalize_url("http://example.com"), "example.com")
    def test_normalize_url_with_slashes(self):
        self.assertEqual(normalize_url("http://example.com/path//"), "example.com/path")

    def test_get_heading_from_html_basic(self):
        input_body = '<html><body><h1>Test Title</h1></body></html>'
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
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

if __name__ == '__main__':
    unittest.main()
