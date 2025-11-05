# Sports Tech Startup Scraper

A platform that searches sports industry magazines for articles about new sports tech startups and provides summaries.

## Features

- Scrapes sports industry publications (starting with Sports Business Journal)
- Identifies articles about sports tech startups
- Extracts startup information and generates summaries
- Extensible design to add more publication sources

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment (optional):
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Run the scraper:
```bash
python scraper.py
```

## Supported Publications

- Sports Business Journal (sportsbusinessjournal.com)

## Output

The scraper returns a list of startups with:
- Startup name
- Brief summary
- Source article URL
- Publication date (when available)
