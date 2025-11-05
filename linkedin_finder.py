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

# Import AI classifier (optional)
try:
    from ai_classifier import SportsTechClassifier
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class LinkedInStealthStartupFinder:
    """Find and track sports tech startups announced on LinkedIn"""

    # Curated LinkedIn posts found via search
    # These are real posts about sports tech startups coming out of stealth
    # NOTE: Filter is set to last 12 months - add recent announcements
    KNOWN_POSTS = [
        {
            "title": "Omnisent Sports - Out of stealth",
            "url": "https://www.linkedin.com/posts/neilmetzler_were-out-of-stealth-omnisent-sports-activity-7370844160737656833-Ktkh",
            "author": "Neil Metzler",
            "company": "Omnisent Sports",
            "description": "Sports tech startup providing real-time sentiment intelligence and sports analytics to help teams price sharper, engage fans deeper, and move faster.",
            "date": "2025-03-15",
            "category": "sports_tech"
        },
        # Add new startups here - entries older than 12 months will be filtered out
        # To add a new startup, copy this template:
        # {
        #     "title": "Company Name - Brief description",
        #     "url": "https://www.linkedin.com/posts/...",
        #     "author": "Person Name",
        #     "company": "Company Name",
        #     "description": "Detailed description (include 'sports tech' keywords)",
        #     "date": "YYYY-MM-DD",
        #     "category": "sports_tech"
        # },
    ]

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

    def get_known_startups(self, max_age_months: int = 12) -> List[Dict]:
        """
        Return list of known sports tech startups found on LinkedIn

        Args:
            max_age_months: Maximum age in months for startups (default: 12)

        Returns:
            List of recent startup announcements
        """
        recent_startups = []
        cutoff_date = datetime.now() - timedelta(days=max_age_months * 30)

        for startup in self.KNOWN_POSTS:
            date_str = startup.get('date', '')

            try:
                # Parse different date formats
                if len(date_str) == 4:  # Year only (e.g., "2025")
                    post_date = datetime(int(date_str), 1, 1)
                elif len(date_str) == 10:  # Full date (e.g., "2025-03-15")
                    post_date = datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    # If can't parse, skip this startup
                    print(f"  ⚠️  Skipping {startup['company']}: Invalid date format '{date_str}'")
                    continue

                # Only include if within the time window
                if post_date >= cutoff_date:
                    recent_startups.append(startup)
                else:
                    days_old = (datetime.now() - post_date).days
                    print(f"  ⏭️  Filtered out {startup['company']}: {days_old} days old (>{max_age_months} months)")

            except Exception as e:
                print(f"  ⚠️  Error parsing date for {startup['company']}: {e}")
                continue

        return recent_startups

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
