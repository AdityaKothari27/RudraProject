#!/usr/bin/env python3

"""
Example script to demonstrate the AI-Powered Personalized Newsletter Generator.
This script fetches a small sample of articles and generates a newsletter for one user.
"""

import logging
import sys
from datetime import datetime

from newsletter_generator.rss_fetcher import RSSFetcher
from newsletter_generator.article_processor import ArticleProcessor
from newsletter_generator.user_manager import UserManager
from newsletter_generator.newsletter_generator import NewsletterGenerator
from newsletter_generator.models.user import User
from newsletter_generator.models.article import Article

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run a simple example of the newsletter generator"""
    logger.info("Running newsletter generator example")
    
    # Sample RSS feeds (just a few for demonstration)
    sample_feeds = {
        "technology": [
            "https://techcrunch.com/feed/",
            "https://www.wired.com/feed/rss"
        ],
        "business": [
            "https://feeds.bloomberg.com/markets/news.rss"
        ],
        "science": [
            "https://www.sciencedaily.com/rss/all.xml"
        ]
    }
    
    # Create components
    user_manager = UserManager()
    rss_fetcher = RSSFetcher(sample_feeds, max_articles_per_feed=5)  # Limit to 5 articles per feed
    article_processor = ArticleProcessor()
    newsletter_generator = NewsletterGenerator()
    
    # Use an existing user or create a demo user
    users = user_manager.get_all_users()
    if users:
        user = users[0]  # Use the first user
        logger.info(f"Using existing user: {user.name}")
    else:
        # Create a demo user
        user = User(
            id="demo-user",
            name="Demo User",
            email="demo@example.com",
            interests=["technology", "AI", "machine learning", "startups"],
            preferred_sources=["TechCrunch", "Wired", "Bloomberg"],
            preferred_categories=["technology", "business"],
        )
        logger.info(f"Created demo user: {user.name}")
    
    # Fetch articles
    logger.info("Fetching articles from RSS feeds")
    articles = rss_fetcher.fetch_all_feeds()
    logger.info(f"Fetched {len(articles)} articles")
    
    if not articles:
        logger.error("No articles fetched, exiting")
        return
    
    # Process articles
    logger.info("Processing articles")
    processed_articles = article_processor.process_articles(articles)
    logger.info(f"Processed {len(processed_articles)} articles")
    
    # Calculate relevance scores for user
    user_articles = article_processor.calculate_relevance_for_user(processed_articles, user)
    
    # Generate newsletter
    logger.info(f"Generating newsletter for {user.name}")
    newsletter = newsletter_generator.generate_newsletter(user, user_articles, max_articles=10)
    
    logger.info(f"Newsletter generated and saved to the output directory")
    logger.info("Example completed successfully")
    
    # Print paths to the generated files
    print("\nNewsletter generated successfully!")
    print(f"Check the output directory for the generated newsletters.")
    
    # If running in interactive mode, offer to display the newsletter
    if sys.stdout.isatty():
        response = input("Would you like to see the newsletter content? (y/n): ")
        if response.lower() == 'y':
            print("\n" + "-" * 80)
            print(newsletter)
            print("-" * 80)


if __name__ == "__main__":
    main() 