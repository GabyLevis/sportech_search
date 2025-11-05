# Sports Tech Startup Scraper

A platform that searches sports industry magazines for articles about new sports tech startups and provides summaries.

## Features

- Scrapes multiple sports/tech industry publications
- Identifies articles about sports tech startups using pattern matching
- Extracts startup information and generates contextual summaries
- Extensible architecture to easily add more publication sources
- Filters out false positives using intelligent validation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the scraper:
```bash
python scraper.py
```

## Supported Publications

- **TechCrunch Sports** (techcrunch.com/category/sports/)
- **Sportico** (sportico.com/business/)

## Output

The scraper returns a list of startups with:
- Startup name
- Brief contextual summary extracted from the article
- Source article URL and title
- Publication name and date (when available)
- Results saved to `startups_found.json`

## How It Works

1. **Article Discovery**: Scrapes publication websites for recent articles
2. **Relevance Filtering**: Identifies tech/startup-related articles using keyword matching
3. **Content Extraction**: Fetches full article text
4. **Startup Identification**: Uses regex patterns to find company mentions:
   - "Startup X raised $..."
   - "X, a sports tech company..."
   - "Parent company X..."
5. **False Positive Filtering**: Removes common words and non-company names
6. **Summary Generation**: Extracts relevant sentences mentioning each startup

## Limitations & Notes

- **Source Dependency**: Results depend on current article availability. Sports tech startup coverage varies by publication.
- **Pattern Matching**: Uses regex-based extraction, which may miss unconventionally-formatted mentions or produce occasional false positives.
- **Access**: Some sports publications block web scrapers (e.g., Sports Business Journal, SportTechie return 403 errors).
- **Best Results**: Works best with tech-focused publications that regularly cover startup funding and launches.

## Future Improvements

- Add RSS feed support for more reliable article discovery
- Integrate with NewsAPI or similar services
- Add more sports tech-specific publications
- Implement AI-powered entity extraction (using OpenAI/Claude APIs)
- Add search functionality to target specific sports/technologies
- Create a web interface for easier interaction
- Add scheduled scraping with email notifications

## Adding New Sources

To add a new publication, create a new scraper class:

```python
class NewPublicationScraper(BaseScraper):
    BASE_URL = "https://example.com"

    def search_articles(self, max_articles: int = 10) -> List[Dict]:
        # Implement article discovery logic
        pass

    def extract_article_content(self, url: str) -> Optional[Dict]:
        # Implement content extraction logic
        pass
```

Then add it to the `scrapers` list in `main()`.
