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
from datetime import datetime
import json


class LinkedInStealthStartupFinder:
    """Find and track sports tech startups announced on LinkedIn"""

    # Curated LinkedIn posts found via search
    # These are real posts about sports tech startups coming out of stealth
    KNOWN_POSTS = [
        {
            "title": "Sports Visio, Inc. - Coming out of stealth",
            "url": "https://www.linkedin.com/posts/jsyversen_sports-visio-inc-linkedin-activity-6876618219461873664-XAFb",
            "author": "Jason Syversen",
            "company": "Sports Visio, Inc.",
            "description": "Sports tech startup coming out of stealth after 9-10 months, transitioning from development to private testing. Starting pre-seed discussions.",
            "date": "2021-12-14",
            "category": "sports_tech"
        },
        {
            "title": "Omnisent Sports - Out of stealth",
            "url": "https://www.linkedin.com/posts/neilmetzler_were-out-of-stealth-omnisent-sports-activity-7370844160737656833-Ktkh",
            "author": "Neil Metzler",
            "company": "Omnisent Sports",
            "description": "Real-time sports delivery platform coming out of stealth mode.",
            "date": "2025",
            "category": "sports_tech"
        },
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

    def get_known_startups(self) -> List[Dict]:
        """Return list of known sports tech startups found on LinkedIn"""
        return self.KNOWN_POSTS.copy()

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


def main():
    """Main execution function"""
    print()
    print("=" * 70)
    print("LinkedIn Sports Tech Startup Finder")
    print("Finding startups coming out of stealth mode")
    print("=" * 70)
    print()

    finder = LinkedInStealthStartupFinder()

    # Show known startups
    known_startups = finder.get_known_startups()

    print(f"FOUND: {len(known_startups)} Sports Tech Startups Coming Out of Stealth")
    print("=" * 70)
    print()

    for i, startup in enumerate(known_startups, 1):
        print(f"{i}. {startup['company']}")
        print("-" * 70)
        print(finder.format_startup_info(startup))
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
        "startups": known_startups,
        "search_date": datetime.now().isoformat(),
        "note": "Visit URLs in a browser with LinkedIn login for full details"
    }

    output_file = "linkedin_sports_tech_startups.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print("=" * 70)
    print(f"Results saved to: {output_file}")
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
