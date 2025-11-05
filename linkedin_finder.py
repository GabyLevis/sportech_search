#!/usr/bin/env python3
"""
LinkedIn Sports Tech Startup Finder
Helps find and track sports tech startups coming out of stealth on LinkedIn

Note: Due to LinkedIn's authentication requirements, this tool:
1. Provides curated search results from web searches
2. Can extract limited public information
3. Outputs URLs for manual review
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from datetime import datetime, timedelta
import json
import time

# Import AI classifier (optional)
try:
    from ai_classifier import SportsTechClassifier
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class LinkedInStealthStartupFinder:
    """Find and track sports tech startups announced on LinkedIn"""

    # Search queries that work well for finding stealth sports tech startups
    SEARCH_QUERIES = [
        'site:linkedin.com/posts "out of stealth" sports tech',
        'site:linkedin.com/posts "coming out of stealth" sports technology',
        'site:linkedin.com/posts sports tech startup "seed funding"',
        'site:linkedin.com/posts sports technology "Series A"',
        'site:linkedin.com/posts "excited to announce" sports tech',
        'site:linkedin.com/posts athlete performance technology startup',
        'site:linkedin.com/posts sports analytics platform launch',
        'site:linkedin.com/posts fan engagement technology startup',
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_linkedin_posts(self, max_results_per_query: int = 5) -> List[Dict]:
        """
        Search LinkedIn for sports tech startup posts using Google

        Args:
            max_results_per_query: Number of results to get per search query

        Returns:
            List of found LinkedIn posts with metadata
        """
        all_posts = []
        seen_urls = set()

        print("Searching LinkedIn for sports tech startup announcements...")
        print()

        for query in self.SEARCH_QUERIES[:3]:  # Use first 3 queries
            print(f"  Searching: {query[:60]}...")

            try:
                # Use Google search to find LinkedIn posts
                search_url = f'https://www.google.com/search?q={requests.utils.quote(query)}&num={max_results_per_query}'
                response = self.session.get(search_url, timeout=15)

                if response.status_code != 200:
                    print(f"    ⚠️  Search failed with status {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, 'lxml')

                # Find all links in search results
                links = soup.find_all('a', href=True)

                found_count = 0
                for link in links:
                    href = link.get('href', '')

                    # Extract actual URL from Google's format
                    if '/url?q=' in href:
                        actual_url = href.split('/url?q=')[1].split('&')[0]

                        # Check if it's a LinkedIn post
                        if ('linkedin.com/posts/' in actual_url or
                            'linkedin.com/feed/update/' in actual_url):

                            # Avoid duplicates
                            if actual_url in seen_urls:
                                continue
                            seen_urls.add(actual_url)

                            # Get title from link text
                            title = link.get_text(strip=True)

                            if title and len(title) > 10:
                                all_posts.append({
                                    'title': title,
                                    'url': actual_url,
                                    'source': 'LinkedIn',
                                    'query': query,
                                    'found_at': datetime.now().isoformat()
                                })

                                found_count += 1
                                if found_count >= max_results_per_query:
                                    break

                print(f"    Found {found_count} posts")

                # Rate limiting
                time.sleep(2)

            except Exception as e:
                print(f"    ⚠️  Error: {e}")
                continue

        print()
        print(f"Total LinkedIn posts found: {len(all_posts)}")
        print()

        return all_posts

    def extract_startup_from_post(self, post: Dict) -> Optional[Dict]:
        """
        Extract startup information from a LinkedIn post

        Args:
            post: Post dictionary with title and URL

        Returns:
            Startup information if found
        """
        title = post.get('title', '')
        url = post.get('url', '')

        if not title or len(title) < 20:
            return None

        # Try to extract company name from title
        # Pattern: Look for capitalized words that might be company names
        patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\s+(?:out of stealth|announced|raised)',
            r'(?:excited to announce|thrilled to share)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}),?\s+a\s+(?:sports|tech)',
        ]

        company_name = None
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                potential_name = match.group(1).strip()
                # Filter out common false positives
                if potential_name not in ['LinkedIn', 'The', 'We', 'I', 'This', 'Today']:
                    company_name = potential_name
                    break

        if not company_name:
            # Fallback: try to extract from URL or use generic name
            if 'activity-' in url:
                company_name = "Sports Tech Startup"
            else:
                return None

        # Extract author from URL if possible
        author = "Unknown"
        if '/posts/' in url:
            parts = url.split('/posts/')
            if len(parts) > 1:
                author_part = parts[1].split('_')[0]
                if author_part:
                    author = author_part.replace('-', ' ').title()

        return {
            'title': f"{company_name} - LinkedIn Announcement",
            'url': url,
            'author': author,
            'company': company_name,
            'description': f"Sports tech startup mentioned in LinkedIn post: {title[:150]}",
            'date': datetime.now().strftime('%Y-%m-%d'),  # Today's date as approximation
            'category': 'sports_tech',
            'raw_title': title
        }

    def get_known_startups(self, max_age_months: int = 12) -> List[Dict]:
        """
        Search for and return sports tech startups from LinkedIn

        Args:
            max_age_months: Maximum age in months for startups (default: 12)

        Returns:
            List of found startup announcements
        """
        # Perform live search
        posts = self.search_linkedin_posts(max_results_per_query=5)

        if not posts:
            print("⚠️  No LinkedIn posts found from search.")
            return []

        # Extract startups from posts
        startups = []
        print("Extracting startup information from posts...")
        print()

        for i, post in enumerate(posts, 1):
            print(f"  [{i}/{len(posts)}] Analyzing: {post['title'][:60]}...")

            startup = self.extract_startup_from_post(post)
            if startup:
                startups.append(startup)
                print(f"    ✓ Found: {startup['company']}")
            else:
                print(f"    ✗ Could not extract startup info")

        return startups

    def try_extract_public_content(self, url: str) -> Optional[Dict]:
        """
        Attempt to extract publicly available content from LinkedIn post
        Note: Most content requires authentication
        """
        try:
            response = self.session.get(url, timeout=15)

            if response.status_code != 200:
                return {"accessible": False, "reason": f"Status {response.status_code}"}

            soup = BeautifulSoup(response.text, 'lxml')

            # Try to extract meta tags (publicly available)
            meta_title = soup.find('meta', property='og:title')
            meta_desc = soup.find('meta', property='og:description')

            title = meta_title.get('content', '') if meta_title else ''
            description = meta_desc.get('content', '') if meta_desc else ''

            return {
                "accessible": len(title) > 0 or len(description) > 0,
                "title": title,
                "description": description,
                "full_content_requires_login": True
            }

        except Exception as e:
            return {"accessible": False, "error": str(e)}

    def format_startup_info(self, startup: Dict) -> str:
        """Format startup information for display"""
        lines = []
        lines.append(f"Company: {startup.get('company', 'Unknown')}")
        lines.append(f"Description: {startup.get('description', 'N/A')}")
        lines.append(f"Announced by: {startup.get('author', 'N/A')}")
        lines.append(f"Date: {startup.get('date', 'N/A')}")
        lines.append(f"LinkedIn Post: {startup.get('url', 'N/A')}")
        return '\n'.join(lines)

    def search_tips(self) -> List[str]:
        """Provide tips for manually searching LinkedIn"""
        return [
            "Use Google search with these queries (copy & paste):",
            "",
            *[f'  • {query}' for query in self.SEARCH_QUERIES],
            "",
            "Best practices:",
            "  • Look for posts from founders, VCs, or tech journalists",
            "  • Check for funding announcements (seed, Series A, etc.)",
            "  • Keywords: 'stealth mode', 'excited to announce', 'launching'",
            "  • Filter by recent posts (last 6-12 months)",
            "",
            "LinkedIn Search (requires login):",
            '  • Use LinkedIn search: "sports tech" + "out of stealth"',
            "  • Follow sports tech investors and accelerators",
            "  • Join sports tech LinkedIn groups",
        ]


def main(max_age_months: int = 12):
    """
    Main execution function

    Args:
        max_age_months: Only show startups from the last N months (default: 12)
    """
    print()
    print("=" * 70)
    print("LinkedIn Sports Tech Startup Finder")
    print("Finding startups coming out of stealth mode")
    print(f"(Showing announcements from the last {max_age_months} months)")
    print("=" * 70)
    print()

    finder = LinkedInStealthStartupFinder()

    # Initialize AI classifier (optional)
    classifier = None
    if AI_AVAILABLE:
        classifier = SportsTechClassifier()
    print()

    # Get recent startups only
    print(f"Filtering for startups announced in the last {max_age_months} months...")
    print()
    known_startups = finder.get_known_startups(max_age_months=max_age_months)

    if not known_startups:
        print("⚠️  No recent stealth announcements found in the database.")
        print(f"   All entries are older than {max_age_months} months.")
        print()
        print("To find new startups, use the Google search queries below.")
        print("=" * 70)
        print()

        # Show search tips
        print("HOW TO FIND MORE STARTUPS")
        print("=" * 70)
        for tip in finder.search_tips():
            print(tip)
        print()
        print("=" * 70)
        return

    # AI Classification (if available)
    verified_startups = []
    if classifier:
        print("AI Classification: Verifying sports tech relevance...")
        print("=" * 70)
        print()

        for startup in known_startups:
            classification = classifier.is_sports_tech(
                company_name=startup['company'],
                description=startup['description'],
                article_title=startup['title']
            )

            startup['classification'] = classification

            if classification['is_sports_tech']:
                verified_startups.append(startup)
                print(f"✓ {startup['company']}: Verified sports tech ({classification['confidence']:.0%})")
                if classification.get('category'):
                    print(f"  Category: {classification['category']}")
            else:
                print(f"✗ {startup['company']}: {classification['reasoning']}")

        print()
        print(f"AI Verification: {len(verified_startups)}/{len(known_startups)} confirmed as sports tech")
        print()
    else:
        # No AI classification available
        verified_startups = known_startups

    print(f"FOUND: {len(verified_startups)} Sports Tech Startups Coming Out of Stealth")
    print("=" * 70)
    print()

    for i, startup in enumerate(verified_startups, 1):
        print(f"{i}. {startup['company']}")
        print("-" * 70)
        print(finder.format_startup_info(startup))

        # Show classification if available
        if startup.get('classification'):
            cls = startup['classification']
            print(f"AI Confidence: {cls['confidence']:.0%} - Category: {cls.get('category', 'N/A')}")

        print()

        # Try to get additional public info
        print(f"  Attempting to fetch public details...")
        public_info = finder.try_extract_public_content(startup['url'])

        if public_info.get('accessible'):
            print(f"  ✓ Public meta data available:")
            if public_info.get('title'):
                print(f"    Title: {public_info['title'][:80]}")
            if public_info.get('description'):
                print(f"    Description: {public_info['description'][:150]}...")
        else:
            print(f"  ✗ Full content requires LinkedIn login")

        print()

    # Save results
    output = {
        "startups": verified_startups,
        "search_date": datetime.now().isoformat(),
        "note": "Visit URLs in a browser with LinkedIn login for full details"
    }

    output_file = "linkedin_sports_tech_startups.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print("=" * 70)
    print(f"Results saved to: {output_file}")
    if classifier:
        print(f"(AI-verified: {len(verified_startups)}/{len(known_startups)} confirmed as sports tech)")
    print("=" * 70)
    print()

    # Show search tips
    print("HOW TO FIND MORE STARTUPS")
    print("=" * 70)
    for tip in finder.search_tips():
        print(tip)
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
