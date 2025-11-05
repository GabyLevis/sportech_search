#!/usr/bin/env python3
"""
AI-Powered Sports Tech Classifier
Uses LLM to determine if a company/article is sports tech related
"""

import os
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SportsTechClassifier:
    """
    Uses OpenAI GPT to classify whether a company or article is sports tech related
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the classifier

        Args:
            api_key: OpenAI API key (if not provided, loads from env)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = None
        self.available = False

        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.available = True
                print("✓ AI Classifier enabled (OpenAI GPT)")
            except Exception as e:
                print(f"⚠️  AI Classifier unavailable: {e}")
                self.available = False
        else:
            print("⚠️  AI Classifier disabled (No API key found)")
            print("    Set OPENAI_API_KEY environment variable to enable")

    def is_sports_tech(self, company_name: str, description: str, article_title: str = "") -> Dict:
        """
        Determine if a company is sports tech related using AI

        Args:
            company_name: Name of the company
            description: Description or context about the company
            article_title: Optional article title for additional context

        Returns:
            Dictionary with classification results:
            {
                'is_sports_tech': bool,
                'confidence': float (0-1),
                'category': str (e.g., 'athlete performance', 'fan engagement'),
                'reasoning': str
            }
        """
        if not self.available:
            # Fallback to keyword-based classification
            return self._fallback_classification(company_name, description, article_title)

        try:
            # Construct prompt for GPT
            prompt = f"""Analyze if this company is a sports technology (sports tech) startup.

Company Name: {company_name}
Description: {description}
{f"Article/Source: {article_title}" if article_title else ""}

Sports tech includes:
- Athlete performance tracking/analytics
- Sports data and analytics platforms
- Fan engagement technology
- Sports betting/gambling technology
- Fitness and wellness tech (if performance-focused)
- Sports team management software
- Sports streaming/media technology
- Wearables for sports/athletics
- eSports technology
- Sports venue/event technology

NOT sports tech:
- General fitness apps (unless athlete-focused)
- General media/content companies (unless sports-specific)
- Sports apparel without tech component
- General business software used by sports teams

Respond in JSON format:
{{
    "is_sports_tech": true/false,
    "confidence": 0.0-1.0,
    "category": "specific sports tech category or null",
    "reasoning": "brief explanation"
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cost-effective
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in sports technology startups. Analyze companies and determine if they are sports tech related. Be strict - only classify as sports tech if there's clear evidence."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,  # Low temperature for consistent classification
                max_tokens=200
            )

            # Parse response
            import json
            result = json.loads(response.choices[0].message.content)

            return {
                'is_sports_tech': result.get('is_sports_tech', False),
                'confidence': result.get('confidence', 0.0),
                'category': result.get('category'),
                'reasoning': result.get('reasoning', ''),
                'method': 'ai'
            }

        except Exception as e:
            print(f"  ⚠️  AI classification failed: {e}")
            return self._fallback_classification(company_name, description, article_title)

    def _fallback_classification(self, company_name: str, description: str, article_title: str = "") -> Dict:
        """
        Fallback keyword-based classification when AI is unavailable

        Args:
            company_name: Name of the company
            description: Description or context
            article_title: Optional article title

        Returns:
            Classification result dictionary
        """
        text = f"{company_name} {description} {article_title}".lower()

        # Sports tech keywords
        sports_tech_keywords = [
            'sports tech', 'sports technology', 'sporttech',
            'athlete performance', 'sports analytics', 'sports data',
            'fan engagement', 'sports betting', 'sports wearable',
            'fitness tracking', 'sports management', 'esports',
            'sports streaming', 'sports venue', 'training platform',
            'athletic performance', 'sports intelligence'
        ]

        # Anti-patterns (not sports tech)
        anti_patterns = [
            'general fitness', 'lifestyle', 'wellness app',
            'media company', 'publishing', 'apparel', 'clothing'
        ]

        # Count matches
        sports_matches = sum(1 for keyword in sports_tech_keywords if keyword in text)
        anti_matches = sum(1 for keyword in anti_patterns if keyword in text)

        is_sports_tech = sports_matches > 0 and sports_matches > anti_matches
        confidence = min(sports_matches * 0.3, 0.9) if is_sports_tech else 0.1

        # Try to determine category
        category = None
        if 'performance' in text or 'athlete' in text:
            category = 'athlete_performance'
        elif 'fan' in text or 'engagement' in text:
            category = 'fan_engagement'
        elif 'analytics' in text or 'data' in text:
            category = 'sports_analytics'
        elif 'betting' in text or 'gambling' in text:
            category = 'sports_betting'

        return {
            'is_sports_tech': is_sports_tech,
            'confidence': confidence,
            'category': category,
            'reasoning': f'Keyword-based: {sports_matches} sports tech keywords found',
            'method': 'keyword'
        }

    def classify_batch(self, items: list) -> list:
        """
        Classify multiple items at once

        Args:
            items: List of dictionaries with 'name', 'description', 'title' keys

        Returns:
            List of items with added 'classification' field
        """
        results = []

        for item in items:
            classification = self.is_sports_tech(
                company_name=item.get('name', ''),
                description=item.get('description', '') or item.get('context', ''),
                article_title=item.get('title', '') or item.get('source_title', '')
            )

            item['classification'] = classification
            results.append(item)

        return results


# Convenience function for quick classification
def classify_company(name: str, description: str, api_key: Optional[str] = None) -> Dict:
    """
    Quick function to classify a single company

    Args:
        name: Company name
        description: Company description
        api_key: Optional OpenAI API key

    Returns:
        Classification result
    """
    classifier = SportsTechClassifier(api_key=api_key)
    return classifier.is_sports_tech(name, description)


if __name__ == "__main__":
    # Test the classifier
    print("=" * 70)
    print("Sports Tech Classifier - Test Mode")
    print("=" * 70)
    print()

    classifier = SportsTechClassifier()

    # Test cases
    test_companies = [
        {
            "name": "Omnisent Sports",
            "description": "Real-time sentiment intelligence to help price sharper, engage deeper, and move faster in sports",
            "title": "Out of stealth announcement"
        },
        {
            "name": "Peloton",
            "description": "Interactive fitness platform with live and on-demand workout classes",
            "title": "Fitness technology company"
        },
        {
            "name": "Nike",
            "description": "Sports apparel and footwear company",
            "title": "Athletic clothing brand"
        },
        {
            "name": "Catapult Sports",
            "description": "Wearable technology and analytics for athlete performance tracking",
            "title": "Sports analytics platform"
        },
    ]

    print("Testing classification on sample companies:")
    print()

    for company in test_companies:
        result = classifier.is_sports_tech(
            company_name=company['name'],
            description=company['description'],
            article_title=company.get('title', '')
        )

        print(f"Company: {company['name']}")
        print(f"  Sports Tech: {'✓ YES' if result['is_sports_tech'] else '✗ NO'}")
        print(f"  Confidence: {result['confidence']:.0%}")
        if result['category']:
            print(f"  Category: {result['category']}")
        print(f"  Reasoning: {result['reasoning']}")
        print(f"  Method: {result['method']}")
        print()
