# boot.dev web crawler

Simple learning project for crawling a site, extracting page data, and saving a JSON report.

## Scripts

- `web_scraper.py`: Async crawler script. It crawls pages on the same domain and collects:
  - page URL
  - heading (`h1`)
  - first paragraph
  - outgoing links
  - image URLs

Run it with:

```bash
python web_scraper.py https://example.com 10 50
```

This writes `report.json` in the project root.

## Tests

- `test_crawl.py`: Unit tests for URL normalization and HTML extraction helpers.

Run tests with:

```bash
pytest test_crawl.py
```
