import unittest
from crawl import normalize_url

class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        self.assertEqual(normalize_url('https://www.boot.dev/blog/path'), 'www.boot.dev/blog/path')
    def test_normalize_url_with_slash(self):
        # The runner automatically finds and runs this too!
        self.assertEqual(normalize_url("https://example.com/path/"), "example.com/path")
    def test_normalize_url_without_slash(self):
        self.assertEqual(normalize_url("http://example.com"), "example.com")

if __name__ == '__main__':
    unittest.main()
