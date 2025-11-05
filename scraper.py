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
from abc import ABC, abstractmethod

# Import AI classifier (optional)
try:
    from ai_classifier import SportsTechClassifier
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class BaseScraper(ABC):
    """Base class for publication scrapers"""

    TECH_KEYWORDS = [
        'startup', 'technology', 'tech', 'innovation', 'app',
        'platform', 'software', 'digital', 'ai', 'artificial intelligence',
        'funding', 'venture', 'investment', 'raises', 'seed',
        'series a', 'series b', 'analytics', 'data', 'wearable',
        'vc', 'fundraising', 'round'
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    @abstractmethod
    def search_articles(self, max_articles: int = 10) -> List[Dict]:
        """Search for articles related to sports tech startups"""
        pass

    @abstractmethod
    def extract_article_content(self, url: str) -> Optional[Dict]:
        """Extract full article content"""
        pass

    def _is_tech_startup_related(self, text: str) -> bool:
        """Check if text is related to tech startups"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.TECH_KEYWORDS)


class TechCrunchScraper(BaseScraper):
    """Scraper for TechCrunch sports category"""

    BASE_URL = "https://techcrunch.com"
    SPORTS_URL = "https://techcrunch.com/category/sports/"

    def search_articles(self, max_articles: int = 10) -> List[Dict]:
        """Search TechCrunch sports category for articles"""
        articles = []

        try:
            print(f"Fetching articles from TechCrunch sports category...")
            response = self.session.get(self.SPORTS_URL, timeout=15)

            if response.status_code != 200:
                print(f"  Error: Got status code {response.status_code}")
                return articles

            soup = BeautifulSoup(response.text, 'lxml')

            # TechCrunch uses specific article containers
            # Look for article links
            article_elements = soup.find_all('h2', class_=re.compile('post-block__title|wp-block-post-title'))

            if not article_elements:
                # Fallback: look for any links that might be articles
                article_elements = soup.find_all('a', href=re.compile(r'/\d{4}/\d{2}/\d{2}/'))

            for elem in article_elements[:max_articles]:
                try:
                    # Get the link
                    link = elem.find('a') if elem.name != 'a' else elem
                    if not link:
                        continue

                    url = link.get('href', '')
                    title = link.get_text(strip=True) or elem.get_text(strip=True)

                    if not url or not title or len(title) < 10:
                        continue

                    # Make URL absolute
                    if not url.startswith('http'):
                        url = self.BASE_URL + url

                    # Check if it's tech/startup related
                    if self._is_tech_startup_related(title):
                        articles.append({
                            'title': title,
                            'url': url,
                            'source': 'TechCrunch',
                            'scraped_at': datetime.now().isoformat()
                        })

                except Exception as e:
                    continue

            print(f"  Found {len(articles)} relevant articles")

        except Exception as e:
            print(f"  Error fetching TechCrunch: {e}")

        return articles

    def extract_article_content(self, url: str) -> Optional[Dict]:
        """Extract content from TechCrunch article"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'lxml')

            # Extract article content
            article_body = soup.find('article') or soup.find('div', class_=re.compile('article-content|entry-content'))

            content = ""
            if article_body:
                paragraphs = article_body.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])

            # Extract date
            date_elem = soup.find('time')
            date = date_elem.get('datetime', date_elem.get_text(strip=True)) if date_elem else None

            return {
                'url': url,
                'content': content,
                'date': date
            }

        except Exception as e:
            print(f"    Error extracting content: {e}")
            return None


