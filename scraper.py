#!/usr/bin/env python3
"""
Sports Tech Startup Scraper
Searches sports industry publications for articles about new sports tech startups
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from datetime import datetime
import json


class SportsBizJournalScraper:
    """Scraper for Sports Business Journal"""

    BASE_URL = "https://www.sportsbusinessjournal.com"
    SEARCH_KEYWORDS = [
        "startup", "technology", "tech", "innovation",
        "funding", "venture capital", "seed round", "Series A"
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_articles(self, keywords: List[str] = None, max_pages: int = 3) -> List[Dict]:
        """
        Search for articles related to sports tech startups

        Args:
            keywords: List of keywords to search for
            max_pages: Maximum number of pages to scrape

        Returns:
            List of article dictionaries with title, url, summary, date
        """
        if keywords is None:
            keywords = self.SEARCH_KEYWORDS

        articles = []

        # Try searching for tech/startup related articles
        search_terms = ["sports tech startup", "sports technology", "sports innovation funding"]

        for term in search_terms[:max_pages]:
            try:
                search_url = f"{self.BASE_URL}/Articles"
                print(f"Searching for: {term}")

                # For demo purposes, we'll scrape recent articles from main sections
                section_urls = [
                    f"{self.BASE_URL}/Articles/Technology",
                    f"{self.BASE_URL}/Daily/Issues",
                ]

                for url in section_urls:
                    try:
                        response = self.session.get(url, timeout=10)
                        if response.status_code == 200:
                            found_articles = self._parse_article_listing(response.text, url)
                            articles.extend(found_articles)
                    except Exception as e:
                        print(f"Error fetching {url}: {e}")
                        continue

            except Exception as e:
                print(f"Error searching for '{term}': {e}")
                continue

        # Remove duplicates by URL
        unique_articles = {article['url']: article for article in articles}
        return list(unique_articles.values())

    def _parse_article_listing(self, html: str, source_url: str) -> List[Dict]:
        """Parse article listing page and extract article information"""
        soup = BeautifulSoup(html, 'lxml')
        articles = []

        # Look for article links - adjust selectors based on actual site structure
        article_links = soup.find_all('a', href=True)

        for link in article_links:
            href = link.get('href', '')

            # Filter for article URLs
            if '/Article/' in href or '/Daily/' in href:
                title = link.get_text(strip=True)

                if not title or len(title) < 10:
                    continue

                # Make URL absolute
                full_url = href if href.startswith('http') else f"{self.BASE_URL}{href}"

                # Check if title suggests tech/startup content
                if self._is_tech_startup_related(title):
                    articles.append({
                        'title': title,
                        'url': full_url,
                        'source': 'Sports Business Journal',
                        'found_via': source_url,
                        'scraped_at': datetime.now().isoformat()
                    })

        return articles

    def _is_tech_startup_related(self, text: str) -> bool:
        """Check if text is related to tech startups"""
        text_lower = text.lower()

        tech_keywords = [
            'startup', 'technology', 'tech', 'innovation', 'app',
            'platform', 'software', 'digital', 'ai', 'artificial intelligence',
            'funding', 'venture', 'investment', 'raises', 'seed',
            'series a', 'series b', 'analytics', 'data', 'wearable'
        ]

        return any(keyword in text_lower for keyword in tech_keywords)

    def extract_article_content(self, url: str) -> Optional[Dict]:
        """
        Fetch and extract full article content

        Args:
            url: Article URL

        Returns:
            Dictionary with article details including full text
        """
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'lxml')

            # Extract article content - adjust selectors based on actual site
            article_body = soup.find('article') or soup.find('div', class_=re.compile('article|content'))

            content = ""
            if article_body:
                # Get all paragraphs
                paragraphs = article_body.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])

            # Extract date if available
            date_elem = soup.find('time') or soup.find(class_=re.compile('date|time'))
            date = date_elem.get_text(strip=True) if date_elem else None

            return {
                'url': url,
                'content': content,
                'date': date
            }

        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return None


class StartupExtractor:
    """Extract startup information from article content"""

    def extract_startups(self, article: Dict) -> List[Dict]:
        """
        Extract startup information from article content

        Args:
            article: Article dictionary with content

        Returns:
            List of startups found in the article
        """
        content = article.get('content', '')
        if not content:
            return []

        startups = []

        # Look for patterns that indicate startup names
        # Pattern: Company names often appear with indicators like "startup X", "X raised", "X announced"
        patterns = [
            r'startup\s+([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+)?)',
            r'([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+)?)\s+raised',
            r'([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+)?)\s+announced',
            r'([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+)?)\s+launched',
            r'company\s+([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+)?)',
        ]

        found_names = set()

        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                company_name = match.group(1).strip()
                if len(company_name) > 2 and company_name not in found_names:
                    found_names.add(company_name)

                    # Extract context around the company name
                    start = max(0, match.start() - 200)
                    end = min(len(content), match.end() + 200)
                    context = content[start:end]

                    startups.append({
                        'name': company_name,
                        'context': context,
                        'source_url': article.get('url'),
                        'source_title': article.get('title'),
                        'date': article.get('date')
                    })

        return startups

    def generate_summary(self, startup: Dict) -> str:
        """
        Generate a summary for a startup based on extracted context

        Args:
            startup: Startup dictionary with context

        Returns:
            Summary string
        """
        context = startup.get('context', '')
        name = startup.get('name', 'This company')

        # Simple extractive summary - find key sentences
        sentences = re.split(r'[.!?]+', context)

        # Filter sentences that mention the startup
        relevant_sentences = [
            s.strip() for s in sentences
            if name.lower() in s.lower() and len(s.strip()) > 20
        ]

        if relevant_sentences:
            summary = '. '.join(relevant_sentences[:2]) + '.'
        else:
            summary = f"Mentioned in article about sports technology and innovation."

        return summary


def main():
    """Main execution function"""
    print("=" * 60)
    print("Sports Tech Startup Scraper")
    print("=" * 60)
    print()

    # Initialize scraper
    scraper = SportsBizJournalScraper()
    extractor = StartupExtractor()

    print("Searching Sports Business Journal for tech startup articles...")
    print()

    # Search for articles
    articles = scraper.search_articles(max_pages=2)

    print(f"Found {len(articles)} potentially relevant articles")
    print()

    all_startups = []

    # Process each article
    for i, article in enumerate(articles[:10], 1):  # Limit to first 10 for demo
        print(f"[{i}/{min(len(articles), 10)}] Processing: {article['title'][:60]}...")

        # Get full article content
        full_article = scraper.extract_article_content(article['url'])

        if full_article:
            article.update(full_article)

            # Extract startups from article
            startups = extractor.extract_startups(article)

            if startups:
                print(f"  → Found {len(startups)} startup(s)")
                all_startups.extend(startups)
            else:
                print(f"  → No startups identified")
        else:
            print(f"  → Could not extract content")

        print()

    # Display results
    print("=" * 60)
    print(f"RESULTS: Found {len(all_startups)} startups")
    print("=" * 60)
    print()

    for i, startup in enumerate(all_startups, 1):
        summary = extractor.generate_summary(startup)

        print(f"{i}. {startup['name']}")
        print(f"   Summary: {summary}")
        print(f"   Source: {startup.get('source_title', 'N/A')}")
        print(f"   URL: {startup['source_url']}")
        if startup.get('date'):
            print(f"   Date: {startup['date']}")
        print()

    # Save results to JSON
    output_file = 'startups_found.json'
    with open(output_file, 'w') as f:
        json.dump(all_startups, f, indent=2)

    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()
