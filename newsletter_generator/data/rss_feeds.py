"""
Configuration file with RSS feed URLs for different categories.
"""

RSS_FEEDS = {
    "general": [
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "http://feeds.bbci.co.uk/news/rss.xml",
        "http://www.reuters.com/rssFeed/topNews",
        "https://www.theguardian.com/world/rss"
    ],
    "technology": [
        "https://techcrunch.com/feed/",
        "https://www.wired.com/feed/rss",
        "https://feeds.feedburner.com/TechCrunch/",
        "https://www.technologyreview.com/topnews.rss",
        "https://feeds.arstechnica.com/arstechnica/technology-lab"
    ],
    "business": [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://www.cnbc.com/id/10001147/device/rss/rss.html",
        "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
        "https://www.ft.com/rss/companies",
        "https://www.forbes.com/business/feed/"
    ],
    "finance": [
        "https://www.forbes.com/money/feed/",
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "https://www.ft.com/rss/markets",
        "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml"
    ],
    "sports": [
        "https://www.espn.com/espn/rss/news",
        "https://feeds.feedburner.com/espnfc/global",
        "https://www.skysports.com/rss/0,25319,12040,00.xml",
        "https://www.bbc.co.uk/sport/rss/sport/football/rss.xml",
        "https://api.foxsports.com/v1/rss?partnerKey=zBaFxRyGKCfxBagJG9b8pqLyndmvo7UU"
    ],
    "entertainment": [
        "https://variety.com/feed/",
        "https://www.hollywoodreporter.com/feed/",
        "https://www.billboard.com/feed/",
        "https://www.rollingstone.com/feed/",
        "https://www.thewrap.com/feed/"
    ],
    "science": [
        "https://www.sciencedaily.com/rss/all.xml",
        "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "https://www.nature.com/nature.rss",
        "https://feeds.arstechnica.com/arstechnica/science",
        "https://www.sciencemag.org/rss/news_current.xml"
    ],
    "health": [
        "https://www.webmd.com/rss/all.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",
        "https://www.medicalnewstoday.com/newsfeeds/rss",
        "https://www.health.harvard.edu/feed/articles.xml",
        "https://www.sciencedaily.com/rss/health_medicine.xml"
    ],
    "politics": [
        "https://feeds.washingtonpost.com/rss/politics",
        "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
        "https://www.politico.com/rss/politicopicks.xml",
        "https://thehill.com/rss/news-by-subject/all-news.xml",
        "https://www.bbc.co.uk/news/politics/rss.xml"
    ],
    "world": [
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://feeds.washingtonpost.com/rss/world",
        "https://www.bbc.co.uk/news/world/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://www.theguardian.com/world/rss"
    ]
}

# Mapping of sources to user personas
PERSONA_SOURCES = {
    "tech_enthusiast": [
        "TechCrunch", "Wired", "Ars Technica", "MIT Technology Review"
    ],
    "finance_guru": [
        "Bloomberg", "Financial Times", "Forbes", "CNBC"
    ],
    "sports_journalist": [
        "ESPN", "BBC Sport", "Sky Sports", "Fox Sports"
    ],
    "entertainment_buff": [
        "Variety", "Rolling Stone", "Billboard", "Hollywood Reporter"
    ],
    "science_nerd": [
        "NASA", "Science Daily", "Nature", "Science Magazine"
    ]
} 