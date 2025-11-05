# Sports Tech Startup Finder

A platform that finds and tracks sports tech startups from multiple sources including publications and LinkedIn announcements.

## Features

- Scrapes multiple sports/tech industry publications
- **AI-Powered Classification**: Uses LLM (OpenAI GPT) to verify if companies are truly sports tech
- Identifies articles about sports tech startups using pattern matching
- Extracts startup information and generates contextual summaries
- Extensible architecture to easily add more publication sources
- Filters out false positives using intelligent validation
- Fallback keyword-based classification when AI is unavailable

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Enable AI Classification:
```bash
# Add your OpenAI API key to .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

3. Run the scrapers:

**Publication Scraper** (TechCrunch, Sportico):
```bash
python scraper.py
```

**LinkedIn Stealth Startup Finder** (Sports tech coming out of stealth):
```bash
python linkedin_finder.py
```

**Test AI Classifier** (optional):
```bash
python ai_classifier.py
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

## AI-Powered Sports Tech Classification

The platform includes an optional AI classifier that uses OpenAI's GPT models to accurately determine if a company is sports tech related.

### How It Works:

1. **Intelligent Analysis**: Uses GPT-4o-mini to analyze company name, description, and context
2. **Accurate Classification**: Provides confidence scores (0-100%) and specific categories
3. **Sports Tech Categories**:
   - Athlete performance tracking/analytics
   - Sports data and analytics platforms
   - Fan engagement technology
   - Sports betting/gambling technology
   - Fitness and wellness tech
   - Sports team management software
   - Wearables for sports/athletics
   - eSports technology

4. **Fallback Mode**: When API key is not available, uses keyword-based classification

### Example Output:

```
AI Classification: Verifying sports tech relevance...
======================================================================

✓ Sports Visio, Inc.: Verified sports tech (90% confidence)
  Category: sports_analytics
✗ Amazon: Not sports tech - General tech company
```

### Benefits:

- **Filters false positives**: Removes companies that aren't truly sports tech (like IAC, Amazon)
- **Improves accuracy**: Better than keyword matching alone
- **Categorizes results**: Identifies specific sports tech sub-categories
- **Optional**: Works with or without API key (fallback to keywords)

## Future Improvements

- Add RSS feed support for more reliable article discovery
- Integrate with NewsAPI or similar services
- Add more sports tech-specific publications
- Support for Claude API as alternative to OpenAI
- Add search functionality to target specific sports/technologies
- Create a web interface for easier interaction
- Add scheduled scraping with email notifications

## LinkedIn Stealth Startup Finder

**Special feature**: Find sports tech startups coming out of stealth mode on LinkedIn.

### What It Does:
- Tracks sports tech startups announcing their exit from stealth mode
- Provides curated list of found startups with LinkedIn post URLs
- Extracts publicly available metadata without requiring login
- Includes search tips for finding more startups manually

### Currently Found Startups (Last 12 Months):
1. **Omnisent Sports** - Real-time sentiment intelligence and sports analytics platform (March 2025)

### Output Files:
- `linkedin_sports_tech_startups.json` - Structured data with startup details

### Date Filtering:
- **Automatic**: Only shows startups from the last 12 months
- **Configurable**: Adjust the time window if needed
- **Example**: Sports from 2021 are automatically filtered out

### Limitations:
- Full LinkedIn post content requires authentication
- Currently provides curated results from web search
- Requires manual updates to add new startups to the database
- Best used as a starting point for manual investigation

### Finding More Startups:
The tool provides Google search queries you can use:
- `site:linkedin.com/posts "out of stealth" sports tech`
- `site:linkedin.com/posts sports tech startup "seed funding"`
- And more...

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
