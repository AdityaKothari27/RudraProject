# AI-Powered Personalized Newsletter Generator

A Python application that creates customized newsletters based on user preferences by fetching articles from various RSS feeds and using NLP to categorize and personalize content.

## Features

- Fetches articles from multiple RSS feeds across different categories
- Uses NLP to categorize and analyze article content
- Personalized content selection based on user preferences
- Generates formatted newsletters in Markdown
- Scheduled newsletter generation and delivery

## Project Structure

```
newsletter_generator/
├── data/                 # Stored user profiles and configurations
├── models/               # Data models for users and articles
├── templates/            # Newsletter templates
├── utils/                # Utility functions
├── __init__.py           # Package initialization
├── article_processor.py  # Article analysis and categorization
├── main.py               # Application entry point
├── newsletter_generator.py # Newsletter creation
├── rss_fetcher.py        # RSS feed parsing
└── user_manager.py       # User profile management
```

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd newsletter-generator
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Download required NLP models:
```
python -m spacy download en_core_web_md
python -m nltk.downloader punkt stopwords wordnet
```

## Usage

1. Configure user profiles in the data directory
2. Run the application:
```
python -m newsletter_generator.main
```

## User Personas

The system is pre-configured with the following user personas:

1. **Alex Parker** (Tech Enthusiast)
   - Interests: AI, cybersecurity, blockchain, startups, programming
   - Sources: TechCrunch, Wired Tech, Ars Technica, MIT Tech Review

2. **Priya Sharma** (Finance & Business Guru)
   - Interests: Global markets, startups, fintech, cryptocurrency, economics
   - Sources: Bloomberg, Financial Times, Forbes, CoinDesk

3. **Marco Rossi** (Sports Journalist)
   - Interests: Football, F1, NBA, Olympic sports, esports
   - Sources: ESPN, BBC Sport, Sky Sports F1, The Athletic

4. **Lisa Thompson** (Entertainment Buff)
   - Interests: Movies, celebrity news, TV shows, music, books
   - Sources: Variety, Rolling Stone, Billboard, Hollywood Reporter

5. **David Martinez** (Science & Space Nerd)
   - Interests: Space exploration, AI, biotech, physics, renewable energy
   - Sources: NASA, Science Daily, Nature, Ars Technica Science

## License

MIT