class SporticoScraper(BaseScraper):
    """Scraper for Sportico"""

    BASE_URL = "https://www.sportico.com"
    BUSINESS_URL = "https://www.sportico.com/business/"

    def search_articles(self, max_articles: int = 10) -> List[Dict]:
        """Search Sportico for business/tech articles"""
        articles = []

        try:
            print(f"Fetching articles from Sportico business section...")
            response = self.session.get(self.BUSINESS_URL, timeout=15)

            if response.status_code != 200:
                print(f"  Error: Got status code {response.status_code}")
                return articles

            soup = BeautifulSoup(response.text, 'lxml')

            # Look for article links
            article_links = soup.find_all('a', href=re.compile(r'/\d{4}/\d{2}/'))

            seen_urls = set()

            for link in article_links:
                if len(articles) >= max_articles:
                    break

                try:
                    url = link.get('href', '')
                    title = link.get_text(strip=True)

                    if not url or not title or len(title) < 10:
                        continue

                    # Make URL absolute
                    if not url.startswith('http'):
                        url = self.BASE_URL + url

                    # Avoid duplicates
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    # Check if it's tech/startup related
                    if self._is_tech_startup_related(title):
                        articles.append({
                            'title': title,
                            'url': url,
                            'source': 'Sportico',
                            'scraped_at': datetime.now().isoformat()
                        })

                except Exception as e:
                    continue

            print(f"  Found {len(articles)} relevant articles")

        except Exception as e:
            print(f"  Error fetching Sportico: {e}")

        return articles

    def extract_article_content(self, url: str) -> Optional[Dict]:
        """Extract content from Sportico article"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'lxml')

            # Extract article content
            article_body = soup.find('article') or soup.find('div', class_=re.compile('article-body|entry-content|post-content'))

            content = ""
            if article_body:
                paragraphs = article_body.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])

            # Extract date
            date_elem = soup.find('time') or soup.find(class_=re.compile('date|published'))
            date = date_elem.get_text(strip=True) if date_elem else None

            return {
                'url': url,
                'content': content,
                'date': date
            }

        except Exception as e:
            print(f"    Error extracting content: {e}")
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
        if not content or len(content) < 100:
            return []

        startups = []

        # Balanced patterns to find startup names
        # Focus on high-confidence patterns with some flexibility
        patterns = [
            # "Startup X" or "startup called X" (most reliable)
            r'startup\s+(?:called\s+)?([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+){0,2})',
            # "X raised $" or "X raises $"
            r'\b([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+){0,2})\s+(?:raised|raises|raising)\s+\$',
            # "X, a [type] startup/company/platform" (very specific)
            r'\b([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+){0,2}),\s+a(?:n)?\s+(?:\w+\s+)?(?:startup|company|platform|app|firm)\s+(?:that|which|based|founded)',
            # "X announced" (when followed by funding keywords)
            r'\b([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+){0,2})\s+announced.*?(?:\$\d+|funding|seed|series\s+[A-Z])',
            # "X secured" or "X closed" (funding context)
            r'\b([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+){0,2})\s+(?:secured|closed|completed)\s+(?:a|an|its)?\s*\$',
            # Company names with explicit descriptors
            r'(?:company|platform|app)\s+(?:called\s+)?([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+){0,2})',
            # Parent company mentions (reliable)
            r'parent\s+company\s+([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+){0,2})',
        ]

        found_names = set()

        # Common false positives to filter out
        false_positives = {
            'The', 'This', 'That', 'These', 'Those', 'They', 'It', 'We', 'He', 'She',
            'According', 'Sports', 'Tech', 'New', 'York', 'Los', 'Angeles', 'San', 'Francisco',
            'NBA', 'NFL', 'MLB', 'NHL', 'MLS', 'USA', 'EU', 'UK', 'US', 'Initially',
            'Store', 'App', 'Some', 'Many', 'Most', 'All', 'Both', 'Few', 'Several',
            'While', 'When', 'Where', 'What', 'Which', 'Who', 'How', 'Why',
            'Before', 'After', 'During', 'Since', 'Until', 'Although', 'However',
            'Therefore', 'Furthermore', 'Moreover', 'Additionally', 'Consequently'
        }

        # Common verbs/words that shouldn't be company names
        verb_words = {'is', 'are', 'was', 'were', 'has', 'have', 'had', 'did', 'does', 'do',
                     'said', 'says', 'told', 'tells', 'asked', 'asks', 'reported', 'reports',
                     'suggested', 'suggests', 'provided', 'provides', 'expects', 'expect',
                     'didn', 'wasn', 'hasn', 'haven', 'couldn', 'wouldn', 'shouldn',
                     'ecosystem', 'battlefield', 'landscape', 'industry', 'market', 'sector'}

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                company_name = match.group(1).strip()

                # Filter out short names and false positives
                if len(company_name) < 3:
                    continue

                # Check against false positives (case-insensitive)
                if company_name in false_positives or company_name.lower() in verb_words:
                    continue

                # Filter multi-word matches that start with common words
                first_word = company_name.split()[0].lower()
                if first_word in {'is', 'are', 'was', 'were', 'has', 'have', 'that', 'which', 'from', 'for', 'and', 'the'}:
                    continue

                # Skip if already found
                if company_name in found_names:
                    continue

                # Additional validation: company name should have at least one capital letter
                # and shouldn't be all lowercase after the first word
                words = company_name.split()
                if len(words) > 1 and not any(w[0].isupper() for w in words[1:] if len(w) > 0):
                    continue

                found_names.add(company_name)

                # Extract context around the company name (400 chars on each side)
                start = max(0, match.start() - 400)
                end = min(len(content), match.end() + 400)
                context = content[start:end]

                startups.append({
                    'name': company_name,
                    'context': context,
                    'source_url': article.get('url'),
                    'source_title': article.get('title'),
                    'source': article.get('source'),
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

        # Filter sentences that mention the startup and have meaningful content
        relevant_sentences = []
        for s in sentences:
            s = s.strip()
            # Check if sentence mentions the company and has decent length
            if name in s and len(s) > 30 and len(s) < 300:
                relevant_sentences.append(s)

        if relevant_sentences:
            # Take the 2 most relevant sentences
            summary = '. '.join(relevant_sentences[:2])
            if not summary.endswith('.'):
                summary += '.'
        else:
            summary = f"Sports tech company mentioned in article about innovation and technology in sports."

        return summary


def main():
    """Main execution function"""
    print("=" * 70)
    print("Sports Tech Startup Scraper")
    print("=" * 70)
    print()

    # Initialize scrapers
    scrapers = [
        TechCrunchScraper(),
        SporticoScraper(),
    ]

    extractor = StartupExtractor()

    # Initialize AI classifier (optional)
    classifier = None
    if AI_AVAILABLE:
        classifier = SportsTechClassifier()
    print()

    print("Searching multiple sources for sports tech startup articles...")
    print()

    all_articles = []

    # Collect articles from all sources
    for scraper in scrapers:
        articles = scraper.search_articles(max_articles=10)
        all_articles.extend(articles)

    print()
    print(f"Total articles found: {len(all_articles)}")
    print()

    all_startups = []

    # Process each article
    for i, article in enumerate(all_articles, 1):
        title_preview = article['title'][:70] + "..." if len(article['title']) > 70 else article['title']
        print(f"[{i}/{len(all_articles)}] {article['source']}: {title_preview}")

        # Get full article content
        # Find the appropriate scraper for this source
        scraper = next((s for s in scrapers if article['source'] in str(type(s).__name__)), scrapers[0])

        full_article = scraper.extract_article_content(article['url'])

        if full_article:
            article.update(full_article)

            # Extract startups from article
            startups = extractor.extract_startups(article)

            if startups:
                print(f"  → Found {len(startups)} startup(s): {', '.join([s['name'] for s in startups])}")
                all_startups.extend(startups)
            else:
                print(f"  → No startups identified")
        else:
            print(f"  → Could not extract content")

        print()

    # AI Classification (if available)
    sports_tech_startups = []
    if classifier and all_startups:
        print("=" * 70)
        print("AI Classification: Verifying sports tech relevance...")
        print("=" * 70)
        print()

        for startup in all_startups:
            classification = classifier.is_sports_tech(
                company_name=startup.get('name', ''),
                description=startup.get('context', ''),
                article_title=startup.get('source_title', '')
            )

            startup['classification'] = classification

            if classification['is_sports_tech']:
                sports_tech_startups.append(startup)
                print(f"✓ {startup['name']}: Sports Tech ({classification['confidence']:.0%} confidence)")
                if classification.get('category'):
                    print(f"  Category: {classification['category']}")
            else:
                print(f"✗ {startup['name']}: Not sports tech - {classification['reasoning']}")

        print()
        print(f"Filtered: {len(sports_tech_startups)}/{len(all_startups)} are sports tech")
        print()
    else:
        # No AI classification, use all startups
        sports_tech_startups = all_startups

    # Display results
    print("=" * 70)
    print(f"RESULTS: Found {len(sports_tech_startups)} sports tech startups from {len(all_articles)} articles")
    print("=" * 70)
    print()

    if sports_tech_startups:
        for i, startup in enumerate(sports_tech_startups, 1):
            summary = extractor.generate_summary(startup)

            print(f"{i}. {startup['name']}")

            # Show classification info if available
            if startup.get('classification'):
                cls = startup['classification']
                print(f"   Classification: {cls['confidence']:.0%} confidence - {cls.get('category', 'N/A')}")

            print(f"   Source: {startup.get('source', 'N/A')} - {startup.get('source_title', 'N/A')[:60]}")
            print(f"   Summary: {summary[:200]}...")
            print(f"   URL: {startup['source_url']}")
            if startup.get('date'):
                print(f"   Date: {startup['date']}")
            print()
    else:
        print("No startups were identified in the articles found.")
        print("This could mean:")
        print("  - The articles didn't contain startup mentions")
        print("  - The extraction patterns need refinement")
        print("  - Try running again or checking different sources")

    # Save results to JSON
    output_file = 'startups_found.json'
    with open(output_file, 'w') as f:
        json.dump(sports_tech_startups, f, indent=2)

    print()
    print(f"Full results saved to {output_file}")
    if classifier:
        print(f"(AI-filtered: {len(sports_tech_startups)}/{len(all_startups)} verified as sports tech)")


if __name__ == "__main__":
    main()
